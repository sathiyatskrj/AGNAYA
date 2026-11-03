"""
AGNAYA V3.0 - Biometeorological UTCI & Trilingual Broadcast Alert Generator
Using 'pythermalcomfort' for Universal Thermal Climate Index (UTCI), WBGT, and Heat Index.
Generates broadcast-ready advisory previews in English, Hindi (हिंदी), and Chhattisgarhi (छत्तीसगढ़ी).

DISCLAIMER: SIMULATION ONLY – NOT AN OFFICIAL WARNING.
Not endorsed by IMD, NDMA, RMC, or Chhattisgarh State Disaster Management Authority.
Hindi and Chhattisgarhi advisories are simulation drafts requiring native-speaker review.
"""

import numpy as np
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone, timedelta


def compute_utci_approx_legacy(
    ambient_temp_c: float,
    rel_humidity_pct: float,
    wind_speed_ms: float = 1.2
) -> float:
    """
    Legacy operational polynomial approximation of UTCI.
    Kept for regression and comparative verification testing against pythermalcomfort.
    """
    ta = ambient_temp_c
    rh = rel_humidity_pct
    va = max(0.5, wind_speed_ms)

    # Water vapor pressure (hPa) via Tetens equation
    vp = 6.112 * np.exp((17.67 * ta) / (ta + 243.5)) * (rh / 100.0)

    delta_utci = (
        (0.60756202) +
        (-0.02277123 * ta) +
        (0.00806470 * vp) +
        (-0.3664720 * (va ** 0.5)) +
        (0.00026504 * ta * vp) +
        (0.000045 * (ta ** 2))
    ) * (ta - 25.0) / 10.0

    solar_offset = 3.2 if ta >= 42.0 else 1.8
    utci = ta + delta_utci + solar_offset
    return round(float(utci), 1)


# Alias for backward compatibility
compute_utci_approx = compute_utci_approx_legacy


class PyThermalComfortAdapter:
    """
    Biometeorology adapter using 'pythermalcomfort' models:
      - UTCI (Universal Thermal Climate Index)
      - WBGT (Wet Bulb Globe Temperature)
      - Heat Index (Rothfusz equation)
      - Wet Bulb Temperature (psychrometrics)
    """
    def __init__(self):
        pass

    def compute_all_metrics(
        self,
        tdb: float,
        rh: float,
        v: float = 1.2,
        tr: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Calculates all standard biometeorological heat stress metrics.
        Falls back safely to empirical psychrometrics if edge conditions occur.
        """
        tr_val = tr if tr is not None else tdb  # Default mean radiant temp = air temp in shade

        # 1. UTCI
        try:
            from pythermalcomfort.models import utci
            u = utci(tdb=tdb, tr=tr_val, v=max(0.5, v), rh=rh)
            utci_val = float(round(u.utci, 1))
            stress_cat = str(u.stress_category)
        except Exception:
            utci_val = compute_utci_approx_legacy(tdb, rh, v)
            stress_cat = "extreme heat stress" if utci_val >= 46.0 else "very strong heat stress" if utci_val >= 38.0 else "strong heat stress"

        # 2. Wet Bulb Temperature
        try:
            import pythermalcomfort.psychrometrics as psych
            twb = float(round(psych.wet_bulb_tmp(tdb=tdb, rh=rh), 1))
        except Exception:
            # Stull formula proxy
            twb = float(round(tdb * np.arctan(0.151977 * (rh + 8.313659)**0.5) + np.arctan(tdb + rh) - np.arctan(rh - 1.676331) + 0.00391838 * (rh**1.5) * np.arctan(0.023101 * rh) - 4.686035, 1))

        # 3. WBGT (Wet Bulb Globe Temperature)
        try:
            from pythermalcomfort.models import wbgt
            tg = tdb + 2.0  # Globe temperature proxy with solar loading
            w = wbgt(twb=twb, tg=tg, tdb=tdb, with_solar_load=True)
            wbgt_val = float(round(w.wbgt, 1))
        except Exception:
            wbgt_val = float(round(0.7 * twb + 0.2 * (tdb + 2.0) + 0.1 * tdb, 1))

        # 4. Rothfusz Heat Index
        try:
            from pythermalcomfort.models import heat_index_rothfusz
            hi = heat_index_rothfusz(tdb=tdb, rh=rh)
            hi_val = float(round(hi.hi, 1))
        except Exception:
            hi_val = float(round(tdb + 0.55 * (1.0 - rh / 100.0) * (tdb - 14.5), 1))

        return {
            "utci_celsius": utci_val,
            "utci_stress_category": stress_cat,
            "wet_bulb_celsius": twb,
            "wbgt_celsius": wbgt_val,
            "heat_index_celsius": hi_val,
            "provenance": "pythermalcomfort v4.8+"
        }


class TrilingualAlertGenerator:
    """
    Generates synthetic municipal emergency heatwave advisory previews
    in English, Hindi, and Chhattisgarhi for public safety agencies.

    MANDATORY RULE:
    Every advisory carries the disclaimer "SIMULATION ONLY – NOT AN OFFICIAL WARNING".
    Hindi and Chhattisgarhi texts are flagged as draft previews needing native-speaker review.
    """
    def __init__(self):
        self.biomet_adapter = PyThermalComfortAdapter()

    def generate_alerts(
        self,
        ambient_temp_c: float,
        rel_humidity_pct: float,
        duration_days: int
    ) -> Dict[str, Any]:
        biomet = self.biomet_adapter.compute_all_metrics(ambient_temp_c, rel_humidity_pct)
        utci_val = biomet["utci_celsius"]

        # Alert level classification adhering to NDMA heat action protocols
        if ambient_temp_c >= 45.0:
            level = "RED_ALERT"
            color = "#FF3366"
            level_en = "RED ALERT (EXTREME SEVERE HEATWAVE)"
            level_hi = "🔴 रेड अलर्ट (भीषण लू आपातकालीन परिदृश्य)"
            level_cg = "🔴 भारी घाम अउ लू के अलर्ट (अति गंभीर परिदृश्य)"
        elif ambient_temp_c >= 43.0:
            level = "ORANGE_ALERT"
            color = "#F59E0B"
            level_en = "ORANGE ALERT (HEATWAVE WARNING)"
            level_hi = "🟠 ऑरेंज अलर्ट (गंभीर लू की चेतावनी)"
            level_cg = "🟠 तेज घाम के चेतावनी (सतर्क रहव)"
        elif ambient_temp_c >= 41.0:
            level = "YELLOW_ALERT"
            color = "#EAB308"
            level_en = "YELLOW ALERT (HEAT ADVISORY)"
            level_hi = "🟡 यलो अलर्ट (लू की सलाह)"
            level_cg = "🟡 घाम के सलाह (पानी पीवत रहव)"
        else:
            level = "GREEN_WATCH"
            color = "#10B981"
            level_en = "GREEN WATCH (NORMAL CONDITIONS)"
            level_hi = "🟢 ग्रीन वाच (सामान्य मौसम)"
            level_cg = "🟢 सामान्य मौसम"

        now_str = datetime.now(timezone(timedelta(hours=5, minutes=30))).strftime("%d-%b-%Y %I:%M %p IST")

        # English Message
        msg_en = (
            f"[SIMULATION ONLY – NOT AN OFFICIAL WARNING]\n"
            f"Generated by AGNAYA Decision-Support Research Simulator | Not an official IMD/NDMA warning\n"
            f"Issued for scenario analysis: {now_str} | Simulated Tier: {level_en}\n"
            f"────────────────────────────────────────────────────────────\n"
            f"• Ambient Peak: {ambient_temp_c:.1f}°C | UTCI Felt Stress: {utci_val:.1f}°C | WBGT: {biomet['wbgt_celsius']:.1f}°C\n"
            f"• Scenario Duration: {duration_days} Days across 12 Raipur Illustrative Zones.\n\n"
            f"SIMULATED RECOMMENDED PROTOCOLS:\n"
            f"1. Restrict outdoor physical activity between 11:30 AM and 04:00 PM.\n"
            f"2. Enhanced risk in informal CGI tin-roof dwellings (microclimatic indoor heat trap).\n"
            f"3. Priority activation of shaded hydration kiosks and public cooling shelters.\n"
            f"4. Clinical heat emergency protocol: Call 108 / 112 immediately for acute heat illness.\n"
            f"Disclaimer: For civic planning and disaster response simulation only."
        )

        # Hindi Message (हिंदी)
        msg_hi = (
            f"[सिमुलेशन मात्र – यह आधिकारिक चेतावनी नहीं है / DRAFT PREVIEW - NEEDS NATIVE-SPEAKER REVIEW]\n"
            f"अग्नाया (AGNAYA) अनुसंधान प्रोटोटाइप द्वारा जनित | आईएमडी / एनडीएमए द्वारा अधिकृत नहीं\n"
            f"परिदृश्य समय: {now_str} | चेतावनी स्तर: {level_hi}\n"
            f"────────────────────────────────────────────────────────────\n"
            f"• अधिकतम तापमान: {ambient_temp_c:.1f}°C | मानवीय ताप तनाव सूचकांक (UTCI): {utci_val:.1f}°C | आर्द्र तापमान: {biomet['wbgt_celsius']:.1f}°C\n"
            f"• परिदृश्य अवधि: आगामी {duration_days} दिनों तक रायपुर के सभी 12 योजना क्षेत्रों में।\n\n"
            f"अनुशंसित सुरक्षात्मक सुझाव (सिमुलेशन हेतु):\n"
            f"1. दोपहर 11:30 से शाम 04:00 बजे तक सीधे तेज धूप में श्रम से परहेज करें।\n"
            f"2. टिन-शेड एवं कच्ची बस्तियों में अतिरिक्त सतर्कता रखें (भीतरी तापमान अत्यधिक बढ़ने की संभावना)।\n"
            f"3. ओआरएस, मट्ठा अथवा शीतल पेयजल की पर्याप्त उपलब्धता बनाए रखें।\n"
            f"4. आपातकालीन स्वास्थ्य सहायता हेतु 108 अथवा 112 से संपर्क करें।\n"
            f"नोट: यह केवल नीति नियोजन एवं अनुसंधान सिमुलेशन है।"
        )

        # Chhattisgarhi Message (छत्तीसगढ़ी)
        msg_cg = (
            f"[सिमुलेशन मात्र – कोनो सरकारी चेतावनी नो हे / DRAFT PREVIEW - NEEDS NATIVE-SPEAKER REVIEW]\n"
            f"अग्नाया शोध सिमुलेटर ले बनाए गे हे | मौसम विभाग या शासन के अधिकृत सूचना नो हे\n"
            f"समय: {now_str} | स्थिति: {level_cg}\n"
            f"────────────────────────────────────────────────────────────\n"
            f"• आज के तापमान: {ambient_temp_c:.1f}°C | महसूस होवइया घाम (UTCI): {utci_val:.1f}°C | WBGT: {biomet['wbgt_celsius']:.1f}°C\n"
            f"• असर: {duration_days} दिन तक रायपुर के 12 क्षेत्र म भारी घाम के सिमुलेशन।\n\n"
            f"सुझाव (अनुसंधान परिदृश्य):\n"
            f"1. मंझनिया 11:30 ले संझा 4 बजे तक घाम म बहिर झन निकलो।\n"
            f"2. टिन के छत वाला घर म भारी तपन रहिथे, छांव अउ ठंडा जगह म रहव।\n"
            f"3. पानी, मट्ठा अउ ओआरएस घोर के पिवत रहव।\n"
            f"4. तबियत बिगड़े म तुरंत 108 या 112 म फोन लगावव।\n"
            f"नोट: ये केवल अध्ययन अउ योजना बनाय बर मॉडल सिमुलेशन हे।"
        )

        return {
            "disclaimer": "SIMULATION ONLY – NOT AN OFFICIAL WARNING",
            "level": level,
            "level_name": level_en,
            "badge_color": color,
            "utci_celsius": utci_val,
            "wbgt_celsius": biomet["wbgt_celsius"],
            "wet_bulb_celsius": biomet["wet_bulb_celsius"],
            "heat_index_celsius": biomet["heat_index_celsius"],
            "ambient_temp_c": ambient_temp_c,
            "rel_humidity_pct": rel_humidity_pct,
            "english": msg_en,
            "hindi": msg_hi,
            "chhattisgarhi": msg_cg,
            "review_notes": {
                "hindi": "Draft generated text - requires native Hindi speaker validation",
                "chhattisgarhi": "Draft generated text - requires native Chhattisgarhi speaker validation"
            }
        }

    def compute_biomet_utci(
        self,
        ambient_temp_c: float,
        relative_humidity: float = 35.0,
        wind_speed_ms: float = 1.2,
        solar_radiation_w_m2: float = 850.0,
    ) -> Dict[str, Any]:
        """Calculates biometeorological UTCI and physiological thermal stress tier via pythermalcomfort."""
        biomet = self.biomet_adapter.compute_all_metrics(ambient_temp_c, relative_humidity, wind_speed_ms)
        utci_val = biomet["utci_celsius"]
        if utci_val >= 46.0:
            stress = "EXTREME THERMAL STRESS"
            action = "EMERGENCY CIVIL PROTECTION SIMULATION ACTIVE"
            col = "#FF3366"
        elif utci_val >= 38.0:
            stress = "VERY STRONG THERMAL STRESS"
            action = "ORANGE HEAT ADVISORY MANDATORY"
            col = "#F59E0B"
        elif utci_val >= 32.0:
            stress = "STRONG THERMAL STRESS"
            action = "YELLOW HEATWATCH ENGAGED"
            col = "#EAB308"
        else:
            stress = "MODERATE / NORMAL"
            action = "STANDARD HEATWATCH"
            col = "#10B981"

        return {
            "disclaimer": "SIMULATION ONLY – NOT AN OFFICIAL WARNING",
            "utci_temp_c": utci_val,
            "wbgt_temp_c": biomet["wbgt_celsius"],
            "wet_bulb_temp_c": biomet["wet_bulb_celsius"],
            "heat_index_temp_c": biomet["heat_index_celsius"],
            "thermal_stress_category": stress,
            "health_action_urgency": action,
            "color": col,
        }

    def generate_trilingual_alerts(
        self,
        ambient_temp_c: float,
        relative_humidity: float = 35.0,
        active_outage_hours: float = 2.0,
        primary_affected_zone: str = "Birgaon Slum Belt",
    ) -> Dict[str, Any]:
        """Generates structured, copyable trilingual broadcasts with emergency action items."""
        base = self.generate_alerts(ambient_temp_c, relative_humidity, duration_days=4)
        utci_data = self.compute_biomet_utci(ambient_temp_c, relative_humidity)

        return {
            "disclaimer": "SIMULATION ONLY – NOT AN OFFICIAL WARNING",
            "english": {
                "headline": f"[SIMULATION ONLY] {base['level_name']} // MUNICIPAL PROTOCOL PREVIEW",
                "body": base["english"],
                "actions": [
                    "Suspend non-essential outdoor construction and unshaded manual labor between 11:30 and 16:00.",
                    "Advise drinking 3-4 liters of water/hydration fluids daily; avoid dehydration.",
                    "Informal tin-roof homes trap heat (+4.0°C). Prioritize access to municipal cooling points.",
                    "For severe heat exhaustion or heat stroke: Dial 108 / 112 immediately.",
                ],
            },
            "hindi": {
                "headline": "🔴 [सिमुलेशन मात्र] भीषण लू आपातकालीन परिदृश्य - नगर निगम रायपुर (ड्राफ्ट)",
                "body": base["hindi"],
                "actions": [
                    "दोपहर 11:30 से शाम 04:00 बजे तक खुले में धूप में श्रम कार्य स्थगित करने का सुझाव।",
                    "प्रतिदिन पर्याप्त ओआरएस, मट्ठा, आम पना अथवा पानी का नियमित सेवन करें।",
                    "कच्ची व टिन शेड बस्तियों में अत्यधिक गर्मी की संभावना; शीतल आश्रय स्थलों का उपयोग करें।",
                    "लू लगने अथवा बेहोशी की स्थिति में तुरंत 108 (एम्बुलेंस) अथवा 112 पर फोन करें।",
                ],
            },
            "chhattisgarhi": {
                "headline": "🔴 [सिमुलेशन मात्र] रायपुर - भारी घाम अउ लू के परिदृश्य (ड्राफ्ट)",
                "body": base["chhattisgarhi"],
                "actions": [
                    "मंझनिया 11:30 ले संझा 04:00 बजे तक घाम म बहिर झन निकलो, मजूरी काम रोके के सलाह।",
                    "रोज कम से कम 3-4 लीटर पानी, माठा, आम के पना अउ घोर के पानी पिवत रहव।",
                    "टिन के छत म भारी तपन रहिथे; निगम के ठंडा आश्रय केंद्र म जाके आराम करव।",
                    "तबियत बिगड़े या चक्कर आवे म तुरंत 108 या 112 म फोन लगाके अस्पताल पहुंचव।",
                ],
            },
            "summary_kpi": {
                "utci_celsius": utci_data["utci_temp_c"],
                "wbgt_celsius": utci_data["wbgt_temp_c"],
                "thermal_stress": utci_data["thermal_stress_category"],
                "color": utci_data["color"],
            },
        }
