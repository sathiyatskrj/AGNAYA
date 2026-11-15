"""
AGNAYA - Adaptive Geospatial Network for Heatwave Analytics and Yield Assessment
Raipur, Chhattisgarh | Municipal & Grid Operations Twin (v3.2)

Architecture:
  Mode 1: Executive Command Center (Situational Cockpit, Causal Cascade, Progressive Lifecycle)
  Mode 2: Spatial & Physical Digital Twins (Geospatial GIS Map, Transformer Aging, DC Power Flow)
  Mode 3: Interventions, Resilience & Governance (HiGHS MILP, Q(t) Resilience, Sobol Sensitivity, Official Artifacts)

Standards & Grounding:
  - IEEE Std C57.91-2011 Clause 7 (Arrhenius Transformer Thermal Aging)
  - IEEE Std 738-2012 (Dynamic Line Rating & Conductor Catenary Sag)
  - CSERC Tariff Order FY 2024-25 (CSPDCL / CSPTCL 220/132/33 kV baselines)
  - IMD Mana Airport #42809 Climatological Normals & All-Time Extreme (47.9°C)
  - NDMA / RMI India Heat Impact Framework (2026) & IIT Roorkee HSRI
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
import sys
import os

# ── Path Setup & Local Models Ingestion
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# ── Dynamic Module Reload (Ensures live Streamlit sessions always pull fresh code from disk)
import importlib
for _mod in [
    "models.cascade_model",
    "models.trilingual_alerts",
    "models.system_resilience",
    "models.grid_digital_twin",
    "models.tapas_health",
    "models.conductor_ampacity",
    "models.grid_power_flow",
    "models.progressive_heatwave",
    "models.cap_alerts",
    "ui.views.e2e_walkthrough_view",
    "ui.views.alerts_view",
    "ui.views.dispatch_view",
    "ui.views.montecarlo_view",
    "ui.views.resilience_view",
]:
    if _mod in sys.modules:
        try:
            importlib.reload(sys.modules[_mod])
        except Exception:
            pass

from config import settings

from data.raipur_data import (
    RAIPUR_ZONES, RAIPUR_SUBSTATIONS, RAIPUR_WATER_PUMPS,
    RAIPUR_HOSPITALS, HISTORICAL_HEATWAVES,
    CSPDCL_PARAMS,
    get_asset_registry, get_provenance_summary,
)
from data.weather_feed import get_current_raipur_weather
from models.cascade_model import (
    DemandModel,
)
from models.grid_digital_twin import GridStressNetwork
from models.tapas_health import TapasHealthEngine
from models.conductor_ampacity import ConductorThermalAmpacity

# Advanced Synthesized Models
from models.grid_power_flow import DCPowerFlowEngine
from models.progressive_heatwave import ProgressiveHeatwaveSimulator

# Modular UI Views
from ui.views.e2e_walkthrough_view import render_e2e_walkthrough_view
from ui.views.alerts_view import render_alerts_view
from ui.views.dispatch_view import render_dispatch_view
from ui.views.montecarlo_view import render_montecarlo_view
from ui.views.resilience_view import render_resilience_view


@st.cache_data
def cached_simulate_demand(t_peak: float, duration_days: int):
    dm = DemandModel()
    return dm.simulate(t_peak, duration_days)


@st.cache_data
def get_logo_base64():
    logo_path = os.path.join(BASE_DIR, "assets", "agnaya_logo.png")
    if os.path.exists(logo_path):
        with open(logo_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return None


@st.cache_data
def get_svg_data_uri(svg_name: str) -> str:
    path = os.path.join(BASE_DIR, "assets", svg_name)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            b64 = base64.b64encode(f.read().encode("utf-8")).decode("utf-8")
            return f"data:image/svg+xml;base64,{b64}"
    return ""


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
        font=dict(family="Inter, -apple-system, BlinkMacSystemFont, sans-serif", size=12, color="#94A3B8"),
        xaxis=dict(
            showgrid=True,
            gridcolor="rgba(255, 255, 255, 0.05)",
            gridwidth=1,
            linecolor="rgba(255, 255, 255, 0.08)",
            tickfont=dict(color="#94A3B8", size=11),
            title_font=dict(color="#CBD5E1", size=12),
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor="rgba(255, 255, 255, 0.05)",
            gridwidth=1,
            linecolor="rgba(255, 255, 255, 0.08)",
            tickfont=dict(color="#94A3B8", size=11),
            title_font=dict(color="#CBD5E1", size=12),
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(color="#CBD5E1", size=11),
            bgcolor="rgba(0,0,0,0)"
        ) if show_legend else dict(visible=False),
    )
    return fig


def render_metric_card(col, label: str, value: str, unit: str = "", caption: str = "", status: str = "", tile_variant: str = ""):
    """Backwards-compatible wrapper rendering Bento Stat Tiles with optional color variants."""
    status_cls = f"{status}" if status else ""
    tile_cls = f"tile-{tile_variant}" if tile_variant else ""
    unit_html = f'<span class="stat-unit">{unit}</span>' if unit else ""
    caption_html = f'<div class="stat-caption">{caption}</div>' if caption else ""
    # Add gradient progress indicator for percentage values
    progress_html = ""
    try:
        num_val = float(value.replace("+", "").replace(",", "").replace("₹", ""))
        if unit in ("%", "MW", "x") and num_val > 0:
            fill_cls = "fill-critical" if status == "critical" else "fill-warning" if status == "warning" else "fill-ok" if status == "ok" else "fill-primary"
            pct = min(100, abs(num_val) * (100 / 500 if unit == "MW" else 100 / 10 if unit == "x" else 1))
            progress_html = f'<div class="progress-bar-track"><div class="progress-bar-fill {fill_cls}" style="width:{pct:.0f}%"></div></div>'
    except (ValueError, ZeroDivisionError):
        pass
    col.markdown(f"""
    <div class="bento-tile {tile_cls}">
      <div class="stat-eyebrow">{label}</div>
      <div class="stat-figure-row">
        <span class="stat-number {status_cls}">{value}</span>
        {unit_html}
      </div>
      {caption_html}
      {progress_html}
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
# SIDEBAR: OPERATIONAL PARAMETERS & CONTEXT
# ══════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("""
    <div class="sidebar-title-container">
      <div class="sidebar-app-name">AGNAYA <span style="font-size:12px;font-weight:400;color:#94A3B8;">v3.2</span></div>
      <div class="sidebar-subtext">Raipur Infrastructure Digital Twin</div>
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

    st.markdown('<div class="sidebar-section-heading">Open-Meteo Weather Feed</div>', unsafe_allow_html=True)
    live_wx = get_current_raipur_weather()
    is_synth = live_wx.get("is_synthetic_fallback", False)
    wx_badge_cls = "stat-tag-ok" if not is_synth else "stat-tag-warning"
    wx_label = "OPEN-METEO NWP" if not is_synth else "SYNTHETIC/FALLBACK"
    wx_time = (live_wx.get("retrieval_timestamp") or "N/A")[:19].replace("T", " ")

    st.markdown(f"""
    <div style="background:#11151D;border:1px solid rgba(255,255,255,0.08);border-radius:6px;padding:10px 12px;margin-bottom:10px;">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:4px;">
        <span style="font-size:11px;font-weight:600;color:#94A3B8;">GRIDDED NWP</span>
        <span class="stat-tag {wx_badge_cls}" style="font-size:10px;padding:2px 6px;">{wx_label}</span>
      </div>
      <div style="font-family:'JetBrains Mono',monospace;font-size:13px;color:#F8FAFC;font-weight:600;">
        {live_wx.get('temperature_c', 42.5):.1f}°C &middot; {live_wx.get('relative_humidity_pct', 35.0):.0f}% RH &middot; {live_wx.get('wind_speed_ms', 2.8):.1f} m/s
      </div>
      <div style="font-size:10.5px;color:#64748B;margin-top:4px;line-height:1.4;">
        Retrieved: {wx_time} UTC<br/>
        <i>Gridded NWP (21.25°N, 81.63°E). NOT official IMD station data.</i>
      </div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("Sync Sliders with Open-Meteo Feed", use_container_width=True):
        st.session_state["slider_temp"] = float(live_wx.get("temperature_c", 42.5))
        st.session_state["slider_rh"] = float(live_wx.get("relative_humidity_pct", 35.0))
        st.rerun()

    st.markdown('<div class="sidebar-section-heading">Meteorological conditions</div>', unsafe_allow_html=True)
    cur_temp_val = st.session_state.get("slider_temp", float(def_temp))
    cur_rh_val = st.session_state.get("slider_rh", float(def_rh))
    T_peak = st.slider(
        "Peak daytime temperature (°C)", 38.0, 50.0, float(cur_temp_val), 0.5,
        help="Simulated maximum dry-bulb temperature. Reference IMD all-time record: 47.9°C (May 28, 2024)."
    )
    rel_humidity = st.slider(
        "Relative humidity (%)", 15.0, 80.0, float(cur_rh_val), 5.0,
        help="Afternoon ambient relative humidity; affects wet-bulb globe temperature and heat index."
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

    prov_sum = get_provenance_summary()
    st.markdown(f"""
    <div style="font-size:11.5px;color:#94A3B8;margin-top:20px;padding:10px;background:#11151D;border:1px solid rgba(255,255,255,0.08);border-radius:6px;line-height:1.5;">
      <b style="color:#F8FAFC;">Data Provenance Audit Matrix:</b><br/>
      &bull; Parameters Audited: <b>{prov_sum.get('total_parameters_audited', 187)}</b><br/>
      &bull; Verified (CSERC/IMD): <b>{prov_sum.get('status_breakdown', {}).get('VERIFIED', 0)}</b><br/>
      &bull; Derived (GIS/Census): <b>{prov_sum.get('status_breakdown', {}).get('DERIVED', 0)}</b><br/>
      &bull; Assumed (Rules/Norms): <b>{prov_sum.get('status_breakdown', {}).get('ASSUMED', 0)}</b><br/>
      <span style="font-size:10.5px;color:#64748B;">Audited in data/DATA_SOURCES.csv</span>
    </div>
    """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# HEADER: OPERATIONAL STATUS & CONTEXT
# ══════════════════════════════════════════════════════════════
t_h, D_mw = cached_simulate_demand(T_peak, duration_days)
peak_d = float(np.max(D_mw))
cap_normal = CSPDCL_PARAMS["raipur_peak_demand_mw"]
shortfall = max(0, peak_d - cap_normal)

now_ist = datetime.now(timezone(timedelta(hours=5, minutes=30))).strftime("%d %b %Y, %H:%M IST")

if T_peak >= 46.0 or shortfall > 50:
    alert_name = "Critical"
    alert_tag_cls = "critical"
    alert_dot_cls = "critical"
elif T_peak >= 44.0 or shortfall > 0:
    alert_name = "Severe"
    alert_tag_cls = "warning"
    alert_dot_cls = "warning"
elif T_peak >= 42.0:
    alert_name = "Elevated"
    alert_tag_cls = "warning"
    alert_dot_cls = "warning"
else:
    alert_name = "Normal"
    alert_tag_cls = "ok"
    alert_dot_cls = "ok"

logo_html = f'<img src="data:image/png;base64,{logo_b64}" style="width:36px;height:36px;border-radius:4px;object-fit:cover;" />' if logo_b64 else ''

st.markdown(f"""
<div class="command-header">
  <div class="command-header-left">
    {logo_html}
    <div class="command-brand-lockup">
      <div class="command-title">AGNAYA <span style="font-weight:400;font-size:12px;color:#94A3B8;margin-left:6px;">v3.2</span></div>
      <div class="command-subtitle">Raipur Infrastructure Digital Twin &middot; Municipal &amp; Grid Decision Support</div>
    </div>
  </div>
  <div class="command-header-telemetry">
    <div class="stat-tag stat-tag-{alert_tag_cls}">
      <span class="status-dot-sm {alert_dot_cls}"></span>
      <span>{alert_name.upper()}</span>
    </div>
    <div class="stat-tag">
      <span>PEAK LOAD: <strong>{peak_d:.0f} MW</strong></span>
    </div>
    <div class="stat-tag">
      <span>{now_ist}</span>
    </div>
  </div>
</div>

<div class="disclaimer-banner">
  <strong>SIMULATION ONLY &ndash; NOT AN OFFICIAL WARNING.</strong> All models, forecasts, risk scores, and resource allocations are research approximations for municipal planning. Not endorsed by IMD, NDMA, RMC, or CSPDCL/CSPTCL.
</div>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
# THE THREE OPERATIONAL MODES (Cognitive Load Limit <= 3)
# ══════════════════════════════════════════════════════════════
active_mode = st.radio(
    "Operational Navigation Mode",
    [
        "Mode 1: Executive Command Center",
        "Mode 2: Spatial & Physical Digital Twins",
        "Mode 3: Interventions, Resilience & Governance"
    ],
    horizontal=True,
    label_visibility="collapsed"
)

# ══════════════════════════════════════════════════════════════
# MODE 1: EXECUTIVE COMMAND CENTER
# ══════════════════════════════════════════════════════════════
if active_mode == "Mode 1: Executive Command Center":
    mode1_svg = get_svg_data_uri("mode1_command.svg")
    if mode1_svg:
        st.markdown(f'<img src="{mode1_svg}" style="width:100%;height:auto;border-radius:12px;margin-bottom:16px;border:1px solid rgba(255,255,255,0.08);box-shadow:0 8px 32px rgba(0,0,0,0.4);" />', unsafe_allow_html=True)

    sub_tab_cockpit, sub_tab_cascade, sub_tab_lifecycle = st.tabs([
        "Situational Cockpit & Live Feed",
        "Coupled Causal Cascade Stepper",
        "Progressive Heatwave Lifecycle (7 Stages)"
    ])

    with sub_tab_cockpit:
        c1, c2, c3, c4 = st.columns(4)
        render_metric_card(
            c1, "Ambient air temperature", f"{T_peak:.1f}", "°C",
            caption="Raipur Station #42809",
            status="critical" if T_peak >= 45 else "warning" if T_peak >= 42 else "ok",
            tile_variant="heat"
        )
        render_metric_card(
            c2, "Peak grid demand", f"{peak_d:.0f}", "MW",
            caption=f"Contracted baseline: {CSPDCL_PARAMS['raipur_peak_demand_mw']} MW",
            status="warning" if peak_d > cap_normal else "ok",
            tile_variant="grid"
        )
        surge_mw = peak_d - CSPDCL_PARAMS['raipur_normal_demand_mw']
        surge_pct = (peak_d / CSPDCL_PARAMS['raipur_normal_demand_mw'] - 1.0) * 100
        render_metric_card(
            c3, "Demand surge", f"+{surge_mw:.0f}", "MW",
            caption=f"+{surge_pct:.0f}% above base load",
            status="critical" if shortfall > 0 else "warning",
            tile_variant="heat"
        )
        render_metric_card(
            c4, "Grid capacity balance", f"{shortfall:.0f}" if shortfall > 0 else f"{cap_normal - peak_d:.0f}", "MW",
            caption=f"{'Shortfall beyond threshold' if shortfall > 0 else 'Remaining capacity margin'}",
            status="critical" if shortfall > 0 else "ok",
            tile_variant="grid"
        )

        similar = [h for h in HISTORICAL_HEATWAVES if abs(h["peak_temp"] - T_peak) < 1.5]
        if similar:
            h_ev = sorted(similar, key=lambda x: abs(x["peak_temp"] - T_peak))[0]
            st.markdown(f"""
            <div class="callout-box">
              <strong style="color:#F8FAFC;">Historical Precedent ({h_ev['year']}):</strong> Raipur recorded <b>{h_ev['peak_temp']}°C</b> over {h_ev['duration_days']} consecutive days, resulting in approximately <b>{h_ev['deaths_estimated']} heat-related casualties</b> and up to <b>{h_ev['max_outage_hours']}h feeder shedding</b>. Active scenario parameters closely match this empirical event profile.
            </div>
            """, unsafe_allow_html=True)

        col_l, col_r = st.columns([3, 2])
        with col_l:
            st.markdown('<div class="section-head">Electricity demand trajectory (continuous ODE dynamics)</div>', unsafe_allow_html=True)
            fig_d = go.Figure()
            fig_d.add_trace(go.Scatter(
                x=t_h / 24, y=D_mw, name="Simulated demand",
                line=dict(color="#3B82F6", width=2.5),
                fill="tozeroy", fillcolor="rgba(59, 130, 246, 0.08)",
            ))
            fig_d.add_hline(
                y=cap_normal, line_dash="dash", line_color="#EF4444",
                annotation_text=f"Contracted limit ({cap_normal} MW)",
                annotation_position="top left",
                annotation_font=dict(color="#EF4444", size=11)
            )
            fig_d.add_hline(
                y=CSPDCL_PARAMS["raipur_normal_demand_mw"], line_dash="dot", line_color="#64748B",
                annotation_text="Base demand (310 MW)",
                annotation_position="bottom left",
                annotation_font=dict(color="#94A3B8", size=11)
            )
            fig_d.update_layout(
                xaxis_title="Simulation timeline (days)",
                yaxis_title="Power demand (MW)",
            )
            apply_utility_chart_theme(fig_d, height=310, show_legend=False)
            st.plotly_chart(fig_d, use_container_width=True)

        with col_r:
            st.markdown('<div class="section-head">Historical extreme heatwaves (IMD Raipur)</div>', unsafe_allow_html=True)
            hdf = pd.DataFrame(HISTORICAL_HEATWAVES)
            fig_h = px.scatter(
                hdf, x="peak_temp", y="deaths_estimated",
                size="duration_days", color="max_outage_hours",
                text="year", color_continuous_scale="Reds", size_max=20,
            )
            fig_h.update_traces(textposition="top center", marker=dict(line=dict(width=1, color="#334155")))
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

    with sub_tab_cascade:
        render_e2e_walkthrough_view(
            T_peak=T_peak,
            rel_humidity=rel_humidity,
            duration_days=duration_days,
            power_outage_sim=power_outage_sim,
            tripped_id=tripped_id,
            budget_lakh=budget_lakh
        )

    with sub_tab_lifecycle:
        st.markdown('<div class="section-head">Progressive heatwave lifecycle</div>', unsafe_allow_html=True)
        st.markdown('<div class="section-subhead">Simulates seven progressive operational phases—from atmospheric onset and cooling surge to conductor thermal sag, tin-roof heat trapping, and lifeline restoration.</div>', unsafe_allow_html=True)

        sim_heatwave = ProgressiveHeatwaveSimulator()
        stages = sim_heatwave.get_all_stages()

        selected_stage_idx = st.slider(
            "Operational stage",
            min_value=1, max_value=7, value=3,
            format="Stage %d",
            help="Select an operational phase to inspect coupled grid, health, and civil response directives."
        )

        stage_info = sim_heatwave.get_stage_details(selected_stage_idx)
        stage_eval = sim_heatwave.evaluate_stage(selected_stage_idx)

        # Visual Step Indicator Ribbon
        steps_html = []
        for s_idx in range(1, 8):
            cls = "active" if s_idx == selected_stage_idx else ("completed" if s_idx < selected_stage_idx else "")
            conn_cls = "completed" if s_idx < selected_stage_idx else ""
            steps_html.append(f'<div class="step-badge {cls}">{s_idx}</div>')
            if s_idx < 7:
                steps_html.append(f'<div class="step-connector {conn_cls}"></div>')

        st.markdown(f"""
        <div class="step-indicator" style="margin: 12px 0 16px 0;">
          {''.join(steps_html)}
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="callout-box callout-heat">
          <div style="font-size:11px;font-weight:600;text-transform:uppercase;color:#FCA5A5;letter-spacing:0.05em;">Phase {stage_info['stage_idx']} of 7 &middot; Horizon: {stage_info['time_label']}</div>
          <div style="font-size:16px;font-weight:600;color:#F8FAFC;margin:4px 0;">{stage_info['name']}</div>
          <div style="font-size:13px;color:#CBD5E1;line-height:1.6;">{stage_info['description']}</div>
        </div>
        """, unsafe_allow_html=True)

        tk1, tk2, tk3, tk4 = st.columns(4)
        render_metric_card(
            tk1, "Ambient temperature", f"{stage_info['ambient_temp_c']:.1f}", "°C",
            caption="Citywide mean dry-bulb",
            status="critical" if stage_info['ambient_temp_c'] >= 44 else "warning",
            tile_variant="heat"
        )
        render_metric_card(
            tk2, "Demand surge", f"+{stage_info['demand_surge_mw']:.0f}", "MW",
            caption="Above baseline demand",
            status="warning" if stage_info['demand_surge_mw'] > 60 else "ok",
            tile_variant="grid"
        )
        render_metric_card(
            tk3, "Transformer thermal aging", f"{stage_info['transformer_aging_factor']:.1f}", "x",
            caption="Insulation degradation rate",
            status="critical" if stage_info['transformer_aging_factor'] >= 4 else "warning",
            tile_variant="heat"
        )
        high_stress_wards = sum(1 for w in stage_eval.get('wards_health', []) if w.get('risk_band') in ['SEVERE', 'HIGH'])
        render_metric_card(
            tk4, "High-stress wards", f"{high_stress_wards} / 12", "zones",
            caption="Zones at High/Severe HSRI",
            status="critical" if high_stress_wards >= 4 else ("warning" if high_stress_wards > 0 else "ok"),
            tile_variant="civic"
        )

        st.markdown('<div class="section-head">Multi-asset parameter progression (Stages 1–7)</div>', unsafe_allow_html=True)
        timeline_df = sim_heatwave.generate_timeline_dataframe()
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
        fig_timeline.add_vline(x=active_stage_short, line_dash="solid", line_color="#CBD5E1", opacity=0.4)
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
            st.markdown('<div class="section-head">Cross-asset cascading dependencies</div>', unsafe_allow_html=True)
            st.markdown(f"""
            <div class="callout-box">
              <div style="font-size:12.5px;color:#CBD5E1;line-height:1.6;">
                <b>Thermal, grid, and public health interactions:</b><br/>
                {stage_info['cross_asset_cascade']}
              </div>
              <div style="margin-top:10px;padding-top:8px;border-top:1px solid rgba(255,255,255,0.08);font-size:11.5px;color:#94A3B8;">
                <b>Active critical lifelines:</b> {' &bull; '.join(stage_info['active_lifelines'])}
              </div>
            </div>
            """, unsafe_allow_html=True)

        with c_recom:
            st.markdown('<div class="section-head">Operational response directives</div>', unsafe_allow_html=True)
            recom_items = "".join([f"<li style='margin-bottom:4px;'>{r}</li>" for r in stage_info['recommendations']])
            st.markdown(f"""
            <div class="callout-box">
              <ul style="margin:0;padding-left:18px;font-size:12.5px;color:#CBD5E1;line-height:1.55;">
                {recom_items}
              </ul>
            </div>
            """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
# MODE 2: SPATIAL & PHYSICAL DIGITAL TWINS
# ══════════════════════════════════════════════════════════════
elif active_mode == "Mode 2: Spatial & Physical Digital Twins":
    mode2_svg = get_svg_data_uri("mode2_twins.svg")
    if mode2_svg:
        st.markdown(f'<img src="{mode2_svg}" style="width:100%;height:auto;border-radius:12px;margin-bottom:16px;border:1px solid rgba(255,255,255,0.08);box-shadow:0 8px 32px rgba(0,0,0,0.4);" />', unsafe_allow_html=True)

    sub_tab_map, sub_tab_substations, sub_tab_powerflow = st.tabs([
        "Geospatial Digital Twin (GIS Map)",
        "Substation Transformer Thermal Twin (IEEE C57.91)",
        "Transmission Power Flow & Conductor Sag (IEEE 738)"
    ])

    tapas_eng = TapasHealthEngine()
    htsi_data = {w["zone_id"]: w for w in tapas_eng.compute_ward_htsi(T_peak, power_outage_sim)}
    cond_eng = ConductorThermalAmpacity()
    gtwin = GridStressNetwork()
    sub_eval = {s["substation_id"]: s for s in gtwin.compute_composite_grid_risk(T_peak, peak_d, tripped_id)}

    with sub_tab_map:
        st.markdown('<div class="section-head">Geospatial Risk Digital Twin (Simulated)</div>', unsafe_allow_html=True)
        st.markdown('<div class="section-subhead">Illustrative GIS layout of Raipur: 220/132/33 kV transmission corridors, substation transformers, water treatment plants, emergency hospitals, and aggregated planning zones.</div>', unsafe_allow_html=True)

        m = folium.Map(
            location=[21.2514, 81.6296],
            zoom_start=13,
            tiles=None,
            control_scale=True,
        )

        if settings.CARTO_API_KEY:
            dark_tiles = f"https://basemaps.cartocdn.com/rastertiles/dark_all/{{z}}/{{x}}/{{y}}.png?key={settings.CARTO_API_KEY}"
            light_tiles = f"https://basemaps.cartocdn.com/rastertiles/light_all/{{z}}/{{x}}/{{y}}.png?key={settings.CARTO_API_KEY}"
        else:
            dark_tiles = "https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}.png"
            light_tiles = "https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}.png"

        folium.TileLayer(
            tiles=dark_tiles,
            attr='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> &copy; <a href="https://carto.com/attributions">CARTO</a>',
            name="CARTO Dark Matter (Muted)",
            max_zoom=19,
            subdomains="abcd",
            overlay=False,
            control=True,
        ).add_to(m)

        folium.TileLayer(
            tiles=light_tiles,
            attr='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> &copy; <a href="https://carto.com/attributions">CARTO</a>',
            name="CARTO Positron (Light)",
            max_zoom=19,
            subdomains="abcd",
            overlay=False,
            control=True,
        ).add_to(m)

        folium.TileLayer(
            tiles="https://tile.openstreetmap.org/{z}/{x}/{y}.png",
            attr='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
            name="OpenStreetMap Standard (Keyless)",
            max_zoom=19,
            overlay=False,
            control=True,
        ).add_to(m)

        # Thermal Layer
        fg_heat = folium.FeatureGroup(name="Thermal risk layer", show=True)
        heat_points = []
        for z in RAIPUR_ZONES:
            hw = htsi_data.get(z["id"], {})
            est_t = hw.get("est_indoor_temp_c", T_peak)
            intensity = max(0.2, min(1.2, (est_t - 36.0) / 10.0))
            heat_points.append([z["lat"], z["lon"], intensity])
            for dx, dy in [(0.005, 0.004), (-0.005, 0.005), (0.006, -0.005), (-0.005, -0.004)]:
                heat_points.append([z["lat"] + dx, z["lon"] + dy, intensity * 0.7])
        heat_points.append([21.2950, 81.5950, 1.1])
        heat_points.append([21.3200, 81.6300, 1.0])
        plugins.HeatMap(
            heat_points, radius=18, blur=14, max_zoom=15, min_opacity=0.3,
            gradient={0.2: "#3B82F6", 0.5: "#F59E0B", 0.8: "#EF4444", 1.0: "#DC2626"}
        ).add_to(fg_heat)
        fg_heat.add_to(m)

        # Corridors Layer
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
                    f"Voltage: {corr['voltage']} kV | Flow: {flow_mw:.1f} MW<br/>"
                    f"Ampacity: {derated_amps:.0f} A (-{derate_pct:.1f}%)"
                )
            ).add_to(fg_corridors)
        fg_corridors.add_to(m)

        # Zones Layer
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

        # Substations Layer
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

        # Lifelines Layer
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
            st.markdown('<div class="section-head" style="font-size:13px;">Substation Telemetry</div>', unsafe_allow_html=True)
            for s in RAIPUR_SUBSTATIONS:
                se = sub_eval.get(s["id"], {})
                is_t = (s["id"] == tripped_id)
                hp = se.get("hotspot_temp_c", 90.0)
                ld = se.get("effective_load_pct", s["load_factor_normal"] * 100)
                st_class = "critical" if is_t else "warning" if hp > 115 else "ok"
                st_text = "Tripped" if is_t else "High temp" if hp > 115 else "Normal"
                st.markdown(f"""
                <div class="bento-tile" style="padding:10px 12px;margin-bottom:8px;">
                  <div style="display:flex;justify-content:space-between;align-items:center;">
                    <span style="font-weight:600;font-size:12.5px;color:#F8FAFC;">{s['name'][:20]}</span>
                    <span class="stat-tag stat-tag-{st_class}" style="padding:1px 5px;font-size:10.5px;">{st_text}</span>
                  </div>
                  <div style="color:#94A3B8;font-size:11.5px;margin-top:4px;">
                    Load: {ld:.0f}% &middot; Hotspot: <span style="font-family:'JetBrains Mono',monospace;">{hp:.1f}°C</span>
                  </div>
                </div>
                """, unsafe_allow_html=True)

    with sub_tab_substations:
        st.markdown('<div class="section-head">Substation transformer digital twin</div>', unsafe_allow_html=True)
        st.markdown('<div class="section-subhead">Thermal models per IEEE C57.91-2011 Clause 7: winding hot-spot temperature rise, top-oil thermal response, spatial neighbor overload stress, and insulation aging acceleration factor (F_AA).</div>', unsafe_allow_html=True)

        sub_eval_list = list(sub_eval.values())
        sc1, sc2, sc3, sc4 = st.columns(4)
        avg_hotspot = np.mean([s["hotspot_temp_c"] for s in sub_eval_list if not s["tripped"]])
        crit_subs = sum(1 for s in sub_eval_list if s["risk_level"] == "CRITICAL" and not s["tripped"])
        max_aging = max(s["aging_factor"] for s in sub_eval_list if not s["tripped"])

        render_metric_card(
            sc1, "Average hot-spot temperature", f"{avg_hotspot:.1f}", "°C",
            caption="Baseline aging limit: 110°C",
            status="warning" if avg_hotspot >= 105 else "ok",
            tile_variant="heat"
        )
        render_metric_card(
            sc2, "Transformers under stress", f"{crit_subs}", f"/ {len(sub_eval_list)}",
            caption="Load > 90% or Hotspot > 115°C",
            status="critical" if crit_subs > 0 else "ok",
            tile_variant="heat"
        )
        render_metric_card(
            sc3, "Peak aging acceleration", f"{max_aging:.1f}", "x",
            caption="Relative to nominal Arrhenius rate",
            status="critical" if max_aging >= 5 else "warning",
            tile_variant="gold"
        )
        render_metric_card(
            sc4, "Simulated N-1 contingency", f"{tripped_id or 'None'}", "",
            caption="Load redirected to adjacent buses",
            status="warning" if tripped_id else "ok",
            tile_variant="grid"
        )

        # 3D Arrhenius Thermal Degradation Landscape (IEEE Std C57.91)
        st.markdown('<div class="section-head">3D Arrhenius Thermal Degradation Landscape (IEEE Std C57.91)</div>', unsafe_allow_html=True)
        st.markdown('<div class="section-subhead">Interactive 3D non-linear surface displaying the Arrhenius acceleration factor (F_AA) and insulation life consumption across varying ambient temperatures and transformer load ratios. Click and drag to rotate.</div>', unsafe_allow_html=True)

        T_amb_range = np.linspace(35, 52, 25)
        Load_range = np.linspace(0.6, 1.4, 25)
        T_grid, L_grid = np.meshgrid(T_amb_range, Load_range)
        theta_H_grid = T_grid + 64.0 * (L_grid ** 1.6)
        faa_grid = np.exp(15000.0 / 383.0 - 15000.0 / (theta_H_grid + 273.15))
        faa_grid = np.clip(faa_grid, 0.1, 50.0)

        fig_3d_arrh = go.Figure()
        fig_3d_arrh.add_trace(go.Surface(
            x=T_amb_range,
            y=Load_range,
            z=faa_grid,
            colorscale="Turbo",
            colorbar=dict(title="F_AA (x)", tickfont=dict(size=10, color="#94A3B8")),
            opacity=0.92,
            contours=dict(
                z=dict(show=True, usecolormap=True, highlightcolor="#FFFFFF", project_z=True)
            ),
            hovertemplate="Ambient Temp: %{x:.1f}°C<br>Load Ratio: %{y:.2f}<br>Aging Factor F_AA: %{z:.2f}x<extra></extra>"
        ))

        sub_x = [T_peak for s in sub_eval_list if not s["tripped"]]
        sub_y = [s["load_ratio"] for s in sub_eval_list if not s["tripped"]]
        sub_z = [s["aging_factor"] for s in sub_eval_list if not s["tripped"]]
        sub_names = [s["name"] for s in sub_eval_list if not s["tripped"]]

        fig_3d_arrh.add_trace(go.Scatter3d(
            x=sub_x,
            y=sub_y,
            z=sub_z,
            mode="markers+text",
            marker=dict(size=6, color="#FFFFFF", symbol="diamond", line=dict(color="#EF4444", width=2)),
            text=sub_names,
            textposition="top center",
            textfont=dict(color="#FEF08A", size=10),
            name="Raipur Substations",
            hovertemplate="<b>%{text}</b><br>T_amb: %{x:.1f}°C<br>Load: %{y:.2f}<br>F_AA: %{z:.2f}x<extra></extra>"
        ))

        fig_3d_arrh.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            scene=dict(
                xaxis=dict(title="Ambient Temp (°C)", backgroundcolor="rgba(15,19,25,0.6)", gridcolor="rgba(255,255,255,0.1)"),
                yaxis=dict(title="Transformer Load Ratio", backgroundcolor="rgba(15,19,25,0.6)", gridcolor="rgba(255,255,255,0.1)"),
                zaxis=dict(title="Aging Rate (F_AA)", backgroundcolor="rgba(15,19,25,0.6)", gridcolor="rgba(255,255,255,0.1)"),
                camera=dict(eye=dict(x=-1.5, y=-1.6, z=1.2))
            ),
            height=460,
            margin=dict(l=10, r=10, t=20, b=10)
        )
        st.plotly_chart(fig_3d_arrh, use_container_width=True)

        st.markdown('<div class="section-head">Substation Digital Twin Status (Simulated)</div>', unsafe_allow_html=True)
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

        st.markdown('<div class="section-head">Critical Infrastructure Asset Registry & Data Provenance</div>', unsafe_allow_html=True)
        reg_items = get_asset_registry()
        reg_df = pd.DataFrame(reg_items)
        st.dataframe(
            reg_df[[
                "asset_id", "name", "asset_class", "is_real_identifiable_asset",
                "capacity_display", "capacity_status", "link_type", "status", "confidence"
            ]],
            use_container_width=True,
            hide_index=True,
            column_config={
                "asset_id": st.column_config.TextColumn("ID", width="small"),
                "name": st.column_config.TextColumn("Asset Name"),
                "asset_class": st.column_config.TextColumn("Class"),
                "is_real_identifiable_asset": st.column_config.CheckboxColumn("Physical Asset?"),
                "capacity_display": st.column_config.TextColumn("Capacity / Sizing"),
                "capacity_status": st.column_config.TextColumn("Capacity Certainty"),
                "link_type": st.column_config.TextColumn("Topology Link"),
                "status": st.column_config.TextColumn("Data Provenance"),
                "confidence": st.column_config.TextColumn("Confidence"),
            }
        )

    with sub_tab_powerflow:
        st.markdown('<div class="section-head">Transmission power flow & conductor clearance</div>', unsafe_allow_html=True)
        st.markdown('<div class="section-subhead">Fast DC power flow solution ([P] = [B][&theta;]) across Raipur\'s 6-bus transmission network paired with IEEE Std 738-2012 dynamic line rating (DTR) and catenary conductor sag calculations.</div>', unsafe_allow_html=True)

        pf_engine = DCPowerFlowEngine()

        c_pf1, c_pf2 = st.columns([2, 1])
    with c_pf1:
        line_choices = ["None"] + [f"{ln['line_id']}: {ln['name']}" for ln in pf_engine.lines]
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
            status="critical" if max_flow_pct >= 100 else "warning" if max_flow_pct >= 85 else "ok",
            tile_variant="heat"
        )
        render_metric_card(
            pk2, "Overloaded corridors", f"{overloaded_count}", "lines",
            caption="Exceeding thermal ampacity",
            status="critical" if overloaded_count > 0 else "ok",
            tile_variant="heat"
        )
        render_metric_card(
            pk3, "Average thermal derating", f"-{avg_derating:.1f}", "%",
            caption=f"At {T_peak:.1f}°C ambient",
            status="warning",
            tile_variant="gold"
        )
        render_metric_card(
            pk4, "Sag clearance alerts", f"{crit_sag}", "spans",
            caption="Ground clearance below limit",
            status="critical" if crit_sag > 0 else "ok",
            tile_variant="grid"
        )

        st.markdown('<div class="section-head">Transmission corridor loading: Normal vs. Post-contingency</div>', unsafe_allow_html=True)
        flow_comp_rows = []
        for line_item in pf_engine.lines:
            lid = line_item["line_id"]
            short_name = line_item["name"].replace("Transmission Line", "").replace("Interconnector", "").strip()
            flow_comp_rows.append({
                "Line": f"{lid}: {short_name}",
                "Base loading (%)": base_pf["line_loadings_pct"].get(lid, 0.0),
                "Contingency loading (%)": contingency_pf["line_loadings_pct"].get(lid, 0.0),
                "Rating MW": line_item["rating_mw"],
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
            st.markdown('<div class="section-head">Bus voltage angles (&theta;)</div>', unsafe_allow_html=True)
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
            st.markdown('<div class="section-head">IEEE Std 738 DTR & conductor sag clearance</div>', unsafe_allow_html=True)
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


# ══════════════════════════════════════════════════════════════
# MODE 3: INTERVENTIONS, RESILIENCE & GOVERNANCE
# ══════════════════════════════════════════════════════════════
elif active_mode == "Mode 3: Interventions, Resilience & Governance":
    mode3_svg = get_svg_data_uri("mode3_resilience.svg")
    if mode3_svg:
        st.markdown(f'<img src="{mode3_svg}" style="width:100%;height:auto;border-radius:12px;margin-bottom:16px;border:1px solid rgba(255,255,255,0.08);box-shadow:0 8px 32px rgba(0,0,0,0.4);" />', unsafe_allow_html=True)

    sub_tab_dispatch, sub_tab_resilience, sub_tab_sobol, sub_tab_artifacts = st.tabs([
        "Deterministic Dispatch & HiGHS MILP",
        "Continuous System Resilience Q(t)",
        "Uncertainty & Sobol Global Sensitivity",
        "Official Artifacts Hub & Provenance"
    ])

    with sub_tab_dispatch:
        render_dispatch_view(T_peak, rel_humidity, budget_lakh)

    with sub_tab_resilience:
        render_resilience_view(T_peak, duration_days, tripped_id, budget_lakh)

    with sub_tab_sobol:
        render_montecarlo_view(T_peak, rel_humidity, duration_days)

    with sub_tab_artifacts:
        render_alerts_view(T_peak, rel_humidity, power_outage_sim, tripped_id)

        st.markdown("---")
        st.markdown('<div class="section-head">Statutory Data Provenance Matrix (187 Parameters Audited)</div>', unsafe_allow_html=True)
        st.markdown("""
| Terminology | Definition & Source Boundary | Application in AGNAYA | Statutory Authority |
| :--- | :--- | :--- | :--- |
| **OBSERVED** | Physical ground-truth measurements recorded by statutory monitoring networks. | IMD Station #42809 records (all-time peak 47.9°C on May 28, 2024); CSERC FY24-25 tariff filings. | India Meteorological Department (IMD) |
| **FORECAST** | Gridded numerical weather prediction (NWP) model outputs from Open-Meteo API. | Hourly temperature, humidity, and irradiance at 21.2514° N, 81.6296° E (30-min cache). NOT official IMD station telemetry. | Open-Meteo NWP (Gridded Model) |
| **USER HYPOTHETICAL** | What-if scenario parameters selected via sliders or test suites to evaluate stress limits. | Scenario sliders (38°C–50°C, outage duration, N-1 substation trip contingency). | User-selected stress scenario |
| **MODEL-CLASSIFIED** | Algorithmic risk tiers and stress indices computed by deterministic physics and engineering models. | Heuristic Heat-Risk Index (HSRI), IEEE Std C57.91 transformer thermal aging acceleration ($F_{AA}$). | Deterministic algorithms (Uncalibrated) |
| **OFFICIAL WARNING** | **NEVER PRODUCED BY THIS TOOL.** Statutory red/orange warnings, heatwave alerts, or evacuation directives. | Explicitly prohibited by core system rules. All outputs carry mandatory simulation disclaimers. | **IMD / NDMA / SEC / DDMA Exclusively** |
""")


# ══════════════════════════════════════════════════════════════
# FOOTER
# ══════════════════════════════════════════════════════════════
st.markdown("""
<div class="app-footer">
  <div>Data Grounding: CSERC Tariff Order FY 2024–25 &middot; CSPTCL Grid Records &middot; IMD Climatological Normals 1970–2024 &middot; Census of India 2011</div>
  <div>AGNAYA v3.2 &middot; Municipal &amp; Utility Decision-Support Prototype &middot; SIMULATION ONLY &ndash; NOT AN OFFICIAL WARNING</div>
</div>
""", unsafe_allow_html=True)
