"""
AGNAYA - Biometeorological Alerts & Trilingual Broadcasts View
Renders pythermalcomfort UTCI/WBGT, tin-roof trap factors, trilingual drafts, and CAP v1.2 XML export.

MANDATORY DISCLAIMER: SIMULATION ONLY – NOT AN OFFICIAL WARNING.
"""

import streamlit as st

from models.trilingual_alerts import TrilingualAlertGenerator
from models.cap_alerts import CAPAlertGenerator
from data.raipur_data import RAIPUR_ZONES


def render_alerts_view(T_peak: float, rel_humidity: float, power_outage_sim: float, tripped_id: str | None):
    st.markdown('<div class="section-head">Biometeorological Risk & Trilingual Civil Broadcasts</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-subhead">Universal Thermal Climate Index (UTCI) biometeorology and Kutcha/Tin-Roof Heat Trap factor, '
        'with draft municipal civil protection bulletins in Hindi, Chhattisgarhi, and English. '
        '<b>Simulation only &mdash; not an official warning.</b></div>',
        unsafe_allow_html=True
    )

    trilingual_gen = TrilingualAlertGenerator()
    utci_data = trilingual_gen.compute_biomet_utci(ambient_temp_c=T_peak, relative_humidity=rel_humidity)

    # Bento Metric Tiles
    u1, u2, u3, u4 = st.columns(4)
    with u1:
        st.markdown(f"""
        <div class="bento-tile tile-heat">
          <div class="stat-eyebrow">Biometeorological UTCI</div>
          <div class="stat-figure-row">
            <span class="stat-number {'critical' if utci_data['utci_temp_c'] >= 46 else 'warning'}">{utci_data['utci_temp_c']:.1f}</span>
            <span class="stat-unit">°C</span>
          </div>
          <div class="stat-caption">{utci_data['thermal_stress_category']}</div>
        </div>
        """, unsafe_allow_html=True)

    with u2:
        st.markdown(f"""
        <div class="bento-tile tile-grid">
          <div class="stat-eyebrow">Wet-Bulb Temp (Twb)</div>
          <div class="stat-figure-row">
            <span class="stat-number">{utci_data.get('wet_bulb_temp_c', 28.5):.1f}</span>
            <span class="stat-unit">°C</span>
          </div>
          <div class="stat-caption">pythermalcomfort solver</div>
        </div>
        """, unsafe_allow_html=True)

    with u3:
        st.markdown(f"""
        <div class="bento-tile tile-gold">
          <div class="stat-eyebrow">WBGT Index</div>
          <div class="stat-figure-row">
            <span class="stat-number warning">{utci_data.get('wbgt_temp_c', 34.0):.1f}</span>
            <span class="stat-unit">°C</span>
          </div>
          <div class="stat-caption">Outdoor work-rest threshold</div>
        </div>
        """, unsafe_allow_html=True)

    with u4:
        trap_pen = min(6.5, 4.0 * 0.35 + 0.8 * power_outage_sim)
        st.markdown(f"""
        <div class="bento-tile tile-heat">
          <div class="stat-eyebrow">Tin-Roof Thermal Penalty</div>
          <div class="stat-figure-row">
            <span class="stat-number critical">+{trap_pen:.1f}</span>
            <span class="stat-unit">°C</span>
          </div>
          <div class="stat-caption">Slum indoor heat entrapment</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # Trilingual Broadcast Previews
    st.markdown('<div class="section-head">Standardized Draft Broadcast Bulletins (Vernacular Previews)</div>', unsafe_allow_html=True)
    alerts_data = trilingual_gen.generate_all_language_alerts(
        ambient_temp_c=T_peak,
        effective_temp_c=utci_data["utci_temp_c"],
        risk_level=utci_data["thermal_stress_category"],
        power_outage_hours=power_outage_sim,
        critical_zone="Z05 Tikrapara"
    )

    lang_tab1, lang_tab2, lang_tab3 = st.tabs(["हिंदी (Hindi)", "छत्तीसगढ़ी (Chhattisgarhi)", "English"])

    with lang_tab1:
        hi = alerts_data["hi"]
        st.markdown(f"""
        <div class="disclaimer-banner">
          <strong>भाषाई समीक्षा सूचना (Review Notice):</strong> {hi['review_warning']}
        </div>
        <div class="callout-box callout-gold">
          <div style="font-weight:600;font-size:14px;color:#FCD34D;">शीर्षक: {hi['headline']}</div>
          <div style="margin-top:6px;line-height:1.6;color:#CBD5E1;">{hi['body']}</div>
          <div style="margin-top:10px;font-weight:600;color:#F8FAFC;">नागरिक सलाह (Citizen Advisories):</div>
          <ul style="margin:4px 0 0 16px;padding:0;color:#94A3B8;">
            {''.join(f'<li>{act}</li>' for act in hi.get('actions', []))}
          </ul>
        </div>
        """, unsafe_allow_html=True)

    with lang_tab2:
        cg = alerts_data["hne"]
        st.markdown(f"""
        <div class="disclaimer-banner">
          <strong>भाखा समीक्षा सूचना (Review Notice):</strong> {cg['review_warning']}
        </div>
        <div class="callout-box callout-patina">
          <div style="font-weight:600;font-size:14px;color:#5EEAD4;">शीर्षक: {cg['headline']}</div>
          <div style="margin-top:6px;line-height:1.6;color:#CBD5E1;">{cg['body']}</div>
          <div style="margin-top:10px;font-weight:600;color:#F8FAFC;">सिखौना अउ उपाय (Citizen Advisories):</div>
          <ul style="margin:4px 0 0 16px;padding:0;color:#94A3B8;">
            {''.join(f'<li>{act}</li>' for act in cg.get('actions', []))}
          </ul>
        </div>
        """, unsafe_allow_html=True)

    with lang_tab3:
        en = alerts_data["en"]
        st.markdown(f"""
        <div class="disclaimer-banner">
          <strong>Review Notice:</strong> {en['review_warning']}
        </div>
        <div class="callout-box">
          <div style="font-weight:600;font-size:14px;color:#F8FAFC;">Headline: {en['headline']}</div>
          <div style="margin-top:6px;line-height:1.6;color:#CBD5E1;">{en['body']}</div>
          <div style="margin-top:10px;font-weight:600;color:#F8FAFC;">Citizen Advisories:</div>
          <ul style="margin:4px 0 0 16px;padding:0;color:#94A3B8;">
            {''.join(f'<li>{act}</li>' for act in en.get('actions', []))}
          </ul>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # OASIS CAP v1.2 XML Export Section
    st.markdown('<div class="section-head">Common Alerting Protocol (OASIS CAP v1.2) Standard Export</div>', unsafe_allow_html=True)
    st.markdown(
        "Generate and download compliant CAP v1.2 XML documents for emergency dispatch interoperability tests. "
        "Strictly labelled <code>&lt;status&gt;Draft&lt;/status&gt;</code> and <code>SIMULATION ONLY</code>."
    )

    cap_gen = CAPAlertGenerator()
    cap_xml = cap_gen.generate_cap_alert(
        ambient_temp_c=T_peak,
        relative_humidity_pct=rel_humidity,
        peak_demand_mw=475.9,
        shortfall_mw=55.9,
        critical_zones=RAIPUR_ZONES[:3],
        tripped_substation=tripped_id
    )

    c_prev, c_dwn = st.columns([2.5, 1])
    with c_prev:
        with st.expander("Preview OASIS CAP v1.2 XML Payload", expanded=False):
            st.code(cap_xml[:1200] + "\n... [truncated]", language="xml")
    with c_dwn:
        st.download_button(
            label="Export OASIS CAP v1.2 XML",
            data=cap_xml,
            file_name=f"CAP_ALERT_RAIPUR_{T_peak:.1f}C_SIMULATION.xml",
            mime="application/xml",
            use_container_width=True
        )
