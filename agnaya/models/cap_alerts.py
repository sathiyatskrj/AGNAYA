"""
AGNAYA - Common Alerting Protocol (CAP v1.2) Standard XML Generator
Implements OASIS Standard CAP-V1.2 compliant emergency alert formatting.

MANDATORY REGULATORY COMPLIANCE:
- Labelled strictly: "SIMULATION ONLY – NOT AN OFFICIAL WARNING".
- Status is set to "Draft" / "Exercise" / "Test" — never "Actual".
- Vernacular translations in Hindi and Chhattisgarhi flagged "needs_native_speaker_review".
- Absolutely no automatic delivery (no SMS, WhatsApp, or TTS broadcasts).
- Purely for file download and system interoperability previews.
"""

from datetime import datetime, timezone
import xml.etree.ElementTree as ET
from xml.dom import minidom
from typing import Any, Dict, List, Optional


class CAPAlertGenerator:
    """
    Constructs standardized OASIS CAP v1.2 XML document structures
    for heatwave infrastructure cascading stress scenarios.
    """

    CAP_NAMESPACE = "urn:oasis:names:tc:emergency:cap:1.2"

    def __init__(self, sender_id: str = "agnaya-simulator@research.raipur.local"):
        self.sender_id = sender_id

    def generate_cap_alert(
        self,
        ambient_temp_c: float,
        relative_humidity_pct: float,
        peak_demand_mw: float,
        shortfall_mw: float,
        critical_zones: List[Dict[str, Any]],
        tripped_substation: Optional[str] = None,
        identifier: Optional[str] = None,
    ) -> str:
        """
        Builds the CAP v1.2 XML document string with English, Hindi, and Chhattisgarhi blocks.
        """
        now_dt = datetime.now(timezone.utc)
        now_iso = now_dt.strftime("%Y-%m-%dT%H:%M:%S-00:00")
        alert_id = identifier or f"AGNAYA-SIM-{now_dt.strftime('%Y%m%d%H%M%S')}-RAIPUR"

        # Severity determination
        if ambient_temp_c >= 46.5 or shortfall_mw >= 50.0:
            severity = "Extreme"
            urgency = "Immediate"
        elif ambient_temp_c >= 44.5 or shortfall_mw > 0.0:
            severity = "Severe"
            urgency = "Expected"
        else:
            severity = "Moderate"
            urgency = "Future"

        root = ET.Element("alert", xmlns=self.CAP_NAMESPACE)

        ET.SubElement(root, "identifier").text = alert_id
        ET.SubElement(root, "sender").text = self.sender_id
        ET.SubElement(root, "sent").text = now_iso
        ET.SubElement(root, "status").text = "Draft"
        ET.SubElement(root, "msgType").text = "Alert"
        ET.SubElement(root, "source").text = "AGNAYA Multi-Model Infrastructure Simulator"
        ET.SubElement(root, "scope").text = "Public"
        ET.SubElement(root, "restriction").text = "Simulation and Disaster Planning Exercise Only"
        ET.SubElement(root, "note").text = (
            "SIMULATION ONLY – NOT AN OFFICIAL WARNING. This alert is a synthetic research model output "
            "and does not constitute an official warning or directive from IMD, NDMA, RMC, or CSPDCL."
        )

        top_zone_names = ", ".join([z.get("name", z.get("id", "Zone")) for z in critical_zones[:3]]) or "Urban Raipur"

        # ── 1. English <info> Block
        info_en = ET.SubElement(root, "info")
        ET.SubElement(info_en, "language").text = "en-US"
        ET.SubElement(info_en, "category").text = "Met"
        ET.SubElement(info_en, "category").text = "Infra"
        ET.SubElement(info_en, "event").text = "Urban Heatwave Cascading Infrastructure Stress"
        ET.SubElement(info_en, "urgency").text = urgency
        ET.SubElement(info_en, "severity").text = severity
        ET.SubElement(info_en, "certainty").text = "Observed"
        ET.SubElement(info_en, "headline").text = (
            f"[SIMULATION ONLY – NOT AN OFFICIAL WARNING] Extreme Heat Stress Alert for Raipur ({ambient_temp_c:.1f}°C)"
        )
        ET.SubElement(info_en, "description").text = (
            f"Simulated peak daytime temperature of {ambient_temp_c:.1f}°C with {relative_humidity_pct:.0f}% relative humidity. "
            f"Modeled electrical demand reaches {peak_demand_mw:.1f} MW, creating a shortfall of {shortfall_mw:.1f} MW above "
            f"CSPDCL's contracted summer peak limit (420 MW). High thermal entrapment modeled in informal settlements "
            f"across {top_zone_names}. Contingency status: {tripped_substation or 'None'}."
        )
        ET.SubElement(info_en, "instruction").text = (
            "Municipal Action Protocol (Simulation): Prioritize mobile water tankers and open shaded cooling centres. "
            "Ensure emergency standby generators at Kharun River WTP and tertiary healthcare centres."
        )

        # Quantitative Parameters
        def add_param(info_block, name, val):
            p = ET.SubElement(info_block, "parameter")
            ET.SubElement(p, "valueName").text = name
            ET.SubElement(p, "value").text = str(val)

        add_param(info_en, "ambient_temperature_celsius", f"{ambient_temp_c:.1f}")
        add_param(info_en, "peak_demand_mw", f"{peak_demand_mw:.1f}")
        add_param(info_en, "grid_shortfall_mw", f"{shortfall_mw:.1f}")
        add_param(info_en, "simulation_watermark", "SIMULATION ONLY – NOT AN OFFICIAL WARNING")

        area_en = ET.SubElement(info_en, "area")
        ET.SubElement(area_en, "areaDesc").text = "Raipur Municipal Corporation Urban Agglomeration"
        ET.SubElement(area_en, "circle").text = "21.2514,81.6296,15.0"

        # ── 2. Hindi <info> Block (Flagged for Native Speaker Review)
        info_hi = ET.SubElement(root, "info")
        ET.SubElement(info_hi, "language").text = "hi-IN"
        ET.SubElement(info_hi, "category").text = "Met"
        ET.SubElement(info_hi, "event").text = "भीषण लू एवं बुनियादी ढांचा तनाव (सिमुलेशन)"
        ET.SubElement(info_hi, "urgency").text = urgency
        ET.SubElement(info_hi, "severity").text = severity
        ET.SubElement(info_hi, "certainty").text = "Observed"
        ET.SubElement(info_hi, "headline").text = (
            f"[केवल सिमुलेशन – आधिकारिक चेतावनी नहीं] रायपुर ग्रीष्मकालीन लू चेतावनी ({ambient_temp_c:.1f}°C)"
        )
        ET.SubElement(info_hi, "description").text = (
            f"अनुमानित अधिकतम तापमान {ambient_temp_c:.1f}°C। बिजली की चरम मांग {peak_demand_mw:.1f} MW तक पहुंचने का अनुमान है, "
            f"जिससे 420 MW के ग्रीष्मकालीन अनुबंध से {shortfall_mw:.1f} MW की कमी हो सकती है। "
            f"असुरक्षित बस्तियों ({top_zone_names}) में टीन की छतों के नीचे तीव्र गर्मी का प्रभाव।"
        )
        add_param(info_hi, "review_status", "NEEDS_NATIVE_SPEAKER_REVIEW")
        add_param(info_hi, "simulation_watermark", "केवल सिमुलेशन – आधिकारिक चेतावनी नहीं")

        # ── 3. Chhattisgarhi <info> Block (Flagged for Native Speaker Review)
        info_cg = ET.SubElement(root, "info")
        ET.SubElement(info_cg, "language").text = "hne-IN"
        ET.SubElement(info_cg, "category").text = "Met"
        ET.SubElement(info_cg, "event").text = "कड़क घाम अउ बिजली संकट (सिमुलेशन)"
        ET.SubElement(info_cg, "urgency").text = urgency
        ET.SubElement(info_cg, "severity").text = severity
        ET.SubElement(info_cg, "certainty").text = "Observed"
        ET.SubElement(info_cg, "headline").text = (
            f"[सिर्फ सिमुलेशन – कोनो सरकारी चेतावनी नोहे] रायपुर म भारी घाम के संदेस ({ambient_temp_c:.1f}°C)"
        )
        ET.SubElement(info_cg, "description").text = (
            f"अटकल म रायपुर के तापमान {ambient_temp_c:.1f}°C पहुंचे के संभावना हे। बिजली के मांग {peak_demand_mw:.1f} MW "
            f"होही, जेकर से {shortfall_mw:.1f} MW के बिजली कमी हो सकत हे। टिन छावनी म भारी तपन के खतरा।"
        )
        add_param(info_cg, "review_status", "NEEDS_NATIVE_SPEAKER_REVIEW")
        add_param(info_cg, "simulation_watermark", "सिर्फ सिमुलेशन – कोनो सरकारी चेतावनी नोहे")

        # Pretty-print XML
        raw_xml = ET.tostring(root, encoding="utf-8")
        parsed = minidom.parseString(raw_xml)
        return parsed.toprettyxml(indent="  ", encoding="utf-8").decode("utf-8")
