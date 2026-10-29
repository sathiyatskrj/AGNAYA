"""
AGNAYA V3.0 - Biometeorological UTCI & Trilingual Broadcast Alert Generator
Synthesizing research from TAPAS (SIH 2026 Winner)
Produces Universal Thermal Climate Index (UTCI) and broadcast-ready alerts
in English, Hindi (हिंदी), and Chhattisgarhi (छत्तीसगढ़ी)
"""

import numpy as np
from typing import Dict, List, Any
from datetime import datetime, timezone, timedelta


def compute_utci_approx(ambient_temp_c: float, rel_humidity_pct: float, wind_speed_ms: float = 1.2) -> float:
    """
    Computes an operational polynomial approximation of the Universal Thermal Climate Index (UTCI)
    for central Indian summer conditions.
    """
    ta = ambient_temp_c
    rh = rel_humidity_pct
    va = max(0.5, wind_speed_ms)

    # Water vapor pressure (hPa) via Tetens equation
    vp = 6.112 * np.exp((17.67 * ta) / (ta + 243.5)) * (rh / 100.0)

    # UTCI baseline difference relative to ambient temperature
    delta_utci = (
        (0.60756202) +
        (-0.02277123 * ta) +
        (0.00806470 * vp) +
        (-0.3664720 * (va ** 0.5)) +
        (0.00026504 * ta * vp) +
        (0.000045 * (ta ** 2))
    ) * (ta - 25.0) / 10.0

    # Solar radiation increment under direct afternoon sun (~+2.5 to +4.0°C)
    solar_offset = 3.2 if ta >= 42.0 else 1.8
    utci = ta + delta_utci + solar_offset
    return round(float(utci), 1)


class TrilingualAlertGenerator:
    """
    Generates official municipal emergency heatwave broadcast messages
    in English, Hindi, and Chhattisgarhi for public safety agencies.
    """
    def __init__(self):
        pass

    def generate_alerts(self, ambient_temp_c: float, rel_humidity_pct: float, duration_days: int) -> Dict[str, Any]:
        utci_val = compute_utci_approx(ambient_temp_c, rel_humidity_pct)
        
        if ambient_temp_c >= 45.0:
            level = "RED_ALERT"
            color = "#FF3366"
            level_en = "RED ALERT (EXTREME SEVERE HEATWAVE)"
            level_hi = "🔴 रेड अलर्ट (भीषण लू एवं आपातकाल)"
            level_cg = "🔴 भारी घाम अउ लू के अलर्ट (अति गंभीर)"
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
            level_hi = "🟢 ग्रीन वाच (सामान्य तापमान)"
            level_cg = "🟢 सामान्य मौसम"

        now_str = datetime.now(timezone(timedelta(hours=5, minutes=30))).strftime("%d-%b-%Y %I:%M %p IST")

        # English Message
        msg_en = (
            f"🚨 RAIPUR MUNICIPAL CORPORATION // HEATWAVE EMERGENCY DIRECTIVE\n"
            f"Issued: {now_str} | Status: {level_en}\n"
            f"────────────────────────────────────────────────────────────\n"
            f"• Ambient Peak: {ambient_temp_c:.1f}°C | Felt Stress (UTCI): {utci_val:.1f}°C\n"
            f"• Forecast Duration: Next {duration_days} Days across all 12 Municipal Wards.\n\n"
            f"CRITICAL DIRECTIVES:\n"
            f"1. AVOID outdoor exposure between 11:30 AM and 04:00 PM.\n"
            f"2. High risk in tin-roof & informal homes (+5°C indoor heat trap).\n"
            f"3. 12 Municipal Air-Cooled Refuge Shelters are open 24/7 with ORS & cold water.\n"
            f"4. For fainting, severe dizziness, or high fever: Dial 108 / 112 immediately.\n"
            f"Helpline: 1800-RAIPUR-HEAT | Raipur District Disaster Management"
        )

        # Hindi Message (हिंदी)
        msg_hi = (
            f"🚨 रायपुर नगर पालिक निगम // आपातकालीन लू चेतावनी निर्देश\n"
            f"जारी समय: {now_str} | चेतावनी स्तर: {level_hi}\n"
            f"────────────────────────────────────────────────────────────\n"
            f"• अधिकतम तापमान: {ambient_temp_c:.1f}°C | मानवीय ताप तनाव सूचकांक (UTCI): {utci_val:.1f}°C\n"
            f"• प्रभाव अवधि: आगामी {duration_days} दिनों तक रायपुर के सभी 12 वार्डों में।\n\n"
            f"नागरिकों हेतु आवश्यक दिशा-निर्देश:\n"
            f"1. दोपहर 11:30 से शाम 04:00 बजे तक धूप में सीधे बाहर निकलने से बचें।\n"
            f"2. टिन-शेड एवं कच्ची बस्तियों में अत्यधिक सावधानी बरतें (कमरे का तापमान 50°C तक संभव)।\n"
            f"3. नगर निगम द्वारा 12 शीतल आश्रय केंद्र 24 घंटे ओआरएस एवं ठंडे पानी सहित प्रारंभ हैं।\n"
            f"4. लू लगने, बेहोशी या सिरदर्द होने पर तुरंत 108 अथवा 112 पर कॉल करें।\n"
            f"हेल्पलाइन: 1800-RAIPUR-HEAT | जिला आपदा प्रबंधन प्राधिकरण, रायपुर"
        )

        # Chhattisgarhi Message (छत्तीसगढ़ी)
        msg_cg = (
            f"🚨 रायपुर नगर निगम // भारी घाम अउ लू के आपात सूचना\n"
            f"समय: {now_str} | स्थिति: {level_cg}\n"
            f"────────────────────────────────────────────────────────────\n"
            f"• आज के तापमान: {ambient_temp_c:.1f}°C | महसूस होवइया घाम (UTCI): {utci_val:.1f}°C\n"
            f"• लू के असर: आगू {duration_days} दिन ले सबो 12 वार्ड म भारी घाम रही।\n\n"
            f"सबो संगी मन बर जरूरी गोठ:\n"
            f"1. मंझनिया 11:30 ले संझा 4 बजे तक घाम म बहिर झन निकलो।\n"
            f"2. टिन के छत वाला घर म भारी तपन रहिथे, छांव अउ ठंडा जगह म रहव।\n"
            f"3. निगम के 12 ठन ठंडा आश्रय केंद्र खुला हे, जिहां पानी अउ ओआरएस (ORS) मिलत हे।\n"
            f"4. तबियत बिगड़े या चक्कर आवे म तुरंत 108 या 112 म फोन लगावव।\n"
            f"सहायता नंबर: 1800-RAIPUR-HEAT | रायपुर आपदा प्रबंधन"
        )

        return {
            "level": level,
            "level_name": level_en,
            "badge_color": color,
            "utci_celsius": utci_val,
            "ambient_temp_c": ambient_temp_c,
            "rel_humidity_pct": rel_humidity_pct,
            "english": msg_en,
            "hindi": msg_hi,
            "chhattisgarhi": msg_cg,
        }

    def compute_biomet_utci(
        self,
        ambient_temp_c: float,
        relative_humidity: float = 35.0,
        wind_speed_ms: float = 1.2,
        solar_radiation_w_m2: float = 850.0,
    ) -> Dict[str, Any]:
        """Calculates biometeorological UTCI and physiological thermal stress tier."""
        utci_val = compute_utci_approx(ambient_temp_c, relative_humidity, wind_speed_ms)
        if utci_val >= 46.0:
            stress = "EXTREME THERMAL STRESS"
            action = "EMERGENCY CIVIL PROTECTION DIRECTIVE ACTIVE"
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
            "utci_temp_c": utci_val,
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
            "english": {
                "headline": f"{base['level_name']} // MUNICIPAL EMERGENCY DIRECTIVE",
                "body": base["english"],
                "actions": [
                    "Suspend all outdoor construction and unshaded manual labor between 11:30 and 16:00.",
                    "Drink at least 3-4 liters of water/electrolyte fluids daily; avoid caffeine and direct sun.",
                    f"Informal/tin-roof homes trap heat (+5.5°C). Access any of the 12 municipal air-cooled shelters.",
                    "Call 108 / 112 immediately for heat stroke, fainting, or severe dehydration.",
                ],
            },
            "hindi": {
                "headline": "🔴 भीषण लू आपातकालीन चेतावनी (रेड अलर्ट) - नगर निगम रायपुर",
                "body": base["hindi"],
                "actions": [
                    "दोपहर 11:30 से शाम 04:00 बजे तक खुले में धूप में श्रम कार्य पूरी तरह बंद रखें।",
                    "प्रतिदिन कम से कम 3-4 लीटर ओआरएस, मट्ठा, आम पना अथवा पानी का नियमित सेवन करें।",
                    "कच्ची व टिन शेड बस्तियों में अत्यधिक गर्मी है; 12 शासकीय शीतल आश्रय स्थलों का उपयोग करें।",
                    "लू लगने या बेहोशी की स्थिति में तुरंत 108 (एम्बुलेंस) अथवा 112 पर फोन करें।",
                ],
            },
            "chhattisgarhi": {
                "headline": "🔴 रायपुर नगर निगम - भारी घाम अउ लू के अति गंभीर चेताउनी",
                "body": base["chhattisgarhi"],
                "actions": [
                    "मंझनिया 11:30 ले संझा 04:00 बजे तक घाम म बहिर झन निकलो, मजूरी काम बंद राखव।",
                    "रोज कम से कम 3-4 लीटर पानी, माठा, आम के पना अउ घोर के पानी पिवत रहव।",
                    "टिन के छत म भारी तपन रहिथे; निगम के 12 ठन ठंडा आश्रय केंद्र म जाके आराम करव।",
                    "तबियत बिगड़े या चक्कर आवे म तुरंत 108 या 112 म फोन लगाके अस्पताल पहुंचव।",
                ],
            },
            "summary_kpi": {
                "utci_celsius": utci_data["utci_temp_c"],
                "thermal_stress": utci_data["thermal_stress_category"],
                "color": utci_data["color"],
            },
        }

