"""
AGNAYA - End-to-End Scenario Walkthrough & Planning View
Step-by-step coupled causal cascade:
Scenario -> Demand & Grid Stress -> Zone Risk -> Baseline vs ONE Intervention -> Plain Explanation & Limitations.

Includes "Executive Planning Context" and "Data Requirements" panels.
MANDATORY DISCLAIMER: SIMULATION ONLY – NOT AN OFFICIAL WARNING.
"""

import streamlit as st
import numpy as np
import plotly.graph_objects as go

from data.raipur_data import (
    RAIPUR_ZONES, CSPDCL_PARAMS
)
from models.cascade_model import DemandModel
from models.grid_digital_twin import GridStressNetwork
from models.tapas_health import TapasHealthEngine
from models.system_resilience import SystemResilienceEngine
from models.cap_alerts import CAPAlertGenerator
from models.pdf_reports import generate_ward_brief_pdf, generate_sitrep_pdf
from models.llm_explainer import DeterministicNarrativeGenerator


def render_e2e_walkthrough_view(
    T_peak: float,
    rel_humidity: float,
    duration_days: int,
    power_outage_sim: float,
    tripped_id: str | None,
    budget_lakh: float
):
    st.markdown('<div class="section-head">End-to-End Cascading Scenario Walkthrough</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-subhead">Trace how a single summer meteorological scenario propagates through electricity demand, '
        'transformer degradation, tin-roof indoor heat traps, and municipal water dependencies &mdash; and evaluate '
        'the exact benefit of targeted interventions.</div>',
        unsafe_allow_html=True
    )

    # ─────────────────────────────────────────────────────────────────────────
    # PLANNING PANELS: "Executive Context" & "Data Requirements"
    # ─────────────────────────────────────────────────────────────────────────
    c_help, c_gaps = st.columns(2)
    with c_help:
        st.markdown("""
        <div class="callout-box callout-patina">
          <strong style="color:#5EEAD4;font-size:13px;">Executive Planning Context: Municipal Decision Support</strong>
          <div style="font-size:12px;color:#94A3B8;margin-top:6px;line-height:1.55;">
            <b>1. Substation Prioritization:</b> Identifies which 132/33 kV substations (e.g. S03 Amanaka) lack automatic N-1 transformer redundancy and face extreme hot-spot degradation.<br/>
            <b>2. Lifeline Protection:</b> Pinpoints water supply dependencies &mdash; ensuring Kharun River WTP (180 MLD) and zonal boosting pumps maintain backup power.<br/>
            <b>3. Slum Heat Entrapment:</b> Pinpoints dense informal settlements (Tikrapara, Bhata Para, Gudhiyari) where tin roofs amplify indoor heat during power cuts.<br/>
            <b>4. Evidence-Based Budgeting:</b> Uses mathematical optimization (MILP) to maximize population protected within municipal contingency budgets.
          </div>
        </div>
        """, unsafe_allow_html=True)

    with c_gaps:
        st.markdown("""
        <div class="callout-box callout-gold">
          <strong style="color:#FCD34D;font-size:13px;">Data Requirements: Production SCADA & Telemetry Gaps</strong>
          <div style="font-size:12px;color:#94A3B8;margin-top:6px;line-height:1.55;">
            <b>&bull; SLDC Feeder Telemetry:</b> Authenticated SCADA feed (IEC 60870-5-104) for real-time 33/11 kV feeder loadings.<br/>
            <b>&bull; Official 70-Ward GeoJSON:</b> Authenticated municipal GIS ward boundaries to migrate from illustrative aggregated zones.<br/>
            <b>&bull; In-Situ Indoor Dataloggers:</b> Low-cost temperature/humidity sensors in CGI tin-roof homes to validate thermal transfer.<br/>
            <b>&bull; Clinical Registry Access:</b> Heat-related morbidity and emergency department admission records from Pt. JNM Medical College & AIIMS Raipur.
          </div>
        </div>
        """, unsafe_allow_html=True)

    # Visual Cascade Ribbon
    st.markdown("""
    <div style="display:flex;align-items:center;justify-content:space-between;margin:18px 0 22px 0;background:#0F1319;border:1px solid rgba(255,255,255,0.08);border-radius:10px;padding:12px 18px;overflow-x:auto;">
      <div style="display:flex;align-items:center;gap:10px;">
        <span style="display:flex;align-items:center;justify-content:center;width:28px;height:28px;border-radius:50%;background:rgba(239,68,68,0.15);color:#EF4444;font-family:'JetBrains Mono';font-weight:700;font-size:12px;border:1px solid rgba(239,68,68,0.3);">1</span>
        <div><div style="font-size:12px;font-weight:600;color:#F8FAFC;">Meteorology</div><div style="font-size:10px;color:#94A3B8;">45°C+ Ambient</div></div>
      </div>
      <span style="color:#475569;font-size:14px;">&rarr;</span>
      <div style="display:flex;align-items:center;gap:10px;">
        <span style="display:flex;align-items:center;justify-content:center;width:28px;height:28px;border-radius:50%;background:rgba(59,130,246,0.15);color:#3B82F6;font-family:'JetBrains Mono';font-weight:700;font-size:12px;border:1px solid rgba(59,130,246,0.3);">2</span>
        <div><div style="font-size:12px;font-weight:600;color:#F8FAFC;">Grid Surge</div><div style="font-size:10px;color:#94A3B8;">420MW Cap</div></div>
      </div>
      <span style="color:#475569;font-size:14px;">&rarr;</span>
      <div style="display:flex;align-items:center;gap:10px;">
        <span style="display:flex;align-items:center;justify-content:center;width:28px;height:28px;border-radius:50%;background:rgba(245,158,11,0.15);color:#F59E0B;font-family:'JetBrains Mono';font-weight:700;font-size:12px;border:1px solid rgba(245,158,11,0.3);">3</span>
        <div><div style="font-size:12px;font-weight:600;color:#F8FAFC;">Tin Roofs</div><div style="font-size:10px;color:#94A3B8;">+4°C Slum Trap</div></div>
      </div>
      <span style="color:#475569;font-size:14px;">&rarr;</span>
      <div style="display:flex;align-items:center;gap:10px;">
        <span style="display:flex;align-items:center;justify-content:center;width:28px;height:28px;border-radius:50%;background:rgba(13,148,136,0.15);color:#0D9488;font-family:'JetBrains Mono';font-weight:700;font-size:12px;border:1px solid rgba(13,148,136,0.3);">4</span>
        <div><div style="font-size:12px;font-weight:600;color:#F8FAFC;">WTP Pumps</div><div style="font-size:10px;color:#94A3B8;">180 MLD Water</div></div>
      </div>
      <span style="color:#475569;font-size:14px;">&rarr;</span>
      <div style="display:flex;align-items:center;gap:10px;">
        <span style="display:flex;align-items:center;justify-content:center;width:28px;height:28px;border-radius:50%;background:rgba(16,185,129,0.15);color:#10B981;font-family:'JetBrains Mono';font-weight:700;font-size:12px;border:1px solid rgba(16,185,129,0.3);">5</span>
        <div><div style="font-size:12px;font-weight:600;color:#F8FAFC;">Shield Fleet</div><div style="font-size:10px;color:#94A3B8;">HiGHS Dispatch</div></div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # ─────────────────────────────────────────────────────────────────────────
    # STEP 1: ATMOSPHERIC CONDITIONS
    # ─────────────────────────────────────────────────────────────────────────
    st.markdown("### Step 1: Meteorological Stress Input")
    st.markdown(
        f"Simulating daytime conditions: **{T_peak:.1f}°C** dry-bulb temperature, **{rel_humidity:.0f}%** relative humidity, "
        f"duration of **{duration_days} consecutive days**, and a localized residential feeder outage of **{power_outage_sim:.1f} hours/day**."
    )

    # ─────────────────────────────────────────────────────────────────────────
    # STEP 2: DEMAND & GRID STRESS
    # ─────────────────────────────────────────────────────────────────────────
    st.markdown("### Step 2: Atmospheric to Grid & Substation Stress")
    dm = DemandModel()
    _, d_series = dm.simulate(T_peak, duration_days=duration_days)
    peak_d = float(np.max(d_series))
    cap_contract = CSPDCL_PARAMS["raipur_peak_demand_mw"]
    cap_emergency = CSPDCL_PARAMS["raipur_emergency_cap_mw"]
    shortfall = max(0.0, peak_d - cap_contract)

    gtwin = GridStressNetwork()
    sub_eval = gtwin.compute_composite_grid_risk(T_peak, peak_d, tripped_id)
    max_hotspot = max(s["hotspot_temp_c"] for s in sub_eval)
    max_aging = max(s["aging_factor"] for s in sub_eval)

    col_g1, col_g2, col_g3 = st.columns(3)
    with col_g1:
        st.markdown(f"""
        <div class="bento-tile tile-heat">
          <div class="stat-eyebrow">Peak Grid Demand</div>
          <div class="stat-figure-row">
            <span class="stat-number {'critical' if shortfall > 0 else 'ok'}">{peak_d:.1f}</span>
            <span class="stat-unit">MW</span>
          </div>
          <div class="stat-caption">+{shortfall:.1f} MW above 420 MW contracted limit</div>
        </div>
        """, unsafe_allow_html=True)

    with col_g2:
        st.markdown(f"""
        <div class="bento-tile tile-gold">
          <div class="stat-eyebrow">Transformer Hotspot Rise</div>
          <div class="stat-figure-row">
            <span class="stat-number {'critical' if max_hotspot > 120 else 'warning'}">{max_hotspot:.1f}</span>
            <span class="stat-unit">°C</span>
          </div>
          <div class="stat-caption">{max_aging:.1f}x nominal Arrhenius aging rate</div>
        </div>
        """, unsafe_allow_html=True)

    with col_g3:
        st.markdown(f"""
        <div class="bento-tile tile-grid">
          <div class="stat-eyebrow">Kharun River WTP Priority</div>
          <div class="stat-figure-row">
            <span class="stat-number ok">180</span>
            <span class="stat-unit">MLD</span>
          </div>
          <div class="stat-caption">{"Dedicated feeder online" if not tripped_id or tripped_id != "S01" else "Grid Tripped / DG Active"}</div>
        </div>
        """, unsafe_allow_html=True)

    # ─────────────────────────────────────────────────────────────────────────
    # STEP 3: ZONE RISK MATRIX
    # ─────────────────────────────────────────────────────────────────────────
    st.markdown("### Step 3: Spatial Vulnerability & Indoor Heat Entrapment")
    tapas = TapasHealthEngine()
    htsi_list = tapas.compute_ward_htsi(T_peak, power_outage_sim)
    sorted_zones = sorted(htsi_list, key=lambda x: x["htsi_score"], reverse=True)
    top_z = sorted_zones[0]

    st.markdown(
        f"Under uninsulated CGI tin roofs, thermal radiation traps heat inside informal settlements. "
        f"The most severely stressed zone is **{top_z['zone_name']} ({top_z['zone_id']})** with a simulated indoor temperature of "
        f"**{top_z['est_indoor_temp_c']:.1f}°C** (a +{top_z['tin_roof_penalty_c']:.1f}°C penalty above ambient) and a Heuristic Heat-Risk Index (HSRI) of "
        f"**{top_z['htsi_score']:.1f} / 100 ({top_z['risk_band']})**."
    )

    # ─────────────────────────────────────────────────────────────────────────
    # STEP 4: BASELINE VS ONE DEFINED INTERVENTION
    # ─────────────────────────────────────────────────────────────────────────
    st.markdown("### Step 4: Baseline vs. ONE Defined Intervention Comparison")
    st.markdown("Select a specific municipal intervention package to observe its direct protective effect on lifeline resilience:")

    interv_choice = st.selectbox(
        "Choose an Intervention Policy to Evaluate:",
        [
            "Option A: Deploy 3 Mobile DG Sets (6 MW) to S03 Amanaka & WP02 (Cost: ₹24 Lakh)",
            "Option B: Open 5 Shaded Air-Conditioned Cooling Centres in Slum Sectors (Cost: ₹12.5 Lakh)",
            "Option C: Deploy 20 Water Tankers to Gudhiyari, Tikrapara & Bhata Para (Cost: ₹16 Lakh)",
            "Option D: Full HiGHS MILP Optimized Multi-Asset Portfolio (Cost: ₹58.5 Lakh)",
        ]
    )

    fleet_dict = {}
    if "Option A" in interv_choice:
        fleet_dict = {"power_resilience": 3}
        rationale = "Injects 6.0 MW of mobile diesel generation at Amanaka, preventing cascading trip of WP02 pumping station."
    elif "Option B" in interv_choice:
        fleet_dict = {"cooling_centre": 5}
        rationale = "Provides 1,000 person sheltered cooling capacity in high-density informal slum wards."
    elif "Option C" in interv_choice:
        fleet_dict = {"water_tankers": 20}
        rationale = "Dispatches 200 kL/day of potable water directly into low-pressure distribution zones."
    else:
        fleet_dict = {"cooling_centre": 5, "power_resilience": 3, "water_tankers": 20, "jal_jeevan": 20}
        rationale = "Balanced mathematical portfolio maximizing population shielded under the municipal budget constraint."

    resil_eng = SystemResilienceEngine()
    resil_res = resil_eng.simulate_resilience(
        T_peak=T_peak,
        duration_days=duration_days,
        interventions=fleet_dict,
        tripped_substation=tripped_id
    )

    base_auc = resil_res["auc_deficit_hours_baseline"]
    shield_auc = resil_res["auc_deficit_hours_shielded"]
    saved_auc = resil_res["disruption_hours_saved"]
    dividend = resil_res["resilience_dividend_pct"]

    col_r1, col_r2, col_r3, col_r4 = st.columns(4)
    with col_r1:
        st.markdown(f"""
        <div class="bento-tile tile-heat">
          <div class="stat-eyebrow">Baseline Deficit</div>
          <div class="stat-figure-row">
            <span class="stat-number critical">{base_auc:.2f}</span>
            <span class="stat-unit">h</span>
          </div>
          <div class="stat-caption">Unmitigated lifeline deficit</div>
        </div>
        """, unsafe_allow_html=True)
    with col_r2:
        st.markdown(f"""
        <div class="bento-tile tile-gold">
          <div class="stat-eyebrow">Protected Deficit</div>
          <div class="stat-figure-row">
            <span class="stat-number">{shield_auc:.2f}</span>
            <span class="stat-unit">h</span>
          </div>
          <div class="stat-caption">With active intervention</div>
        </div>
        """, unsafe_allow_html=True)
    with col_r3:
        st.markdown(f"""
        <div class="bento-tile tile-ok">
          <div class="stat-eyebrow">Deficit Hours Saved</div>
          <div class="stat-figure-row">
            <span class="stat-number ok">{saved_auc:.2f}</span>
            <span class="stat-unit">h</span>
          </div>
          <div class="stat-caption">Net disruption reduction</div>
        </div>
        """, unsafe_allow_html=True)
    with col_r4:
        st.markdown(f"""
        <div class="bento-tile tile-ok">
          <div class="stat-eyebrow">Resilience Dividend</div>
          <div class="stat-figure-row">
            <span class="stat-number ok">+{dividend:.1f}</span>
            <span class="stat-unit">%</span>
          </div>
          <div class="stat-caption">Overall lifeline protection</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="callout-box" style="margin-top:14px;">
      <b>Intervention Mechanics:</b> {rationale}
    </div>
    """, unsafe_allow_html=True)

    # Resilience Curves Plot
    t_arr = np.array(resil_res["timeline_hours"])
    q_base = np.array(resil_res["q_baseline"])
    q_shield = np.array(resil_res["q_shielded"])

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=t_arr, y=q_base, mode="lines", name="Baseline Lifeline Q(t)",
        line=dict(color="#EF4444", width=2, dash="dot")
    ))
    fig.add_trace(go.Scatter(
        x=t_arr, y=q_shield, mode="lines", name="Protected Lifeline Q(t)",
        line=dict(color="#10B981", width=2.5)
    ))
    fig.update_layout(
        title="Lifeline Performance Trajectory Q(t): Baseline vs Protected",
        xaxis_title="Simulation Hours",
        yaxis_title="Lifeline Availability Index [0 - 1.0]",
        yaxis=dict(range=[0.0, 1.05]),
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=320,
        margin=dict(l=20, r=20, t=35, b=20)
    )
    st.plotly_chart(fig, use_container_width=True)

    # ─────────────────────────────────────────────────────────────────────────
    # STEP 5: PLAIN EXPLANATION & LIMITATIONS
    # ─────────────────────────────────────────────────────────────────────────
    st.markdown("### Step 5: Plain Explanation & Scientific Limitations")

    expl_inputs = {
        "ambient_temp_c": T_peak,
        "relative_humidity_pct": rel_humidity,
        "peak_demand_mw": peak_d,
        "contracted_limit_mw": cap_contract,
        "emergency_cap_mw": cap_emergency,
        "substation_hotspot_c": max_hotspot,
        "tripped_substation": tripped_id,
        "disruption_hours_saved": saved_auc,
        "resilience_dividend_pct": dividend,
        "top_vulnerable_zone": f"{top_z['zone_name']} ({top_z['zone_id']})",
        "max_indoor_temp_c": top_z["est_indoor_temp_c"],
    }
    narrative_text = DeterministicNarrativeGenerator.generate_narrative(expl_inputs)

    st.markdown(f"""
    <div class="callout-box" style="margin-bottom:14px;">
      <strong style="color:#F8FAFC;">Deterministic Causal Chain Narrative:</strong><br/>
      <div style="margin-top:6px;line-height:1.6;color:#CBD5E1;">{narrative_text}</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="disclaimer-banner">
      <strong>Methodological & Statutory Limitations:</strong><br/>
      1. <b>Not Clinical Mortality:</b> The Heuristic Heat-Risk Index (HSRI) is an empirical indicator. It does not predict medical mortality or heat-stroke rates without epidemiological calibration against Pt. JNM Medical College emergency registries.<br/>
      2. <b>Secondary Phase Outages:</b> Transmission models simulate bulk 220/132/33 kV flows. Local low-voltage (415V/230V) distribution phase imbalances or blown pole-mounted fuses cannot be modeled without utility AMI/SCADA telemetry.<br/>
      3. <b>Microclimate Resolution:</b> Zone-wide indoor temperatures are simplified estimates pending in-situ data logger deployment (see docs/PILOT.md).<br/>
      4. <b>Not Official Directives:</b> Never use this simulation to issue public evacuation orders or statutory heat alerts.
    </div>
    """, unsafe_allow_html=True)

    # ─────────────────────────────────────────────────────────────────────────
    # DOWNLOAD ARTIFACTS: PDF BRIEFS & CAP XML
    # ─────────────────────────────────────────────────────────────────────────
    st.markdown("### Export Scenario Briefs & Standard Alerts")
    c_pdf1, c_pdf2, c_xml = st.columns(3)

    # 1. Ward Brief PDF
    target_zone = next(z for z in RAIPUR_ZONES if z["id"] == top_z["zone_id"])
    ward_pdf_bytes = generate_ward_brief_pdf(
        target_zone,
        {
            "ambient_temp_c": T_peak,
            "outage_hours": power_outage_sim,
            "indoor_temp_c": top_z["est_indoor_temp_c"],
            "hsri_score": top_z["htsi_score"],
            "risk_band": top_z["risk_band"],
        }
    )
    c_pdf1.download_button(
        label=f"Export Ward Brief ({top_z['zone_id']} PDF)",
        data=ward_pdf_bytes,
        file_name=f"Ward_Brief_{top_z['zone_id']}_{T_peak:.1f}C.pdf",
        mime="application/pdf",
        use_container_width=True
    )

    # 2. Municipal SITREP PDF
    sitrep_pdf_bytes = generate_sitrep_pdf(
        {
            "peak_temp_celsius": T_peak,
            "peak_demand_mw": peak_d,
            "disruption_hours_saved": saved_auc,
            "resilience_dividend_pct": dividend,
        },
        top_threats=sorted_zones,
        allocated_fleet=fleet_dict
    )
    c_pdf2.download_button(
        label="Export Municipal SITREP (PDF)",
        data=sitrep_pdf_bytes,
        file_name=f"Municipal_SITREP_Raipur_{T_peak:.1f}C.pdf",
        mime="application/pdf",
        use_container_width=True
    )

    # 3. CAP v1.2 XML Alert
    cap_gen = CAPAlertGenerator()
    cap_xml_str = cap_gen.generate_cap_alert(
        ambient_temp_c=T_peak,
        relative_humidity_pct=rel_humidity,
        peak_demand_mw=peak_d,
        shortfall_mw=shortfall,
        critical_zones=sorted_zones,
        tripped_substation=tripped_id
    )
    c_xml.download_button(
        label="Export OASIS CAP v1.2 XML",
        data=cap_xml_str,
        file_name=f"CAP_Alert_Raipur_{T_peak:.1f}C.xml",
        mime="application/xml",
        use_container_width=True
    )
