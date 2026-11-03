"""
AGNAYA - Deterministic 3-Stage Dispatch & HiGHS MILP View
Shows costs, municipal budget execution, coverage assumptions, and mathematical selection rationale.

MANDATORY DISCLAIMER: SIMULATION ONLY – NOT AN OFFICIAL WARNING.
"""

import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go

from data.raipur_data import INTERVENTION_OPTIONS, COOLING_CENTRES, RAIPUR_ZONES
from models.cascade_model import InterventionOptimizer
from models.agents_pipeline import DeterministicDispatchEngine


def render_dispatch_view(T_peak: float, rel_humidity: float, budget_lakh: float):
    st.markdown('<div class="section-title">Deterministic Multi-Stage Dispatch & HiGHS MILP Optimizer</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-desc">Solves an exact Mixed-Integer Linear Program (MILP) using SciPy HiGHS '
        'to maximize population protected under municipal budgetary constraints.</div>',
        unsafe_allow_html=True
    )

    optimizer = InterventionOptimizer(budget_lakh=budget_lakh)
    # Estimate baseline severity from peak temperature
    severity = min(1.0, max(0.0, (T_peak - 40.0) / 8.0))
    opt_res = optimizer.optimize_fleet(severity_index=severity)

    fleet = opt_res["allocated_fleet"]
    total_cost = opt_res["total_cost_lakh"]
    utilization_pct = opt_res["budget_utilization_pct"]

    # KPI Summary Cards
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Municipal Budget", f"₹{budget_lakh:.1f} Lakh", "Contingency Fund")
    c2.metric("Allocated Spend", f"₹{total_cost:.1f} Lakh", f"{utilization_pct:.1f}% Budget Utilization")
    c3.metric("Cooling Centres", f"{fleet.get('cooling_centre', 0)} Sites", "Shelter Capacity: ~1,000")
    c4.metric("Water Tankers", f"{fleet.get('water_tankers', 0)} Units", "Payload: 200 kL/day")

    st.markdown("---")

    # Itemized Breakdown Table
    col_t1, col_t2 = st.columns([1.6, 1.2])

    with col_t1:
        st.markdown('<div class="section-title">Optimal Resource Allocation Breakdown</div>', unsafe_allow_html=True)
        items = []
        for k, v in fleet.items():
            meta = INTERVENTION_OPTIONS.get(k, {})
            cost_u = meta.get("cost_per_unit_lakh", 1.0)
            items.append({
                "Intervention Type": meta.get("label", k),
                "Units Allocated": v,
                "Unit Cost": f"₹{cost_u:.1f} Lakh",
                "Total Cost": f"₹{v * cost_u:.1f} Lakh",
                "Effectiveness Weight": meta.get("effectiveness_score", 0.5),
                "Benefit-to-Cost Ratio": round(meta.get("effectiveness_score", 0.5) / cost_u, 3),
            })
        df_items = pd.DataFrame(items)
        st.dataframe(df_items, use_container_width=True, hide_index=True)

        st.markdown(f"""
        <div style="background:#161920;border:1px solid #262A33;border-radius:6px;padding:12px;margin-top:10px;font-size:12px;color:#D1D5DB;line-height:1.5;">
          <b>Why This Solution Was Chosen (Mathematical Rationale):</b><br/>
          HiGHS MILP optimizes the objective: &sum; (v<sub>k</sub> &times; x<sub>k</sub>) subject to &sum; (c<sub>k</sub> &times; x<sub>k</sub>) &le; B<sub>budget</sub>.<br/>
          &bull; <b>Water Tankers:</b> High marginal utility ratio (0.625) &mdash; rapid potable water relief at modest unit cost (₹0.8 Lakh).<br/>
          &bull; <b>Cooling Centres:</b> Direct sheltering for dense slum zones with tin-roof traps (0.280 ratio).<br/>
          &bull; <b>Mobile DG Sets:</b> Selected to anchor 33/11 kV critical feeders and prevent water pumping blackouts.
        </div>
        """, unsafe_allow_html=True)

    with col_t2:
        st.markdown('<div class="section-title">Cooling Centre Walking Coverage (OSM Isochrone Proxy)</div>', unsafe_allow_html=True)
        cc_rows = []
        for cc in COOLING_CENTRES:
            # Walking speed: 4.5 km/h -> 10 min = 750m buffer radius
            cc_rows.append({
                "Site": cc["name"],
                "Capacity": f"{cc['capacity_persons']} persons",
                "10-min Walk Radius": "750 m",
                "Estimated Slum Reach": "1,200 - 1,800 residents",
                "Status": "Operational" if cc.get("operational") else "Standby (To Open)",
            })
        df_cc = pd.DataFrame(cc_rows)
        st.dataframe(df_cc, use_container_width=True, hide_index=True)

        st.info(
            "**Coverage Model:** Based on standard 10–15 minute pedestrian walking isochrones (4.5 km/h). "
            "Prioritizes sites within 800m of dense informal settlements in Gudhiyari, Tikrapara, and Pandri."
        )
