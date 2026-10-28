"""
AGNAYA - Adaptive Geospatial Network for Heatwave Analytics and Yield Assessment
Raipur, Chhattisgarh | Municipal & Grid Operations Twin

Synthesized Research Frameworks:
  - kd365/heatwave-public: 3-Agent Collaborative AI Pipeline & MILP Dispatch
  - parisproffitt/GridStressDigitalTwin: 7-Stage Progressive Heatwave Timeline & Transformer Thermal Models
  - doaamostafa67988/GridPulse-AI: 5-Component Deterministic Risk Engine & Statutory Audit Reports
  - Nihita49/TAPAS: UTCI Biometeorology, Tin-Roof Heat Trap & Trilingual Public Advisories
  - emliang/Heat-Analysis: IEEE Std 738-2012 Dynamic Line Rating (DTR) & Catenary Sag Clearance
  - nabilkhondaker/ClimateSim: Synchronous DC Power Flow (P = B*theta) & System Resilience Curves Q(t)

Data Grounding:
  - CSERC Tariff Order FY 2024-25 (CSPDCL / CSPTCL / CSPGCL)
  - CSPTCL Substation & Transmission Grid Records (220/132/33 kV)
  - IMD Climatological Normals 1970–2024 & Census of India 2011 (Raipur Municipal Corporation)
"""

import streamlit as st
import streamlit.components.v1 as components
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import folium
from folium import plugins
from datetime import datetime, timezone, timedelta
import base64
import sys, os

# ── Path Setup & Local Models Ingestion
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# Authenticated CARTO Basemaps API Key
CARTO_KEY = "cb1_4luv_1_702fe094ac8114d4005f2fa3"

from data.raipur_data import (
    RAIPUR_ZONES, RAIPUR_SUBSTATIONS, RAIPUR_WATER_PUMPS,
    RAIPUR_HOSPITALS, RAIPUR_CLIMATE, HISTORICAL_HEATWAVES,
    INTERVENTION_OPTIONS, COOLING_CENTRES, CSPDCL_PARAMS,
)
from models.cascade_model import (
    DemandModel, InfrastructureNetwork, MonteCarloCascade,
    InterventionOptimizer, compute_zone_risk_table,
)
from models.grid_digital_twin import GridStressNetwork, compute_spatial_load_distribution
from models.tapas_health import TapasHealthEngine, HAP_MEASURES
from models.conductor_ampacity import ConductorThermalAmpacity, RAIPUR_TRANSMISSION_CORRIDORS
from models.agents_pipeline import SpatialClimateAgent, ThreatAssessmentAgent, DispatchCommanderAgent
from models.climate_analytics import ClimateAnalyticsEngine

# Advanced Synthesized Models
from models.grid_power_flow import DCPowerFlowEngine
from models.progressive_heatwave import ProgressiveHeatwaveSimulator
from models.system_resilience import SystemResilienceEngine
from models.trilingual_alerts import TrilingualAlertGenerator
from models.gridpulse_risk import GridPulseRiskEngine

@st.cache_data
def get_logo_base64():
    logo_path = os.path.join(BASE_DIR, "assets", "agnaya_logo.png")
    if os.path.exists(logo_path):
        with open(logo_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return None

logo_b64 = get_logo_base64()
logo_img_path = os.path.join(BASE_DIR, "assets", "agnaya_logo.png")

# ══════════════════════════════════════════════════════════════
# PAGE CONFIGURATION
# ══════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="AGNAYA — Raipur Heatwave & Grid Digital Twin",
    page_icon=logo_img_path if os.path.exists(logo_img_path) else "⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ══════════════════════════════════════════════════════════════
# LOAD UNIFIED STYLESHEET
# ══════════════════════════════════════════════════════════════
styles_path = os.path.join(BASE_DIR, "styles.css")
if os.path.exists(styles_path):
    with open(styles_path, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# SHARED PLOTLY TEMPLATE (Utility & Municipal Theme)
# ══════════════════════════════════════════════════════════════
def apply_utility_chart_theme(fig, height=320, show_legend=True):
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=height,
        margin=dict(l=16, r=16, t=24, b=16),
        font=dict(family="Inter, -apple-system, BlinkMacSystemFont, sans-serif", size=12, color="#9CA3AF"),
        xaxis=dict(
            showgrid=True,
            gridcolor="#262A33",
            gridwidth=1,
            linecolor="#262A33",
            tickfont=dict(color="#9CA3AF", size=11),
            title_font=dict(color="#D1D5DB", size=12),
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor="#262A33",
            gridwidth=1,
            linecolor="#262A33",
            tickfont=dict(color="#9CA3AF", size=11),
            title_font=dict(color="#D1D5DB", size=12),
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(color="#D1D5DB", size=11),
            bgcolor="rgba(0,0,0,0)"
        ) if show_legend else dict(visible=False),
    )
    return fig

def render_metric_card(col, label: str, value: str, unit: str = "", caption: str = "", status: str = ""):
    status_cls = f"status-{status}" if status else ""
    unit_html = f'<span class="metric-unit">{unit}</span>' if unit else ""
    caption_html = f'<div class="metric-caption">{caption}</div>' if caption else ""
    col.markdown(f"""
    <div class="metric-card">
      <div class="metric-label">{label}</div>
      <div class="metric-value-row">
        <span class="metric-number {status_cls}">{value}</span>
        {unit_html}
      </div>
      {caption_html}
    </div>
    """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# SIDEBAR: OPERATIONAL PARAMETERS
# ══════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("""
    <div class="sidebar-title-container">
      <div class="sidebar-app-name">AGNAYA</div>
      <div class="sidebar-subtext">Raipur Heatwave & Grid Digital Twin</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="sidebar-section-heading">Scenario presets</div>', unsafe_allow_html=True)
    preset = st.selectbox(
        "Operational scenario",
        [
            "Custom parameters",
            "May 2024 heatwave (44.8°C, high grid strain)",
            "May 2015 extreme event (47.2°C, 220 kV contingency)",
            "Extreme multi-day peak (48.5°C, 4h feeder outage)"
        ],
        index=0,
        label_visibility="collapsed"
    )

    if preset == "May 2024 heatwave (44.8°C, high grid strain)":
        def_temp, def_rh, def_dur, def_out, def_trip = 44.8, 30.0, 4, 1.0, 0
    elif preset == "May 2015 extreme event (47.2°C, 220 kV contingency)":
        def_temp, def_rh, def_dur, def_out, def_trip = 47.2, 28.0, 7, 4.0, 1
    elif preset == "Extreme multi-day peak (48.5°C, 4h feeder outage)":
        def_temp, def_rh, def_dur, def_out, def_trip = 48.5, 32.0, 6, 6.0, 1
    else:
        def_temp, def_rh, def_dur, def_out, def_trip = 45.5, 35.0, 4, 2.0, 0

    st.markdown('<div class="sidebar-section-heading">Meteorological conditions</div>', unsafe_allow_html=True)
    T_peak = st.slider(
        "Peak daytime temperature (°C)", 38.0, 50.0, float(def_temp), 0.5,
        help="Forecasted maximum dry-bulb temperature recorded at Raipur IMD station #42809."
    )
    rel_humidity = st.slider(
        "Relative humidity (%)", 15.0, 80.0, float(def_rh), 5.0,
        help="Afternoon ambient humidity; affects wet-bulb globe temperature and heat index."
    )
    duration_days = st.slider(
        "Heatwave duration (days)", 1, 10, int(def_dur),
        help="Consecutive days of extreme temperatures causing compound thermal storage."
    )
    power_outage_sim = st.slider(
        "Feeder outage duration (hours)", 0.0, 12.0, float(def_out), 0.5,
        help="Simulated daily power interruption duration per residential feeder."
    )

    st.markdown('<div class="sidebar-section-heading">Grid operational parameters</div>', unsafe_allow_html=True)
    sub_options = [
        "None",
        "S01 - Raipur Main (220 kV)",
        "S02 - Mowa (132 kV)",
        "S03 - Amanaka (132 kV)",
        "S06 - Gudhiyari (33 kV)"
    ]
    tripped_sub = st.selectbox(
        "N-1 Substation contingency",
        sub_options,
        index=def_trip,
        help="Simulates an unexpected trip of a primary CSPTCL transmission substation."
    )
    tripped_id = tripped_sub.split(" - ")[0] if tripped_sub != "None" else None

    st.markdown('<div class="sidebar-section-heading">Resource allocation</div>', unsafe_allow_html=True)
    budget_lakh = st.number_input(
        "Municipal budget (₹ Lakhs)", 10.0, 500.0, 80.0, 10.0,
        help="Total municipal contingency funds allocated for heat mitigation assets."
    )

    st.markdown("""
    <div style="font-size:11.5px;color:#6B7280;margin-top:24px;padding-top:12px;border-top:1px solid #262A33;line-height:1.45;">
      <b>Data Grounding:</b><br/>
      • CSERC Tariff Order FY 2024–25<br/>
      • CSPTCL Substation Records<br/>
      • IMD Raipur Normals (1970–2024)<br/>
      • Census of India 2011 (RMC)
    </div>
    """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# HEADER: OPERATIONAL STATUS & CONTEXT
# ══════════════════════════════════════════════════════════════
dm = DemandModel()
t_h, D_mw = dm.simulate(T_peak, duration_days)
peak_d = float(np.max(D_mw))
cap_normal = CSPDCL_PARAMS["raipur_peak_demand_mw"]
shortfall = max(0, peak_d - cap_normal)

now_ist = datetime.now(timezone(timedelta(hours=5, minutes=30))).strftime("%d %b %Y, %H:%M IST")

if T_peak >= 46.0 or shortfall > 50:
    alert_name = "Critical"
    alert_badge_cls = "status-badge-critical"
    alert_dot_cls = "status-dot-critical"
elif T_peak >= 44.0 or shortfall > 0:
    alert_name = "Severe"
    alert_badge_cls = "status-badge-warning"
    alert_dot_cls = "status-dot-warning"
elif T_peak >= 42.0:
    alert_name = "Elevated"
    alert_badge_cls = "status-badge-warning"
    alert_dot_cls = "status-dot-warning"
else:
    alert_name = "Normal"
    alert_badge_cls = "status-badge-ok"
    alert_dot_cls = "status-dot-ok"

logo_html = f'<img src="data:image/png;base64,{logo_b64}" style="width:38px;height:38px;border-radius:4px;object-fit:cover;" />' if logo_b64 else ''

st.markdown(f"""
<div class="app-header">
  <div class="app-header-left">
    {logo_html}
    <div>
      <h1 class="app-title">AGNAYA — Heatwave & Grid Digital Twin</h1>
      <p class="app-subtitle">Raipur Municipal Corporation &middot; Chhattisgarh State Power Distribution Company Ltd (CSPDCL)</p>
    </div>
  </div>
  <div class="app-header-status">
    <div class="status-badge {alert_badge_cls}">
      <span class="status-dot {alert_dot_cls}"></span>
      <span>Alert level: {alert_name}</span>
    </div>
    <div class="status-badge status-badge-neutral">
      <span>Simulated load: <b>{peak_d:.0f} MW</b></span>
    </div>
    <div class="status-badge status-badge-neutral">
      <span>{now_ist}</span>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# THE 9 REFINED OPERATIONAL TABS
# ══════════════════════════════════════════════════════════════
(
    tab_overview,
    tab_timeline,
    tab_map,
    tab_powerflow,
    tab_substations,
    tab_alerts,
    tab_dispatch,
    tab_montecarlo,
    tab_resilience
) = st.tabs([
    "Overview",
    "Timeline",
    "Map",
    "Power flow",
    "Substations",
    "Alerts",
    "Dispatch",
    "Monte Carlo",
    "Resilience"
])

# ──────────────────────────────────────────────────────────────
# TAB 1: OVERVIEW
# ──────────────────────────────────────────────────────────────
with tab_overview:
    c1, c2, c3, c4 = st.columns(4)
    render_metric_card(
        c1, "Ambient air temperature", f"{T_peak:.1f}", "°C",
        caption="Raipur Station #42809",
        status="critical" if T_peak >= 45 else "warning" if T_peak >= 42 else "ok"
    )
    render_metric_card(
        c2, "Peak grid demand", f"{peak_d:.0f}", "MW",
        caption=f"Baseline normal: {CSPDCL_PARAMS['raipur_normal_demand_mw']} MW",
        status="warning" if peak_d > cap_normal else "ok"
    )
    surge_mw = peak_d - CSPDCL_PARAMS['raipur_normal_demand_mw']
    surge_pct = (peak_d / CSPDCL_PARAMS['raipur_normal_demand_mw'] - 1.0) * 100
    render_metric_card(
        c3, "Demand surge", f"+{surge_mw:.0f}", "MW",
        caption=f"+{surge_pct:.0f}% above base load",
        status="critical" if shortfall > 0 else "warning"
    )
    render_metric_card(
        c4, "Grid capacity balance", f"{shortfall:.0f}" if shortfall > 0 else f"{cap_normal - peak_d:.0f}", "MW",
        caption=f"{'Shortfall beyond threshold' if shortfall > 0 else 'Remaining capacity margin'}",
        status="critical" if shortfall > 0 else "ok"
    )

    # Historical Precedent Matching
    similar = [h for h in HISTORICAL_HEATWAVES if abs(h["peak_temp"] - T_peak) < 1.5]
    if similar:
        h_ev = sorted(similar, key=lambda x: abs(x["peak_temp"] - T_peak))[0]
        st.markdown(f"""
        <div class="note-box">
          <b>Historical precedent ({h_ev['year']}):</b> Raipur recorded <b>{h_ev['peak_temp']}°C</b> over {h_ev['duration_days']} consecutive days, resulting in approximately <b>{h_ev['deaths_estimated']} heat-related casualties</b> and up to <b>{h_ev['max_outage_hours']}h feeder shedding</b>. Active scenario parameters closely match this empirical event profile.
        </div>
        """, unsafe_allow_html=True)

    col_l, col_r = st.columns([3, 2])
    with col_l:
        st.markdown('<div class="section-title">Electricity demand trajectory (continuous ODE dynamics)</div>', unsafe_allow_html=True)
        fig_d = go.Figure()
        fig_d.add_trace(go.Scatter(
            x=t_h / 24, y=D_mw, name="Simulated demand",
            line=dict(color="#3B82F6", width=2.5),
            fill="tozeroy", fillcolor="rgba(59, 130, 246, 0.08)",
        ))
        fig_d.add_hline(
            y=cap_normal, line_dash="dash", line_color="#EF4444",
            annotation_text=f"Grid threshold ({cap_normal} MW)",
            annotation_position="top left",
            annotation_font=dict(color="#EF4444", size=11)
        )
        fig_d.add_hline(
            y=CSPDCL_PARAMS["raipur_normal_demand_mw"], line_dash="dot", line_color="#6B7280",
            annotation_text="Base demand (310 MW)",
            annotation_position="bottom left",
            annotation_font=dict(color="#9CA3AF", size=11)
        )
        fig_d.update_layout(
            xaxis_title="Simulation timeline (days)",
            yaxis_title="Power demand (MW)",
        )
        apply_utility_chart_theme(fig_d, height=310, show_legend=False)
        st.plotly_chart(fig_d, use_container_width=True)

    with col_r:
        st.markdown('<div class="section-title">Historical extreme heatwaves (IMD Raipur)</div>', unsafe_allow_html=True)
        hdf = pd.DataFrame(HISTORICAL_HEATWAVES)
        fig_h = px.scatter(
            hdf, x="peak_temp", y="deaths_estimated",
            size="duration_days", color="max_outage_hours",
            text="year", color_continuous_scale="Reds", size_max=22,
        )
        fig_h.update_traces(textposition="top center", marker=dict(line=dict(width=1, color="#374151")))
        fig_h.add_vline(
            x=T_peak, line_dash="dash", line_color="#F59E0B",
            annotation_text=f"Scenario ({T_peak}°C)",
            annotation_position="top right",
            annotation_font=dict(color="#F59E0B", size=11)
        )
        fig_h.update_layout(
            xaxis_title="Peak temperature (°C)",
            yaxis_title="Recorded casualties",
            coloraxis_colorbar=dict(title="Outage (h)", tickfont=dict(size=10)),
        )
        apply_utility_chart_theme(fig_h, height=310, show_legend=False)
        st.plotly_chart(fig_h, use_container_width=True)

# ──────────────────────────────────────────────────────────────
# TAB 2: TIMELINE
# ──────────────────────────────────────────────────────────────
with tab_timeline:
    st.markdown('<div class="section-title">Progressive heatwave lifecycle</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-desc">Simulates seven progressive operational phases—from atmospheric onset and cooling surge to conductor thermal sag, tin-roof heat trapping, and lifeline restoration.</div>', unsafe_allow_html=True)

    sim_heatwave = ProgressiveHeatwaveSimulator()
    stages = sim_heatwave.get_all_stages()

    selected_stage_idx = st.slider(
        "Operational stage",
        min_value=1, max_value=7, value=3,
        format="Stage %d",
        help="Select an operational phase to inspect coupled grid, health, and civil response directives."
    )

    stage_info = sim_heatwave.get_stage_details(selected_stage_idx)

    # Active Stage Overview Card
    st.markdown(f"""
    <div class="advisory-card">
      <div class="advisory-card-header">
        <div>
          <div class="advisory-authority">Phase {stage_info['stage_idx']} of 7 &middot; Horizon: {stage_info['time_label']}</div>
          <div class="advisory-headline">{stage_info['name']}</div>
        </div>
        <div class="status-badge status-badge-warning">
          <span>Active stage</span>
        </div>
      </div>
      <div class="advisory-body">{stage_info['description']}</div>
    </div>
    """, unsafe_allow_html=True)

    tk1, tk2, tk3, tk4 = st.columns(4)
    render_metric_card(
        tk1, "Ambient temperature", f"{stage_info['ambient_temp_c']:.1f}", "°C",
        caption="Citywide mean dry-bulb",
        status="critical" if stage_info['ambient_temp_c'] >= 44 else "warning"
    )
    render_metric_card(
        tk2, "Demand surge", f"+{stage_info['demand_surge_mw']:.0f}", "MW",
        caption="Above baseline demand",
        status="warning" if stage_info['demand_surge_mw'] > 60 else "ok"
    )
    render_metric_card(
        tk3, "Transformer thermal aging", f"{stage_info['transformer_aging_factor']:.1f}", "x",
        caption="Insulation degradation rate",
        status="critical" if stage_info['transformer_aging_factor'] >= 4 else "warning"
    )
    render_metric_card(
        tk4, "Projected ER admissions", f"{stage_info['hospital_heat_admissions']}", "patients/day",
        caption="Raipur AIIMS & District Hospital",
        status="critical" if stage_info['hospital_heat_admissions'] > 80 else "ok"
    )

    st.markdown('<div class="section-title">Multi-asset parameter progression (Stages 1–7)</div>', unsafe_allow_html=True)
    timeline_df = sim_heatwave.generate_timeline_dataframe()

    # Short stage names to eliminate overlapping/rotated labels
    timeline_df["stage_short"] = [f"Stage {i}" for i in timeline_df["stage_idx"]]

    fig_timeline = go.Figure()
    fig_timeline.add_trace(go.Scatter(
        x=timeline_df["stage_short"], y=timeline_df["ambient_temp_c"],
        name="Ambient temp (°C)", line=dict(color="#EF4444", width=2.5),
        mode="lines+markers", marker=dict(size=7),
        customdata=timeline_df["stage_name"],
        hovertemplate="<b>%{customdata}</b><br>Stage: %{x}<br>Ambient Temp: %{y:.1f}°C<extra></extra>"
    ))
    fig_timeline.add_trace(go.Scatter(
        x=timeline_df["stage_short"], y=timeline_df["demand_surge_mw"],
        name="Demand surge (MW)", line=dict(color="#3B82F6", width=2, dash="dash"),
        mode="lines+markers", marker=dict(size=7), yaxis="y2",
        customdata=timeline_df["stage_name"],
        hovertemplate="<b>%{customdata}</b><br>Stage: %{x}<br>Demand Surge: +%{y:.0f} MW<extra></extra>"
    ))
    fig_timeline.add_trace(go.Scatter(
        x=timeline_df["stage_short"], y=timeline_df["transformer_aging_factor"],
        name="Aging acceleration factor (x)", line=dict(color="#F59E0B", width=2, dash="dot"),
        mode="lines+markers", marker=dict(size=6), yaxis="y3",
        customdata=timeline_df["stage_name"],
        hovertemplate="<b>%{customdata}</b><br>Stage: %{x}<br>Aging Rate: %{y:.1f}x<extra></extra>"
    ))

    active_stage_short = f"Stage {stage_info['stage_idx']}"
    fig_timeline.add_vline(x=active_stage_short, line_dash="solid", line_color="#D1D5DB", opacity=0.5)
    fig_timeline.add_annotation(
        x=active_stage_short, y=stage_info["ambient_temp_c"],
        text=f"Selected: Stage {stage_info['stage_idx']}",
        showarrow=True, arrowhead=2, arrowsize=1, arrowwidth=1.2, arrowcolor="#D1D5DB",
        ax=0, ay=-32,
        font=dict(color="#FFFFFF", size=11, family="Inter"),
        bgcolor="#1E232D", bordercolor="#323744", borderwidth=1, borderpad=4
    )

    fig_timeline.update_layout(
        xaxis=dict(title="Progressive lifecycle stages", tickangle=0),
        yaxis=dict(title=dict(text="Ambient temp (°C)", font=dict(color="#EF4444")), tickfont=dict(color="#EF4444")),
        yaxis2=dict(title=dict(text="Demand surge (MW)", font=dict(color="#3B82F6")), tickfont=dict(color="#3B82F6"), overlaying="y", side="right"),
        yaxis3=dict(title=dict(text="Aging factor (x)", font=dict(color="#F59E0B")), tickfont=dict(color="#F59E0B"), overlaying="y", side="right", anchor="free", position=0.96),
    )
    apply_utility_chart_theme(fig_timeline, height=330, show_legend=True)
    st.plotly_chart(fig_timeline, use_container_width=True)

    c_casc, c_recom = st.columns(2)
    with c_casc:
        st.markdown('<div class="section-title">Cross-asset cascading dependencies</div>', unsafe_allow_html=True)
        st.markdown(f"""
        <div class="advisory-card">
          <div style="font-size:13px;color:#D1D5DB;line-height:1.6;">
            <b>Thermal, grid, and public health interactions:</b><br/>
            {stage_info['cross_asset_cascade']}
          </div>
          <div style="margin-top:12px;padding-top:10px;border-top:1px solid #262A33;font-size:12px;color:#9CA3AF;">
            <b>Active critical lifelines:</b> {' &bull; '.join(stage_info['active_lifelines'])}
          </div>
        </div>
        """, unsafe_allow_html=True)

    with c_recom:
        st.markdown('<div class="section-title">Operational response directives</div>', unsafe_allow_html=True)
        recom_items = "".join([f"<li style='margin-bottom:4px;'>{r}</li>" for r in stage_info['recommendations']])
        st.markdown(f"""
        <div class="advisory-card">
          <ul class="advisory-actions-list" style="margin:0;padding-left:18px;">
            {recom_items}
          </ul>
        </div>
        """, unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────
# TAB 3: MAP
# ──────────────────────────────────────────────────────────────
with tab_map:
    st.markdown('<div class="section-title">Geospatial risk digital twin</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-desc">Grounded GIS layout of Raipur: 220/132/33 kV transmission lines, substation transformers, water treatment plants, emergency hospitals, and municipal wards.</div>', unsafe_allow_html=True)

    tapas_eng = TapasHealthEngine()
    htsi_data = {w["zone_id"]: w for w in tapas_eng.compute_ward_htsi(T_peak, power_outage_sim)}
    cond_eng = ConductorThermalAmpacity()
    gtwin = GridStressNetwork()
    sub_eval = {s["substation_id"]: s for s in gtwin.compute_composite_grid_risk(T_peak, peak_d, tripped_id)}

    m = folium.Map(
        location=[21.2514, 81.6296],
        zoom_start=13,
        tiles=None,
        control_scale=True,
    )

    folium.TileLayer(
        tiles=f"https://basemaps.cartocdn.com/rastertiles/dark_all/{{z}}/{{x}}/{{y}}.png?key={CARTO_KEY}",
        attr='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> &copy; <a href="https://carto.com/attributions">CARTO</a>',
        name="CARTO Dark Matter (Muted)",
        max_zoom=19,
        subdomains="abcd",
        overlay=False,
        control=True,
    ).add_to(m)

    folium.TileLayer(
        tiles=f"https://basemaps.cartocdn.com/rastertiles/light_all/{{z}}/{{x}}/{{y}}.png?key={CARTO_KEY}",
        attr='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> &copy; <a href="https://carto.com/attributions">CARTO</a>',
        name="CARTO Positron (Light)",
        max_zoom=19,
        subdomains="abcd",
        overlay=False,
        control=True,
    ).add_to(m)

    # 1. Thermal Heatmap Layer (Smaller radius, muted gradient)
    fg_heat = folium.FeatureGroup(name="Thermal risk layer", show=True)
    heat_points = []
    for z in RAIPUR_ZONES:
        hw = htsi_data.get(z["id"], {})
        est_t = hw.get("est_indoor_temp_c", T_peak)
        intensity = max(0.2, min(1.2, (est_t - 36.0) / 10.0))
        heat_points.append([z["lat"], z["lon"], intensity])
        for dx, dy in [(0.005, 0.004), (-0.005, 0.005), (0.006, -0.005), (-0.005, -0.004)]:
            heat_points.append([z["lat"] + dx, z["lon"] + dy, intensity * 0.7])
    # Industrial heat zones
    heat_points.append([21.2950, 81.5950, 1.1])  # Urla Industrial
    heat_points.append([21.3200, 81.6300, 1.0])  # Siltara Belt
    plugins.HeatMap(
        heat_points, radius=18, blur=14, max_zoom=15, min_opacity=0.3,
        gradient={0.2: "#3B82F6", 0.5: "#F59E0B", 0.8: "#EF4444", 1.0: "#DC2626"}
    ).add_to(fg_heat)
    fg_heat.add_to(m)

    # 2. Transmission Corridors
    fg_corridors = folium.FeatureGroup(name="Transmission corridors (220/132/33 kV)", show=True)
    sub_coords = {s["id"]: [s["lat"], s["lon"]] for s in RAIPUR_SUBSTATIONS}
    corridor_specs = [
        {"id": "LINE_01", "name": "Bhilai - Raipur Main 220 kV", "from": [21.1938, 81.3509], "to": sub_coords["S01"], "voltage": 220, "conductor": "ACSR Zebra", "rated_amps": 1050, "normal_mw": 340.0, "sub_from": "BHILAI", "sub_to": "S01"},
        {"id": "LINE_02", "name": "Raipur Main - Mowa 132 kV", "from": sub_coords["S01"], "to": sub_coords["S02"], "voltage": 132, "conductor": "ACSR Panther", "rated_amps": 620, "normal_mw": 115.0, "sub_from": "S01", "sub_to": "S02"},
        {"id": "LINE_03", "name": "Raipur Main - Amanaka 132 kV", "from": sub_coords["S01"], "to": sub_coords["S03"], "voltage": 132, "conductor": "ACSR Panther", "rated_amps": 620, "normal_mw": 98.0, "sub_from": "S01", "sub_to": "S03"},
        {"id": "LINE_04", "name": "Mowa - Pandri 33 kV", "from": sub_coords["S02"], "to": sub_coords["S04"], "voltage": 33, "conductor": "ACSR Dog", "rated_amps": 380, "normal_mw": 35.0, "sub_from": "S02", "sub_to": "S04"},
        {"id": "LINE_05", "name": "Amanaka - Gudhiyari 33 kV", "from": sub_coords["S03"], "to": sub_coords["S06"], "voltage": 33, "conductor": "ACSR Dog", "rated_amps": 380, "normal_mw": 42.0, "sub_from": "S03", "sub_to": "S06"},
        {"id": "LINE_06", "name": "Pandri - Khamardih 33 kV", "from": sub_coords["S04"], "to": sub_coords["S05"], "voltage": 33, "conductor": "ACSR Dog", "rated_amps": 380, "normal_mw": 28.0, "sub_from": "S04", "sub_to": "S05"},
        {"id": "LINE_07", "name": "Mandir Hasaud - Pandri 132 kV", "from": [21.2589, 81.7750], "to": sub_coords["S04"], "voltage": 132, "conductor": "ACSR Panther", "rated_amps": 620, "normal_mw": 85.0, "sub_from": "MANDIR_HASAUD", "sub_to": "S04"},
    ]

    for corr in corridor_specs:
        derated_amps = corr["rated_amps"] * max(0.65, 1.0 - (T_peak - 40.0) * 0.015)
        derate_pct = max(0.0, (1.0 - derated_amps / corr["rated_amps"]) * 100.0)
        line_tripped = (tripped_id in [corr["sub_from"], corr["sub_to"]])

        if line_tripped:
            line_col = "#EF4444"
            dash = "6, 6"
            st_label = "Contingency trip"
            flow_mw = 0.0
        elif derate_pct > 8.0:
            line_col = "#F59E0B"
            dash = None
            st_label = f"Derated (-{derate_pct:.1f}%)"
            flow_mw = corr["normal_mw"] * (peak_d / 310.0) * 0.85
        else:
            line_col = "#3B82F6"
            dash = None
            st_label = "Normal"
            flow_mw = corr["normal_mw"] * (peak_d / 310.0) * 0.85

        folium.PolyLine(
            locations=[corr["from"], corr["to"]],
            color=line_col, weight=4 if corr["voltage"] >= 132 else 2.5,
            opacity=0.85, dash_array=dash,
            tooltip=folium.Tooltip(
                f"<b>{corr['name']}</b><br/>"
                f"Status: {st_label}<br/>"
                f"Voltage: {corr['voltage']} kV | Normal Flow: {flow_mw:.1f} MW<br/>"
                f"Ampacity: {derated_amps:.0f} A (-{derate_pct:.1f}%)"
            )
        ).add_to(fg_corridors)
    fg_corridors.add_to(m)

    # 3. Municipal Wards
    fg_zones = folium.FeatureGroup(name="Municipal wards", show=True)
    for z in RAIPUR_ZONES:
        hw = htsi_data.get(z["id"], {})
        b_col = "#EF4444" if hw.get("risk_band") == "SEVERE" else "#F59E0B" if hw.get("risk_band") == "HIGH" else "#10B981"
        folium.CircleMarker(
            location=[z["lat"], z["lon"]],
            radius=max(8, min(16, z["population"] / 9000)),
            color=b_col, fill=True, fill_color=b_col, fill_opacity=0.35, weight=1.5,
            tooltip=folium.Tooltip(
                f"<b>{z['name']} ({z['id']})</b><br/>"
                f"Population: {z['population']:,} | Slum Density: {z['slum_pct']*100:.0f}%<br/>"
                f"HTSI Score: {hw.get('htsi_score', 0):.1f} ({hw.get('risk_band', 'N/A')})<br/>"
                f"Est. Indoor Temp: {hw.get('est_indoor_temp_c', 0):.1f}°C (+{hw.get('tin_roof_penalty_c', 0):.1f}°C trap)<br/>"
                f"Served by: {z['substation']}"
            ),
        ).add_to(fg_zones)
    fg_zones.add_to(m)

    # 4. Substations (Clean circular markers)
    fg_subs = folium.FeatureGroup(name="CSPTCL Substations", show=True)
    for s in RAIPUR_SUBSTATIONS:
        se = sub_eval.get(s["id"], {})
        is_t = (s["id"] == tripped_id)
        hp = se.get("hotspot_temp_c", 90.0)
        ld = se.get("effective_load_pct", s["load_factor_normal"] * 100)
        marker_color = "#EF4444" if is_t else "#F59E0B" if hp > 115 else "#10B981"

        folium.CircleMarker(
            location=[s["lat"], s["lon"]],
            radius=8,
            color=marker_color,
            fill=True,
            fill_color=marker_color,
            fill_opacity=0.9,
            weight=2,
            tooltip=folium.Tooltip(
                f"<b>{s['name']} ({s['voltage_kv']} kV)</b><br/>"
                f"Status: {'Tripped (N-1)' if is_t else 'High thermal load' if hp > 115 else 'Normal'}<br/>"
                f"Load: {ld:.0f}% | Hot-spot: {hp:.1f}°C"
            ),
        ).add_to(fg_subs)
    fg_subs.add_to(m)

    # 5. Lifelines (Water & Hospitals)
    fg_water = folium.FeatureGroup(name="Water treatment plants", show=False)
    for wp in RAIPUR_WATER_PUMPS:
        folium.Marker(
            location=[wp["lat"], wp["lon"]],
            icon=folium.Icon(icon="tint", prefix="fa", color="blue"),
            tooltip=f"{wp['name']} ({wp['capacity_MLD']} MLD)",
        ).add_to(fg_water)
    fg_water.add_to(m)

    fg_hosp = folium.FeatureGroup(name="Emergency hospitals", show=False)
    for h in RAIPUR_HOSPITALS:
        folium.Marker(
            location=[h["lat"], h["lon"]],
            icon=folium.Icon(icon="plus", prefix="fa", color="gray"),
            tooltip=f"{h['name']} ({h['total_beds']} beds)",
        ).add_to(fg_hosp)
    fg_hosp.add_to(m)

    plugins.Fullscreen(position="topleft").add_to(m)
    folium.LayerControl(position="topright", collapsed=False).add_to(m)

    col_map, col_side = st.columns([3.2, 1.1])
    with col_map:
        components.html(m._repr_html_(), height=620, scrolling=False)

    with col_side:
        st.markdown('<div class="section-title">Substation SCADA telemetry</div>', unsafe_allow_html=True)
        for s in RAIPUR_SUBSTATIONS:
            se = sub_eval.get(s["id"], {})
            is_t = (s["id"] == tripped_id)
            hp = se.get("hotspot_temp_c", 90.0)
            ld = se.get("effective_load_pct", s["load_factor_normal"] * 100)
            st_class = "status-badge-critical" if is_t else "status-badge-warning" if hp > 115 else "status-badge-ok"
            st_text = "Tripped" if is_t else "High temp" if hp > 115 else "Normal"
            st.markdown(f"""
            <div style="background:#161920;border:1px solid #262A33;padding:9px 12px;border-radius:6px;margin-bottom:8px;">
              <div style="display:flex;justify-content:space-between;align-items:center;">
                <span style="font-weight:600;font-size:13px;color:#F3F4F6;">{s['name'][:20]}</span>
                <span class="status-badge {st_class}" style="padding:2px 6px;font-size:11px;">{st_text}</span>
              </div>
              <div style="color:#9CA3AF;font-size:12px;margin-top:4px;">
                Load: {ld:.0f}% &middot; Hotspot: <span style="font-family:'JetBrains Mono',monospace;">{hp:.1f}°C</span>
              </div>
            </div>
            """, unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────
# TAB 4: POWER FLOW
# ──────────────────────────────────────────────────────────────
with tab_powerflow:
    st.markdown('<div class="section-title">Transmission power flow & conductor clearance</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-desc">Fast DC power flow solution ([P] = [B][&theta;]) across Raipur\'s 6-bus transmission network paired with IEEE Std 738-2012 dynamic line rating (DTR) and catenary conductor sag calculations.</div>', unsafe_allow_html=True)

    pf_engine = DCPowerFlowEngine()

    c_pf1, c_pf2 = st.columns([2, 1])
    with c_pf1:
        line_choices = ["None"] + [f"{l['line_id']}: {l['name']}" for l in pf_engine.lines]
        chosen_line_trip = st.selectbox("Simulate line outage (N-1 contingency)", line_choices, index=0)
        tripped_line_key = chosen_line_trip.split(":")[0] if chosen_line_trip != "None" else None

    with c_pf2:
        wind_speed_slider = st.slider("Conductor cross-wind speed (m/s)", 0.2, 5.0, 1.2, 0.2, help="Wind perpendicular to conductors provides convective cooling.")

    base_pf = pf_engine.solve_dc_power_flow(total_demand_mw=peak_d, tripped_line_id=None)
    contingency_pf = pf_engine.solve_dc_power_flow(total_demand_mw=peak_d, tripped_line_id=tripped_line_key)
    dtr_results = pf_engine.compute_ieee738_dtr(ambient_temp_c=T_peak, wind_speed_ms=wind_speed_slider)

    pk1, pk2, pk3, pk4 = st.columns(4)
    max_flow_pct = max(contingency_pf["line_loadings_pct"].values()) if contingency_pf["line_loadings_pct"] else 0.0
    overloaded_count = len(contingency_pf["overloaded_lines"])
    avg_derating = np.mean([d["derating_pct"] for d in dtr_results])
    crit_sag = sum(1 for d in dtr_results if d["sag_risk"] == "CRITICAL")

    render_metric_card(
        pk1, "Max line loading", f"{max_flow_pct:.1f}", "%",
        caption="Highest loaded corridor",
        status="critical" if max_flow_pct >= 100 else "warning" if max_flow_pct >= 85 else "ok"
    )
    render_metric_card(
        pk2, "Overloaded corridors", f"{overloaded_count}", "lines",
        caption="Exceeding thermal ampacity",
        status="critical" if overloaded_count > 0 else "ok"
    )
    render_metric_card(
        pk3, "Average thermal derating", f"-{avg_derating:.1f}", "%",
        caption=f"At {T_peak:.1f}°C ambient",
        status="warning"
    )
    render_metric_card(
        pk4, "Sag clearance alerts", f"{crit_sag}", "spans",
        caption="Ground clearance below limit",
        status="critical" if crit_sag > 0 else "ok"
    )

    st.markdown('<div class="section-title">Transmission corridor loading: Normal vs. Post-contingency</div>', unsafe_allow_html=True)
    flow_comp_rows = []
    for l in pf_engine.lines:
        lid = l["line_id"]
        # Short clean name
        short_name = l["name"].replace("Transmission Line", "").replace("Interconnector", "").strip()
        flow_comp_rows.append({
            "Line": f"{lid}: {short_name}",
            "Base loading (%)": base_pf["line_loadings_pct"].get(lid, 0.0),
            "Contingency loading (%)": contingency_pf["line_loadings_pct"].get(lid, 0.0),
            "Rating MW": l["rating_mw"],
            "Flow MW": contingency_pf["line_flows_mw"].get(lid, 0.0)
        })
    fdf = pd.DataFrame(flow_comp_rows)

    fig_flows = go.Figure()
    fig_flows.add_trace(go.Bar(
        x=fdf["Line"], y=fdf["Base loading (%)"], name="Base loading (all lines in service)",
        marker_color="#3B82F6"
    ))
    fig_flows.add_trace(go.Bar(
        x=fdf["Line"], y=fdf["Contingency loading (%)"], name=f"Contingency loading ({tripped_line_key or 'None'})",
        marker_color="#EF4444"
    ))
    fig_flows.add_hline(y=100.0, line_dash="dash", line_color="#EF4444", annotation_text="100% Thermal rating limit")
    fig_flows.add_hline(y=80.0, line_dash="dot", line_color="#F59E0B", annotation_text="80% Operational threshold")
    fig_flows.update_layout(
        barmode="group",
        yaxis_title="Line loading (%)",
        xaxis_title="CSPTCL Transmission corridors",
    )
    apply_utility_chart_theme(fig_flows, height=310, show_legend=True)
    st.plotly_chart(fig_flows, use_container_width=True)

    c_ang, c_sag = st.columns([1, 2.2])
    with c_ang:
        st.markdown('<div class="section-title">Bus voltage angles (&theta;)</div>', unsafe_allow_html=True)
        bus_angles = [
            {"Bus": b, "Angle (deg)": ang}
            for b, ang in contingency_pf["bus_angles_deg"].items()
        ]
        st.dataframe(
            pd.DataFrame(bus_angles),
            use_container_width=True,
            hide_index=True,
            column_config={
                "Bus": st.column_config.TextColumn("Substation bus"),
                "Angle (deg)": st.column_config.NumberColumn("Phase angle (°)", format="%.2f°")
            }
        )

    with c_sag:
        st.markdown('<div class="section-title">IEEE Std 738 DTR & conductor sag clearance</div>', unsafe_allow_html=True)
        sag_table = [
            {
                "Line": d["name"][:24],
                "Conductor": d["conductor"],
                "Static MVA": d["static_rating_mva"],
                "DTR MVA": d["dtr_rating_mva"],
                "Derating": d["derating_pct"],
                "Mid-Span Sag": d["sag_clearance_m"],
                "Risk": d["sag_risk"]
            }
            for d in dtr_results
        ]
        st.dataframe(
            pd.DataFrame(sag_table),
            use_container_width=True,
            hide_index=True,
            column_config={
                "Line": st.column_config.TextColumn("Corridor"),
                "Conductor": st.column_config.TextColumn("Conductor type"),
                "Static MVA": st.column_config.NumberColumn("Static MVA", format="%.0f"),
                "DTR MVA": st.column_config.NumberColumn("DTR MVA", format="%.0f"),
                "Derating": st.column_config.NumberColumn("Derating", format="-%.1f%%"),
                "Mid-Span Sag": st.column_config.NumberColumn("Ground clearance", format="%.2f m"),
                "Risk": st.column_config.TextColumn("Clearance status")
            }
        )

# ──────────────────────────────────────────────────────────────
# TAB 5: SUBSTATIONS
# ──────────────────────────────────────────────────────────────
with tab_substations:
    st.markdown('<div class="section-title">Substation transformer digital twin</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-desc">Thermal models per IEEE C57.91-2011: winding hot-spot temperature rise, top-oil thermal response, spatial neighbor overload stress, and insulation aging acceleration factor (F_AA).</div>', unsafe_allow_html=True)

    sub_eval_list = list(sub_eval.values())
    sc1, sc2, sc3, sc4 = st.columns(4)
    avg_hotspot = np.mean([s["hotspot_temp_c"] for s in sub_eval_list if not s["tripped"]])
    crit_subs = sum(1 for s in sub_eval_list if s["risk_level"] == "CRITICAL" and not s["tripped"])
    max_aging = max(s["aging_factor"] for s in sub_eval_list if not s["tripped"])

    render_metric_card(
        sc1, "Average hot-spot temperature", f"{avg_hotspot:.1f}", "°C",
        caption="Baseline aging limit: 110°C",
        status="warning" if avg_hotspot >= 105 else "ok"
    )
    render_metric_card(
        sc2, "Transformers under stress", f"{crit_subs}", f"/ {len(sub_eval_list)}",
        caption="Load > 90% or Hotspot > 115°C",
        status="critical" if crit_subs > 0 else "ok"
    )
    render_metric_card(
        sc3, "Peak aging acceleration", f"{max_aging:.1f}", "x",
        caption="Relative to nominal rate",
        status="critical" if max_aging >= 5 else "warning"
    )
    render_metric_card(
        sc4, "Simulated N-1 contingency", f"{tripped_id or 'None'}", "",
        caption="Load redirected to adjacent buses",
        status="warning" if tripped_id else "ok"
    )

    st.markdown('<div class="section-title">Substation digital twin telemetry</div>', unsafe_allow_html=True)
    sub_df = pd.DataFrame(sub_eval_list)
    st.dataframe(
        sub_df[[
            "substation_id", "name", "voltage_kv", "capacity_mva", "load_ratio",
            "load_mw_approx", "hotspot_temp_c", "top_oil_temp_c", "aging_factor", "risk_level"
        ]],
        use_container_width=True,
        hide_index=True,
        column_config={
            "substation_id": st.column_config.TextColumn("ID", width="small"),
            "name": st.column_config.TextColumn("Substation name"),
            "voltage_kv": st.column_config.NumberColumn("Voltage", format="%d kV"),
            "capacity_mva": st.column_config.NumberColumn("Capacity", format="%.0f MVA"),
            "load_ratio": st.column_config.ProgressColumn("Load ratio", format="%.2f", min_value=0.0, max_value=1.5),
            "load_mw_approx": st.column_config.NumberColumn("Load (MW)", format="%.1f"),
            "hotspot_temp_c": st.column_config.NumberColumn("Hotspot temp", format="%.1f °C"),
            "top_oil_temp_c": st.column_config.NumberColumn("Top-oil temp", format="%.1f °C"),
            "aging_factor": st.column_config.NumberColumn("Aging acceleration", format="%.2fx"),
            "risk_level": st.column_config.TextColumn("Status")
        }
    )

    st.markdown('<div class="section-title">Transmission corridor thermal ratings (IEEE Std 738-2012)</div>', unsafe_allow_html=True)
    lines_eval = cond_eng.evaluate_all_corridors(T_peak)
    lines_df = pd.DataFrame(lines_eval)
    st.dataframe(
        lines_df[[
            "corridor_id", "name", "voltage_kv", "conductor_type", "rated_capacity_mw",
            "derated_capacity_mw", "derating_percentage", "normal_flow_mw", "loading_percentage", "status"
        ]],
        use_container_width=True,
        hide_index=True,
        column_config={
            "corridor_id": st.column_config.TextColumn("ID", width="small"),
            "name": st.column_config.TextColumn("Corridor name"),
            "voltage_kv": st.column_config.NumberColumn("Voltage", format="%d kV"),
            "conductor_type": st.column_config.TextColumn("Conductor"),
            "rated_capacity_mw": st.column_config.NumberColumn("Static rating", format="%.1f MW"),
            "derated_capacity_mw": st.column_config.NumberColumn("DTR rating", format="%.1f MW"),
            "derating_percentage": st.column_config.NumberColumn("Derating", format="%.1f%%"),
            "normal_flow_mw": st.column_config.NumberColumn("Flow (MW)", format="%.1f"),
            "loading_percentage": st.column_config.ProgressColumn("Loading", format="%.1f%%", min_value=0.0, max_value=120.0),
            "status": st.column_config.TextColumn("Status")
        }
    )

# ──────────────────────────────────────────────────────────────
# TAB 6: ALERTS
# ──────────────────────────────────────────────────────────────
with tab_alerts:
    st.markdown('<div class="section-title">Heat-health risk & public advisories</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-desc">Universal Thermal Climate Index (UTCI) biometeorology and Kutcha/Tin-Roof Heat Trap factor, with municipal civil protection bulletins in Hindi, Chhattisgarhi, and English.</div>', unsafe_allow_html=True)

    trilingual_gen = TrilingualAlertGenerator()
    utci_data = trilingual_gen.compute_biomet_utci(ambient_temp_c=T_peak, relative_humidity=rel_humidity)

    u1, u2, u3, u4 = st.columns(4)
    render_metric_card(
        u1, "Biometeorological UTCI", f"{utci_data['utci_temp_c']:.1f}", "°C",
        caption=utci_data['thermal_stress_category'],
        status="critical" if utci_data['utci_temp_c'] >= 46 else "warning"
    )
    render_metric_card(
        u2, "IMD Departure", f"+{T_peak - 42.4:.1f}", "°C",
        caption="Above Raipur normal (42.4°C)",
        status="critical" if T_peak - 42.4 >= 4 else "warning"
    )
    render_metric_card(
        u3, "Advisory level", utci_data['health_action_urgency'], "",
        caption="Action threshold active",
        status="warning"
    )
    render_metric_card(
        u4, "Emergency routing", "108 / 112 / 1912", "",
        caption="Health / Disaster / Power helplines",
        status="ok"
    )

    alerts_data = trilingual_gen.generate_trilingual_alerts(
        ambient_temp_c=T_peak,
        relative_humidity=rel_humidity,
        active_outage_hours=power_outage_sim,
        primary_affected_zone="Birgaon Industrial & Urla Slum Belt"
    )

    st.markdown('<div class="section-title">Civil protection broadcast bulletins</div>', unsafe_allow_html=True)
    lang_tab1, lang_tab2, lang_tab3 = st.tabs(["हिंदी (Hindi)", "छत्तीसगढ़ी (Chhattisgarhi)", "English"])

    with lang_tab1:
        hindi_acts = "".join([f"<li>{act}</li>" for act in alerts_data['hindi']['actions']])
        st.markdown(f"""
        <div class="advisory-card">
          <div class="advisory-card-header">
            <div>
              <div class="advisory-authority">कार्यालय कलेक्टर एवं जिला दंडाधिकारी, रायपुर &middot; जिला आपदा प्रबंधन प्राधिकरण</div>
              <div class="advisory-headline">{alerts_data['hindi']['headline']}</div>
            </div>
            <div class="advisory-meta">
              जारी समय: {now_ist}<br/>
              संदर्भ: DDMA/RPR/HW-2024
            </div>
          </div>
          <div class="advisory-body">{alerts_data['hindi']['body']}</div>
          <div class="advisory-actions-title">आवश्यक जनसुरक्षा निर्देश:</div>
          <ul class="advisory-actions-list">{hindi_acts}</ul>
          <div class="advisory-footer-contacts">
            <span>आपातकालीन सेवाएं:</span>
            <span>एम्बुलेंस: <b>108</b></span>
            <span>आपदा राहत नियंत्रण कक्ष: <b>112</b></span>
            <span>बिजली विभाग (CSPDCL): <b>1912</b></span>
          </div>
        </div>
        """, unsafe_allow_html=True)

    with lang_tab2:
        chhat_acts = "".join([f"<li>{act}</li>" for act in alerts_data['chhattisgarhi']['actions']])
        st.markdown(f"""
        <div class="advisory-card">
          <div class="advisory-card-header">
            <div>
              <div class="advisory-authority">कार्यालय कलेक्टर एवं जिला दंडाधिकारी, रायपुर &middot; जनसूचना परिपत्र</div>
              <div class="advisory-headline">{alerts_data['chhattisgarhi']['headline']}</div>
            </div>
            <div class="advisory-meta">
              जारी समय: {now_ist}<br/>
              संदर्भ: DDMA/RPR/HW-2024-CG
            </div>
          </div>
          <div class="advisory-body">{alerts_data['chhattisgarhi']['body']}</div>
          <div class="advisory-actions-title">बचे बर जरूरी उपाय:</div>
          <ul class="advisory-actions-list">{chhat_acts}</ul>
          <div class="advisory-footer-contacts">
            <span>आपातकाल संपर्क:</span>
            <span>दवा-दारू एम्बुलेंस: <b>108</b></span>
            <span>मदद नियंत्रण कक्ष: <b>112</b></span>
            <span>बिजली शिकायत: <b>1912</b></span>
          </div>
        </div>
        """, unsafe_allow_html=True)

    with lang_tab3:
        eng_acts = "".join([f"<li>{act}</li>" for act in alerts_data['english']['actions']])
        st.markdown(f"""
        <div class="advisory-card">
          <div class="advisory-card-header">
            <div>
              <div class="advisory-authority">Office of the District Magistrate & District Disaster Management Authority, Raipur</div>
              <div class="advisory-headline">{alerts_data['english']['headline']}</div>
            </div>
            <div class="advisory-meta">
              Issued: {now_ist}<br/>
              Ref: DDMA/RPR/HW-2024-ENG
            </div>
          </div>
          <div class="advisory-body">{alerts_data['english']['body']}</div>
          <div class="advisory-actions-title">Mandatory Citizen Safeguards:</div>
          <ul class="advisory-actions-list">{eng_acts}</ul>
          <div class="advisory-footer-contacts">
            <span>Emergency Helplines:</span>
            <span>Medical Emergency (Ambulance): <b>108</b></span>
            <span>Civil Protection Control Room: <b>112</b></span>
            <span>Electricity Outage Helpline: <b>1912</b></span>
          </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<div class="section-title">Ward heat vulnerability & indoor thermal trap (TAPAS model)</div>', unsafe_allow_html=True)
    tapas_res = tapas_eng.compute_ward_htsi(T_peak, power_outage_sim)
    tdf = pd.DataFrame(tapas_res)
    st.dataframe(
        tdf[[
            "zone_id", "zone_name", "population", "slum_pct", "tin_roof_penalty_c",
            "est_indoor_temp_c", "htsi_score", "risk_band", "daily_excess_deaths", "daily_emergency_admissions"
        ]],
        use_container_width=True,
        hide_index=True,
        column_config={
            "zone_id": st.column_config.TextColumn("ID", width="small"),
            "zone_name": st.column_config.TextColumn("Ward name"),
            "population": st.column_config.NumberColumn("Population", format="%d"),
            "slum_pct": st.column_config.ProgressColumn("Slum density", format="%.0f%%", min_value=0.0, max_value=1.0),
            "tin_roof_penalty_c": st.column_config.NumberColumn("Tin roof trap", format="+%.1f °C"),
            "est_indoor_temp_c": st.column_config.NumberColumn("Est. indoor temp", format="%.1f °C"),
            "htsi_score": st.column_config.ProgressColumn("HTSI score", format="%.1f", min_value=0.0, max_value=100.0),
            "risk_band": st.column_config.TextColumn("Risk level"),
            "daily_excess_deaths": st.column_config.NumberColumn("Est. excess deaths/day", format="%.1f"),
            "daily_emergency_admissions": st.column_config.NumberColumn("Est. admissions/day", format="%.0f")
        }
    )

# ──────────────────────────────────────────────────────────────
# TAB 7: DISPATCH
# ──────────────────────────────────────────────────────────────
with tab_dispatch:
    st.markdown('<div class="section-title">Resource allocation & dispatch</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-desc">Multi-agent decision pipeline: Spatial climate ingestion &rarr; Threat assessment &rarr; Mixed-Integer Linear Programming (MILP via HiGHS) allocating cooling centers, water tankers, power resilience units, and hospital surge teams.</div>', unsafe_allow_html=True)

    strat_choice = st.selectbox(
        "Optimization strategy",
        [
            "optimize_coverage (Maximize shielded population)",
            "optimize_response_time (Priority allocation to critical wards)",
            "optimize_staged_reserve (70% deployed, 30% reserve buffer)"
        ],
        index=0
    )
    clean_strat = strat_choice.split(" ")[0]

    run_pipeline = st.button("Run resource optimization")

    if run_pipeline or "pipeline_results" in st.session_state:
        if run_pipeline or "pipeline_results" not in st.session_state:
            with st.spinner("Solving Mixed-Integer Linear Program..."):
                a1 = SpatialClimateAgent()
                w_out = a1.run(T_peak, rel_humidity)
                a2 = ThreatAssessmentAgent()
                th_out = a2.run(w_out, peak_d)
                a3 = DispatchCommanderAgent()
                disp_out = a3.run(th_out, budget_lakh=budget_lakh, strategy=clean_strat)
                st.session_state["pipeline_results"] = disp_out

        disp_out = st.session_state["pipeline_results"]
        dplan = disp_out["dispatch_plan"]

        ac1, ac2, ac3 = st.columns(3)
        render_metric_card(
            ac1, "Budget allocated", f"₹ {dplan['total_cost_lakh']:.1f}", "L",
            caption=f"Budget ceiling: ₹ {budget_lakh:.1f}L",
            status="ok"
        )
        render_metric_card(
            ac2, "Estimated population protected", f"{dplan['estimated_citizens_shielded']:,}", "",
            caption="Direct protection from acute heat injury",
            status="ok"
        )
        render_metric_card(
            ac3, "Solver status", f"{dplan['solver_status']}", "",
            caption="HiGHS Mixed-Integer Linear Program",
            status="ok"
        )

        st.markdown('<div class="section-title">Allocated municipal resources</div>', unsafe_allow_html=True)
        alloc_items = [f"<b>{k.replace('_', ' ').capitalize()}</b>: {v} units" for k, v in dplan["units_allocated"].items() if v > 0]
        st.markdown(f"""
        <div class="note-box">
          {' &nbsp;&bull;&nbsp; '.join(alloc_items)}
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="section-title">Ward deployment schedule</div>', unsafe_allow_html=True)
        disp_df = pd.DataFrame([
            {
                "Ward": z["zone_name"],
                "Threat level": z["threat_level"],
                "Threat score": z["threat_score"],
                "Assigned resources": ", ".join(z["assigned_interventions"]) if z["assigned_interventions"] else "Routine surveillance"
            }
            for z in dplan["zone_assignments"]
        ])
        st.dataframe(
            disp_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Ward": st.column_config.TextColumn("Municipal ward"),
                "Threat level": st.column_config.TextColumn("Risk level"),
                "Threat score": st.column_config.ProgressColumn("Threat index", format="%.2f", min_value=0.0, max_value=1.0),
                "Assigned resources": st.column_config.TextColumn("Deployed mitigation units")
            }
        )

# ──────────────────────────────────────────────────────────────
# TAB 8: MONTE CARLO
# ──────────────────────────────────────────────────────────────
with tab_montecarlo:
    st.markdown('<div class="section-title">Stochastic cascade simulation</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-desc">Evaluates the probability of compounding urban lifeline failures (substations, water pumping, emergency hospitals) across stochastic realizations under severe heat conditions.</div>', unsafe_allow_html=True)

    mc_c1, mc_c2, mc_c3 = st.columns([1.5, 1.5, 1])
    with mc_c1:
        n_runs = st.select_slider("Stochastic realizations", [100, 250, 500, 1000], value=250)
    with mc_c2:
        compare_interventions = st.checkbox("Compare with municipal mitigation", value=True)
    with mc_c3:
        st.markdown("<div style='height:28px;'></div>", unsafe_allow_html=True)
        recompute_mc = st.button("Run simulation batch")

    mc_cache_key = f"{T_peak}_{duration_days}_{n_runs}_{compare_interventions}"
    if recompute_mc or "mc_data" not in st.session_state or st.session_state.get("mc_key") != mc_cache_key:
        with st.spinner(f"Simulating {n_runs} stochastic realizations..."):
            mc_engine = MonteCarloCascade(N_sim=n_runs)
            base_res = mc_engine.run(T_peak, duration_days, interventions={})
            if compare_interventions:
                int_res = mc_engine.run(T_peak, duration_days, interventions={
                    "power_resilience": 4, "cooling_centre": 5, "water_tankers": 15, "hospital_surge": 2
                })
            else:
                int_res = None
            st.session_state["mc_data"] = {"baseline": base_res, "intervention": int_res}
            st.session_state["mc_key"] = mc_cache_key

    mc_data = st.session_state["mc_data"]
    b_res = mc_data["baseline"]
    i_res = mc_data["intervention"]
    par = b_res["population_at_high_risk"]

    m1, m2, m3, m4, m5 = st.columns(5)
    fail_rate = b_res.get("failure_rate_percent", 75.0)
    mean_sev = b_res.get("mean_wards_severed", 3.2)
    p90_sev = b_res.get("p90_wards_severed", 6.0)
    avg_sub_fail = np.mean(list(b_res["substation_failure_prob"].values()))

    render_metric_card(
        m1, "System failure risk", f"{fail_rate:.1f}", "%",
        caption="P(&ge;1 substation outage)",
        status="critical" if fail_rate > 50 else "warning"
    )
    render_metric_card(
        m2, "Mean wards severed", f"{mean_sev:.1f}", "/ 12",
        caption=f"P90: {p90_sev:.0f} wards",
        status="critical" if mean_sev >= 4 else "warning"
    )
    render_metric_card(
        m3, "Mean at-risk population", f"{par['mean']/1000:.1f}", "k",
        caption=f"P10–P90: {par['p10']/1000:.0f}k–{par['p90']/1000:.0f}k",
        status="critical"
    )
    render_metric_card(
        m4, "Grid shortfall", f"{b_res['demand_shortfall_mw']:.0f}", "MW",
        caption=f"Surge: +{peak_d-cap_normal:.0f} MW",
        status="warning"
    )
    render_metric_card(
        m5, "Average substation risk", f"{avg_sub_fail*100:.1f}", "%",
        caption="Across all 6 substations",
        status="warning"
    )

    st.markdown('<div class="section-title">Population-at-risk probability distribution</div>', unsafe_allow_html=True)
    fig_mc_dist = go.Figure()
    raw_base = [v / 1000.0 for v in b_res.get("raw_population_at_high_risk", [par['mean']])]
    fig_mc_dist.add_trace(go.Histogram(
        x=raw_base, name="Baseline (unmitigated)",
        nbinsx=35, marker_color="rgba(239, 68, 68, 0.65)", opacity=0.75
    ))

    if i_res is not None:
        raw_int = [v / 1000.0 for v in i_res.get("raw_population_at_high_risk", [i_res["population_at_high_risk"]['mean']])]
        fig_mc_dist.add_trace(go.Histogram(
            x=raw_int, name="With municipal mitigation",
            nbinsx=35, marker_color="rgba(16, 185, 129, 0.65)", opacity=0.75
        ))
        i_par = i_res["population_at_high_risk"]
        fig_mc_dist.add_vline(
            x=i_par['mean'] / 1000.0, line_dash="dash", line_color="#10B981",
            annotation_text=f"Mitigated mean: {i_par['mean']/1000:.1f}k",
            annotation_font=dict(color="#10B981", size=11)
        )

    fig_mc_dist.add_vline(
        x=par['mean'] / 1000.0, line_dash="dash", line_color="#EF4444",
        annotation_text=f"Baseline mean: {par['mean']/1000:.1f}k",
        annotation_font=dict(color="#EF4444", size=11)
    )
    fig_mc_dist.update_layout(
        barmode="overlay",
        xaxis_title="Citizens exposed to severe thermal stress or power loss (thousands)",
        yaxis_title="Simulation realizations",
    )
    apply_utility_chart_theme(fig_mc_dist, height=310, show_legend=True)
    st.plotly_chart(fig_mc_dist, use_container_width=True)

    c_sub_f, c_ward_f = st.columns([1.3, 2.7])
    with c_sub_f:
        st.markdown('<div class="section-title">Substation failure probabilities</div>', unsafe_allow_html=True)
        sub_probs = [
            {"Substation": next(s["name"].replace("Substation", "").strip() for s in RAIPUR_SUBSTATIONS if s["id"] == sid), "Prob": p * 100.0}
            for sid, p in b_res["substation_failure_prob"].items()
        ]
        sp_df = pd.DataFrame(sub_probs)
        fig_sp = px.bar(
            sp_df, x="Prob", y="Substation", orientation="h",
            color="Prob", color_continuous_scale="Reds", text="Prob"
        )
        fig_sp.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
        fig_sp.update_layout(
            xaxis_title="Failure probability (%)", yaxis_title="",
            xaxis_range=[0, 115],
            coloraxis_showscale=False
        )
        apply_utility_chart_theme(fig_sp, height=280, show_legend=False)
        st.plotly_chart(fig_sp, use_container_width=True)

    with c_ward_f:
        st.markdown('<div class="section-title">Ward cascading disruption matrix</div>', unsafe_allow_html=True)
        ward_matrix = []
        for z in RAIPUR_ZONES:
            w_risk = b_res["water_disruption_prob"].get(z["id"], 0.0)
            h_stat = b_res["zone_health_risk"].get(z["id"], {})
            sub_id = z["substation"]
            p_risk = b_res["substation_failure_prob"].get(sub_id, 0.0)
            exposed_pop = int(h_stat.get('mean', 0.0) * z['population'])
            ward_matrix.append({
                "Ward": z["name"],
                "Population": z["population"],
                "Power loss risk": p_risk * 100.0,
                "Water cutoff risk": w_risk * 100.0,
                "Mean exposed pop": exposed_pop,
                "Slum density": z["slum_pct"]
            })
        st.dataframe(
            pd.DataFrame(ward_matrix),
            use_container_width=True,
            hide_index=True,
            column_config={
                "Ward": st.column_config.TextColumn("Municipal ward"),
                "Population": st.column_config.NumberColumn("Population", format="%d"),
                "Power loss risk": st.column_config.NumberColumn("Power risk", format="%.1f%%"),
                "Water cutoff risk": st.column_config.NumberColumn("Water risk", format="%.1f%%"),
                "Mean exposed pop": st.column_config.NumberColumn("Exposed population", format="%d"),
                "Slum density": st.column_config.ProgressColumn("Slum density", format="%.0f%%", min_value=0.0, max_value=1.0)
            }
        )

# ──────────────────────────────────────────────────────────────
# TAB 9: RESILIENCE
# ──────────────────────────────────────────────────────────────
with tab_resilience:
    st.markdown('<div class="section-title">Infrastructure resilience & risk audit</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-desc">Continuous infrastructure performance curves Q(t) &isin; [0, 1] and Area Under the Curve (AUC) resilience loss reduction, paired with statutory deterministic risk scoring.</div>', unsafe_allow_html=True)

    resilience_eng = SystemResilienceEngine()
    res_comp = resilience_eng.compare_resilience_curves(peak_temp_c=T_peak, duration_days=duration_days)
    b_resil = res_comp["baseline"]
    a_resil = res_comp["agnaya_shielded"]

    rk1, rk2, rk3, rk4, rk5 = st.columns(5)
    render_metric_card(
        rk1, "Baseline resilience", f"{b_resil['resilience_index_percent']:.1f}", "%",
        caption=f"Nadir Q_min: {b_resil['nadir_q']:.2f}",
        status="critical"
    )
    render_metric_card(
        rk2, "Mitigated resilience", f"{a_resil['resilience_index_percent']:.1f}", "%",
        caption=f"Nadir Q_min: {a_resil['nadir_q']:.2f}",
        status="ok"
    )
    render_metric_card(
        rk3, "AUC loss avoided", f"{res_comp['loss_reduction_percent']:.1f}", "%",
        caption="Area under disruption curve spared",
        status="ok"
    )
    render_metric_card(
        rk4, "Baseline recovery", f"{b_resil['recovery_time_h']:.0f}", "hrs",
        caption=f"Degradation: {b_resil['degradation_time_h']:.0f}h",
        status="warning"
    )
    render_metric_card(
        rk5, "Mitigated recovery", f"{a_resil['recovery_time_h']:.0f}", "hrs",
        caption="Accelerated restoration",
        status="ok"
    )

    st.markdown('<div class="section-title">Continuous infrastructure performance Q(t) vs. Time</div>', unsafe_allow_html=True)
    fig_res = go.Figure()
    fig_res.add_trace(go.Scatter(
        x=[t / 24.0 for t in b_resil["time_hours"]], y=b_resil["Q_t"],
        name="Baseline performance Q_base(t)",
        line=dict(color="#EF4444", width=2.5), fill="tozeroy", fillcolor="rgba(239, 68, 68, 0.06)"
    ))
    fig_res.add_trace(go.Scatter(
        x=[t / 24.0 for t in a_resil["time_hours"]], y=a_resil["Q_t"],
        name="Mitigated performance Q_shielded(t)",
        line=dict(color="#10B981", width=2.5), fill="tonexty", fillcolor="rgba(16, 185, 129, 0.12)"
    ))
    fig_res.add_hline(y=1.0, line_dash="dot", line_color="#6B7280", annotation_text="100% Normal capacity")
    fig_res.add_hline(y=0.5, line_dash="dash", line_color="#F59E0B", annotation_text="50% Severe disruption")
    fig_res.update_layout(
        xaxis_title="Time since heatwave onset (days)",
        yaxis_title="System performance quality Q(t)",
        yaxis_range=[0.0, 1.05]
    )
    apply_utility_chart_theme(fig_res, height=310, show_legend=True)
    st.plotly_chart(fig_res, use_container_width=True)

    st.markdown('<div class="section-title">Deterministic risk audit (5-factor framework)</div>', unsafe_allow_html=True)
    gpr_engine = GridPulseRiskEngine()
    gpr_wards = gpr_engine.compute_all_wards_gridpulse(ambient_temp_c=T_peak, total_grid_demand_mw=peak_d, outage_hours=power_outage_sim)
    gpr_df = pd.DataFrame(gpr_wards)

    c_audit1, c_audit2 = st.columns([1.2, 2.8])
    with c_audit1:
        st.markdown("**Inspect ward audit report:**")
        selected_zone_name = st.selectbox("Municipal ward", [z["zone_name"] for z in gpr_wards], index=0, label_visibility="collapsed")
        sel_zone_id = next(z["zone_id"] for z in gpr_wards if z["zone_name"] == selected_zone_name)
        card_data = gpr_engine.generate_boardroom_audit_report(sel_zone_id, ambient_temp_c=T_peak, total_grid_demand_mw=peak_d, outage_hours=power_outage_sim)

        st.markdown(f"""
        <div class="advisory-card">
          <div class="advisory-authority">Municipal Risk Assessment</div>
          <div class="advisory-headline" style="font-size:15px;margin-top:2px;">{card_data['zone_name']} ({card_data['zone_id']})</div>
          <div style="font-size:13px;color:#9CA3AF;margin:8px 0 12px 0;line-height:1.5;">{card_data['executive_summary']}</div>
          <div style="font-size:12.5px;color:#D1D5DB;line-height:1.7;border-top:1px solid #262A33;padding-top:8px;">
            <b>5-Factor Deterministic Weights:</b><br/>
            &bull; Hazard (30%): <b>{card_data['factors']['H_hazard']:.2f}</b><br/>
            &bull; Demand (25%): <b>{card_data['factors']['D_demand']:.2f}</b><br/>
            &bull; Asset Stress (20%): <b>{card_data['factors']['A_asset']:.2f}</b><br/>
            &bull; Outage Exposure (15%): <b>{card_data['factors']['O_outage']:.2f}</b><br/>
            &bull; Vulnerability (10%): <b>{card_data['factors']['V_vulnerability']:.2f}</b>
          </div>
          <div style="font-size:11.5px;color:#6B7280;margin-top:10px;padding-top:8px;border-top:1px solid #262A33;line-height:1.4;">
            <b>Statutory Citations:</b><br/>
            {"<br/>".join([f"&bull; {c}" for c in card_data['citations']])}
          </div>
        </div>
        """, unsafe_allow_html=True)

    with c_audit2:
        st.markdown("**Citywide 12-Ward Risk Scoring Matrix:**")
        st.dataframe(
            gpr_df[[
                "zone_id", "zone_name", "composite_risk", "risk_tier",
                "H_hazard", "D_demand", "A_asset", "O_outage", "V_vulnerability"
            ]],
            use_container_width=True,
            hide_index=True,
            column_config={
                "zone_id": st.column_config.TextColumn("ID", width="small"),
                "zone_name": st.column_config.TextColumn("Ward name"),
                "composite_risk": st.column_config.ProgressColumn("Composite risk", format="%.1f", min_value=0.0, max_value=100.0),
                "risk_tier": st.column_config.TextColumn("Risk band"),
                "H_hazard": st.column_config.NumberColumn("Hazard (H)", format="%.2f"),
                "D_demand": st.column_config.NumberColumn("Demand (D)", format="%.2f"),
                "A_asset": st.column_config.NumberColumn("Asset (A)", format="%.2f"),
                "O_outage": st.column_config.NumberColumn("Outage (O)", format="%.2f"),
                "V_vulnerability": st.column_config.NumberColumn("Vulnerability (V)", format="%.2f")
            }
        )

# ══════════════════════════════════════════════════════════════
# FOOTER
# ══════════════════════════════════════════════════════════════
st.markdown("""
<div class="app-footer">
  <div>Data sources: CSERC Tariff Order FY 2024–25 &middot; CSPTCL Grid Records &middot; IMD Climatological Normals 1970–2024 &middot; Census of India 2011</div>
  <div>AGNAYA v3.0 &middot; Raipur Municipal Corporation &amp; CSPDCL</div>
</div>
""", unsafe_allow_html=True)
