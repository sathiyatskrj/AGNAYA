"""
AGNAYA - 3D City Simulation & Causal Cascade Theatre (Mode 4)
OpenCityModel (CityJSON LOD1) Georeferenced Digital Twin of Raipur, Chhattisgarh.
Incorporates CityJSON geometries from https://github.com/opencitymodel/opencitymodel,
Smart City assets from https://github.com/AkshaySharmaDEV/Cycle4Change-SmartCityRaipur,
CSERC Tariff Order FY24-25 grid parameters, Kharun River 180 MLD water facilities,
and biometeorological heatwave cascade dynamics.

MANDATORY DISCLAIMER: SIMULATION ONLY – NOT AN OFFICIAL WARNING.
"""

import json
import base64
from pathlib import Path
import streamlit as st
import streamlit.components.v1 as components
from data.raipur_opencitymodel import get_raipur_opencitymodel
from data.smartcity_assets import get_smartcity_assets


def render_city_simulation_view(
    T_peak: float,
    rel_humidity: float,
    duration_days: int,
    budget_lakh: float,
    tripped_id: str | None = "S03 Amanaka"
):
    st.markdown('<div class="section-head">3D Raipur City Digital Twin & Causal Cascade Theatre</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-subhead">Georeferenced 3D digital twin of Raipur City built on the open '
        '<a href="https://github.com/opencitymodel/opencitymodel" target="_blank" style="color:#38BDF8;text-decoration:underline;">OpenCityModel (CityJSON LOD1)</a> '
        'standard and enriched with urban assets from <a href="https://github.com/AkshaySharmaDEV/Cycle4Change-SmartCityRaipur" target="_blank" style="color:#10B981;text-decoration:underline;">Raipur Smart City Limited (Cycles4Change)</a>. '
        'Simulates physical macroclimate propagation across 12 municipal planning zones, Ghadi Chowk, Telibandha Marine Drive, '
        'CSPTCL 220/132 kV substations, the Kharun River 180 MLD water treatment facility, and slum microclimates. '
        '<b>Simulation only &mdash; not an official warning.</b></div>',
        unsafe_allow_html=True
    )

    # Fetch verified OpenCityModel dataset for Raipur
    raipur_city_json = get_raipur_opencitymodel()
    city_json_str = json.dumps(raipur_city_json)

    # Fetch verified FBX 7.x assets from Cycle4Change-SmartCityRaipur
    smartcity_assets = get_smartcity_assets()
    smartcity_assets_json = json.dumps(smartcity_assets)

    # Load Raipur Smart City logo
    base_dir = Path(__file__).resolve().parent.parent.parent
    rscl_logo_path = base_dir / "assets" / "raipur_smart_city_logo.png"
    rscl_logo_b64 = ""
    if rscl_logo_path.exists():
        with open(rscl_logo_path, "rb") as f:
            rscl_logo_b64 = base64.b64encode(f.read()).decode("utf-8")

    # Top Control Bar (Camera & Playback Presets)
    c_mode, c_cam, c_spd, c_int = st.columns([2, 2, 1, 2])
    with c_mode:
        sim_stage = st.selectbox(
            "Simulation Act / Phase:",
            [
                "Act 1: Summer Onset & Normal Grid (38.0°C)",
                "Act 2: Heatwave Inversion & Load Surge (43.0°C)",
                "Act 3: Thermal Expansion & Conductor Sag (46.5°C)",
                "Act 4: Transformer Short-Circuit & Arc Flash (47.9°C)",
                "Act 5: Kharun Water Pump Outage & Slum Crisis",
                "Act 6: Emergency Tanker Dispatch & Q(t) Recovery"
            ],
            index=3
        )

    stage_to_hour = {
        "Act 1": 0.0,
        "Act 2": 24.0,
        "Act 3": 38.0,
        "Act 4": 48.0,
        "Act 5": 60.0,
        "Act 6": 72.0
    }
    initial_hour = 48.0
    for prefix, hr in stage_to_hour.items():
        if prefix in sim_stage:
            initial_hour = hr
            break

    with c_cam:
        cam_view = st.selectbox(
            "Cinematic Landmark Camera:",
            [
                "⚡ S03 Amanaka 132 kV Substation (Trip Site)",
                "🕰️ Ghadi Chowk (Raipur Clock Tower)",
                "🚴 Cycles4Change Smart Corridor (RSCL)",
                "🌊 Telibandha Marine Drive Lakefront",
                "💧 Kharun River 180 MLD Intake & Pumping Works",
                "🏚️ Tikrapara Informal Slum (Tin Roof Heat Trap)",
                "🏥 Dr. B.R. Ambedkar Memorial Hospital (Mekahara)",
                "🚁 Full Raipur Aerial Drone Orbit",
                "📐 Top-Down OpenCityModel Blueprint"
            ],
            index=0
        )
    with c_spd:
        st.selectbox("Playback Speed:", ["1x Real-Time", "2x Accelerated", "5x Hyper-lapse"], index=0)
    with c_int:
        st.checkbox("Deploy Municipal Relief Fleet (HiGHS MILP)", value=True)

    # Build the self-contained Three.js WebGL simulation HTML
    html_code = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8">
      <title>AGNAYA 3D Raipur OpenCityModel Simulation</title>
      <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
          background: #38BDF8;
          color: #E2E8F0;
          font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
          overflow: hidden;
          width: 100vw;
          height: 100vh;
          user-select: none;
        }}
        #canvas-container {{
          width: 100%;
          height: 100%;
          position: absolute;
          top: 0;
          left: 0;
        }}
        /* Glassmorphic HUD Header Overlay */
        .hud-header {{
          position: absolute;
          top: 14px;
          left: 14px;
          right: 14px;
          display: flex;
          justify-content: space-between;
          align-items: center;
          background: rgba(15, 23, 42, 0.88);
          backdrop-filter: blur(16px);
          border: 1px solid rgba(255, 255, 255, 0.15);
          border-radius: 10px;
          padding: 10px 20px;
          z-index: 100;
          box-shadow: 0 10px 30px rgba(0, 0, 0, 0.4);
          pointer-events: auto;
        }}
        .hud-title-lockup {{
          display: flex;
          align-items: center;
          gap: 12px;
        }}
        .rscl-logo-img {{
          width: 34px;
          height: 34px;
          border-radius: 6px;
          background: #FFFFFF;
          padding: 2px;
          object-fit: contain;
          box-shadow: 0 2px 8px rgba(0,0,0,0.25);
        }}
        .hud-badge {{
          font-size: 11px;
          font-weight: 800;
          letter-spacing: 0.08em;
          text-transform: uppercase;
          background: #EF4444;
          color: #FFFFFF;
          padding: 4px 10px;
          border-radius: 5px;
          box-shadow: 0 0 14px rgba(239, 68, 68, 0.6);
          animation: pulse-red 2s infinite;
        }}
        @keyframes pulse-red {{
          0%, 100% {{ opacity: 1; transform: scale(1); }}
          50% {{ opacity: 0.75; transform: scale(0.98); }}
        }}
        .hud-stats {{
          display: flex;
          gap: 24px;
          font-family: 'SF Mono', Monaco, monospace;
        }}
        .hud-stat-item {{
          display: flex;
          flex-direction: column;
          align-items: flex-end;
        }}
        .hud-stat-label {{
          font-size: 10px;
          color: #94A3B8;
          text-transform: uppercase;
          font-weight: 600;
          letter-spacing: 0.04em;
        }}
        .hud-stat-val {{
          font-size: 14px;
          font-weight: 800;
          letter-spacing: -0.02em;
        }}
        .hud-stat-val.crit {{ color: #EF4444; text-shadow: 0 0 10px rgba(239,68,68,0.4); }}
        .hud-stat-val.warn {{ color: #F59E0B; text-shadow: 0 0 10px rgba(245,158,11,0.4); }}
        .hud-stat-val.ok {{ color: #10B981; text-shadow: 0 0 10px rgba(16,185,129,0.4); }}
        .hud-stat-val.cyan {{ color: #38BDF8; text-shadow: 0 0 10px rgba(56,189,248,0.4); }}

        /* Floating Video Playback Transport Controls */
        .hud-transport {{
          position: absolute;
          bottom: 22px;
          left: 50%;
          transform: translateX(-50%);
          display: flex;
          align-items: center;
          gap: 16px;
          background: rgba(15, 23, 42, 0.92);
          backdrop-filter: blur(16px);
          border: 1px solid rgba(255, 255, 255, 0.16);
          border-radius: 36px;
          padding: 8px 26px;
          z-index: 100;
          box-shadow: 0 14px 40px rgba(0, 0, 0, 0.65);
        }}
        .transport-btn {{
          background: #1E293B;
          border: 1px solid rgba(255, 255, 255, 0.14);
          color: #F8FAFC;
          width: 40px;
          height: 40px;
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          cursor: pointer;
          transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
          font-size: 15px;
        }}
        .transport-btn:hover {{
          background: #3B82F6;
          border-color: #60A5FA;
          transform: scale(1.08);
          box-shadow: 0 0 16px rgba(59, 130, 246, 0.6);
        }}
        .transport-btn.active {{
          background: #EF4444;
          border-color: #F87171;
          box-shadow: 0 0 16px rgba(239, 68, 68, 0.6);
        }}
        .scrubber-container {{
          display: flex;
          flex-direction: column;
          gap: 4px;
          width: 290px;
        }}
        .scrubber-track {{
          position: relative;
          width: 100%;
          height: 7px;
          background: #334155;
          border-radius: 4px;
          cursor: pointer;
          overflow: hidden;
        }}
        .scrubber-fill {{
          height: 100%;
          width: 50%;
          background: linear-gradient(90deg, #38BDF8, #F59E0B, #EF4444);
          border-radius: 4px;
          box-shadow: 0 0 10px rgba(239, 68, 68, 0.6);
        }}
        .scrubber-labels {{
          display: flex;
          justify-content: space-between;
          font-size: 10px;
          color: #94A3B8;
          font-family: monospace;
          font-weight: 600;
        }}

        /* Live Event Log Ticker */
        .hud-ticker {{
          position: absolute;
          bottom: 24px;
          left: 18px;
          max-width: 380px;
          background: rgba(15, 23, 42, 0.94);
          backdrop-filter: blur(12px);
          border: 1px solid rgba(239, 68, 68, 0.45);
          border-radius: 8px;
          padding: 10px 14px;
          font-size: 11px;
          line-height: 1.45;
          z-index: 100;
          color: #E2E8F0;
          box-shadow: 0 8px 24px rgba(0, 0, 0, 0.5);
        }}
        .ticker-header {{
          color: #EF4444;
          font-weight: 800;
          font-size: 10.5px;
          text-transform: uppercase;
          margin-bottom: 4px;
          display: flex;
          align-items: center;
          gap: 8px;
          letter-spacing: 0.04em;
        }}
        .ticker-dot {{
          width: 7px;
          height: 7px;
          border-radius: 50%;
          background: #EF4444;
          box-shadow: 0 0 8px #EF4444;
          animation: pulse-red 1.2s infinite;
        }}

        /* Camera Mode Buttons */
        .hud-cam-pills {{
          position: absolute;
          top: 76px;
          right: 18px;
          display: flex;
          flex-direction: column;
          gap: 6px;
          z-index: 100;
        }}
        .cam-pill {{
          background: rgba(15, 23, 42, 0.88);
          backdrop-filter: blur(8px);
          border: 1px solid rgba(255, 255, 255, 0.12);
          color: #E2E8F0;
          padding: 6px 14px;
          border-radius: 6px;
          font-size: 11px;
          font-weight: 600;
          cursor: pointer;
          transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
          text-align: right;
        }}
        .cam-pill:hover, .cam-pill.active {{
          background: #3B82F6;
          color: #FFFFFF;
          border-color: #93C5FD;
          transform: translateX(-4px);
          box-shadow: 0 4px 14px rgba(59, 130, 246, 0.5);
        }}

        /* OpenCityModel Inspector Card (Interactive Click) */
        .inspector-card {{
          position: absolute;
          top: 76px;
          left: 18px;
          width: 300px;
          background: rgba(15, 23, 42, 0.95);
          backdrop-filter: blur(16px);
          border: 1px solid rgba(56, 189, 248, 0.45);
          border-radius: 10px;
          padding: 14px;
          font-size: 11px;
          z-index: 100;
          display: none;
          box-shadow: 0 12px 36px rgba(0, 0, 0, 0.6);
        }}
        .inspector-title {{
          color: #38BDF8;
          font-weight: 800;
          font-size: 12.5px;
          margin-bottom: 8px;
          border-bottom: 1px solid rgba(255, 255, 255, 0.1);
          padding-bottom: 6px;
        }}
        .inspector-row {{
          display: flex;
          justify-content: space-between;
          margin-bottom: 4px;
        }}
        .inspector-label {{ color: #94A3B8; font-weight: 500; }}
        .inspector-val {{ font-family: monospace; font-weight: 700; color: #F8FAFC; }}

        /* Legend */
        .hud-legend {{
          position: absolute;
          bottom: 24px;
          right: 18px;
          background: rgba(15, 23, 42, 0.9);
          backdrop-filter: blur(10px);
          border: 1px solid rgba(255, 255, 255, 0.12);
          border-radius: 8px;
          padding: 10px 14px;
          font-size: 10.5px;
          font-weight: 600;
          z-index: 100;
          display: flex;
          flex-direction: column;
          gap: 5px;
          box-shadow: 0 8px 24px rgba(0, 0, 0, 0.5);
        }}
        .legend-item {{
          display: flex;
          align-items: center;
          gap: 9px;
        }}
        .legend-color {{
          width: 12px;
          height: 12px;
          border-radius: 3px;
        }}
      </style>
      <!-- Three.js and Loaders from reliable CDNs -->
      <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
      <script src="https://cdn.jsdelivr.net/npm/fflate@0.7.4/umd/index.js"></script>
      <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/loaders/FBXLoader.js"></script>
      <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
    </head>
    <body>
      <div id="canvas-container"></div>

      <!-- Glassmorphic Top HUD -->
      <div class="hud-header">
        <div class="hud-title-lockup">
          {'<img class="rscl-logo-img" src="data:image/png;base64,' + rscl_logo_b64 + '" alt="RSCL" />' if rscl_logo_b64 else ''}
          <span class="hud-badge" id="hud-badge">STAGE 4 // S03 ARC FAULT</span>
          <div>
            <div style="font-weight: 800; font-size: 13.5px; letter-spacing: -0.01em;">RAIPUR SMART CITY 3D DIGITAL TWIN</div>
            <div style="font-size: 10.5px; color: #94A3B8;">RSCL &middot; Cycles4Change Urban Corridor &middot; OpenCityModel (CityJSON LOD1)</div>
          </div>
        </div>
        <div class="hud-stats">
          <div class="hud-stat-item">
            <span class="hud-stat-label">IMD Air Temp</span>
            <span class="hud-stat-val crit" id="val-temp">{T_peak:.1f}°C</span>
          </div>
          <div class="hud-stat-item">
            <span class="hud-stat-label">CSPDCL Demand</span>
            <span class="hud-stat-val crit" id="val-load">475.9 MW</span>
          </div>
          <div class="hud-stat-item">
            <span class="hud-stat-label">S03 Amanaka Hotspot</span>
            <span class="hud-stat-val crit" id="val-hotspot">134.8°C</span>
          </div>
          <div class="hud-stat-item">
            <span class="hud-stat-label">Kharun Pumping</span>
            <span class="hud-stat-val warn" id="val-water">90 / 180 MLD</span>
          </div>
          <div class="hud-stat-item">
            <span class="hud-stat-label">Relief Tankers</span>
            <span class="hud-stat-val cyan" id="val-tankers">20 Active</span>
          </div>
        </div>
      </div>

      <!-- Landmark Camera Selection -->
      <div class="hud-cam-pills">
        <div class="cam-pill" onclick="switchCam('s03')">⚡ S03 Amanaka 132 kV Substation</div>
        <div class="cam-pill" onclick="switchCam('ghadi')">🕰️ Ghadi Chowk (Clock Tower)</div>
        <div class="cam-pill" onclick="switchCam('cycle')">🚴 Cycles4Change Smart Track</div>
        <div class="cam-pill" onclick="switchCam('telibandha')">🌊 Telibandha Marine Drive</div>
        <div class="cam-pill" onclick="switchCam('kharun')">💧 Kharun 180 MLD Water Plant</div>
        <div class="cam-pill" onclick="switchCam('slum')">🏚️ Tikrapara Slum (Tin Heat Trap)</div>
        <div class="cam-pill" onclick="switchCam('hospital')">🏥 Ambedkar Memorial Hospital (Mekahara)</div>
        <div class="cam-pill" onclick="switchCam('drone')">🚁 Full Raipur Drone Flyover</div>
        <div class="cam-pill" onclick="switchCam('top')">📐 OpenCityModel Top-Down Blueprint</div>
      </div>

      <!-- OpenCityModel Asset Inspector Card -->
      <div class="inspector-card" id="inspector-card">
        <div class="inspector-title" id="insp-title">OpenCityModel Asset</div>
        <div class="inspector-row"><span class="inspector-label">Type:</span><span class="inspector-val" id="insp-type">Building (LOD1)</span></div>
        <div class="inspector-row"><span class="inspector-label">Class:</span><span class="inspector-val" id="insp-class">Infrastructure</span></div>
        <div class="inspector-row"><span class="inspector-label">Roof Material:</span><span class="inspector-val" id="insp-roof">Corrugated Tin</span></div>
        <div class="inspector-row"><span class="inspector-label">Thermal Penalty:</span><span class="inspector-val" id="insp-pen">+4.5°C</span></div>
        <div class="inspector-row"><span class="inspector-label">WGS84 Coordinates:</span><span class="inspector-val" id="insp-coords">21.2514° N, 81.6296° E</span></div>
        <div class="inspector-row"><span class="inspector-label">Civic Provenance:</span><span class="inspector-val" id="insp-prov" style="color:#10B981;font-size:10px;">Raipur Smart City (RSCL)</span></div>
      </div>

      <!-- Playback Transport Controller -->
      <div class="hud-transport">
        <button class="transport-btn" id="btn-play-pause" onclick="togglePlayPause()">⏸</button>
        <button class="transport-btn" onclick="resetSim()">↺</button>
        <div class="scrubber-container">
          <div class="scrubber-track" onclick="seekTimeline(event)">
            <div class="scrubber-fill" id="scrubber-fill"></div>
          </div>
          <div class="scrubber-labels">
            <span>00:00 (38°C)</span>
            <span id="label-curr-time">Hour {initial_hour:.1f}:00</span>
            <span>96:00 (Recovery)</span>
          </div>
        </div>
        <button class="transport-btn" id="btn-speed" onclick="cycleSpeed()" style="font-size:12px;font-weight:800;">1x</button>
      </div>

      <!-- Live Event Ticker -->
      <div class="hud-ticker">
        <div class="ticker-header">
          <span class="ticker-dot"></span>
          <span id="ticker-time">14:32 IST // CASCADING INFRASTRUCTURE CRISIS</span>
        </div>
        <div id="ticker-text">
          S03 Amanaka 132/33 kV Substation transformer winding reached 134.8°C (Arrhenius aging rate 18.2x). Flashover electrical arc triggered differential relay trip! Kharun River WP02 lost feeder power. Tikrapara slum water pressure collapsed.
        </div>
      </div>

      <!-- Legend -->
      <div class="hud-legend">
        <div class="legend-item"><div class="legend-color" style="background:#10B981;"></div><span>Cycles4Change Green Bike Track (RSCL)</span></div>
        <div class="legend-item"><div class="legend-color" style="background:#F59E0B;"></div><span>Ghadi Chowk Clock Tower & Heritage Plaza</span></div>
        <div class="legend-item"><div class="legend-color" style="background:#06B6D4;"></div><span>Kharun River 180 MLD Intake & Mains</span></div>
        <div class="legend-item"><div class="legend-color" style="background:#0284C7;"></div><span>Telibandha Talab & Lake Fountain (Marine Drive)</span></div>
        <div class="legend-item"><div class="legend-color" style="background:#38BDF8;"></div><span>CSPTCL 220/132 kV Transmission Grid</span></div>
        <div class="legend-item"><div class="legend-color" style="background:#EF4444;"></div><span>S03 Arc Fault & Tripped Substation</span></div>
        <div class="legend-item"><div class="legend-color" style="background:#E2E8F0;"></div><span>Urban Pucca & High-Rise Districts</span></div>
        <div class="legend-item"><div class="legend-color" style="background:#B45309;"></div><span>Tikrapara Slum Dwellings (Tin Roof Trap)</span></div>
        <div class="legend-item"><div class="legend-color" style="background:#22C55E;"></div><span>Parks, Tree Canopies & Urban Forestry</span></div>
      </div>

      <!-- Ingest OpenCityModel CityJSON & Run Three.js Engine -->
      <script>
        window.onerror = function(msg, url, lineNo, columnNo, error) {{
          console.error("ThreeJS Simulation Error:", msg, lineNo, error);
        }};

        const RAIPUR_CITY_JSON = {city_json_str};
        const SMARTCITY_ASSETS = {smartcity_assets_json};

        let isPlaying = true;
        let simSpeed = 1.0;
        let simTimeHours = {initial_hour};
        const maxTimeHours = 96.0;

        // Container & WebGL Renderer with Game HDR Tonemapping
        const container = document.getElementById('canvas-container');
        const scene = new THREE.Scene();

        // Atmospheric Sky Colors
        const skyPalette = {{
          day: new THREE.Color(0x38bdf8),     // Radiant Sunny Blue Sky
          warm: new THREE.Color(0xfb923c),    // Golden Hour Warmth
          heat: new THREE.Color(0xf97316),    // Scorching Indian Summer Heat Dome (Vivid Amber)
          crisis: new THREE.Color(0xef4444)   // Severe Heatwave Inversion
        }};
        scene.background = skyPalette.day.clone();
        scene.fog = new THREE.FogExp2(0xdbeafe, 0.0016);

        const camera = new THREE.PerspectiveCamera(46, window.innerWidth / window.innerHeight, 1, 3500);
        camera.position.set(-65, 55, 195);

        const renderer = new THREE.WebGLRenderer({{ antialias: true, alpha: false, powerPreference: 'high-performance' }});
        renderer.setSize(window.innerWidth, window.innerHeight);
        renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
        renderer.shadowMap.enabled = true;
        renderer.shadowMap.type = THREE.PCFSoftShadowMap;
        renderer.toneMapping = THREE.ACESFilmicToneMapping;
        renderer.toneMappingExposure = 1.35;
        container.appendChild(renderer.domElement);

        // Defensive OrbitControls Initialization
        let controls;
        if (typeof THREE.OrbitControls === 'function') {{
          controls = new THREE.OrbitControls(camera, renderer.domElement);
          controls.enableDamping = true;
          controls.dampingFactor = 0.05;
          controls.maxPolarAngle = Math.PI / 2 - 0.03;
          controls.minDistance = 15;
          controls.maxDistance = 750;
          controls.target.set(0, 5, 0);
        }} else {{
          controls = {{
            target: new THREE.Vector3(0, 5, 0),
            update: function() {{}},
            dispose: function() {{}}
          }};
        }}

        // Game-like Outdoor Dual Lighting
        const hemiLight = new THREE.HemisphereLight(0xbae6fd, 0x86efac, 1.45);
        scene.add(hemiLight);

        const sunLight = new THREE.DirectionalLight(0xfffbeb, 2.3);
        sunLight.position.set(180, 260, 140);
        sunLight.castShadow = true;
        sunLight.shadow.mapSize.width = 2048;
        sunLight.shadow.mapSize.height = 2048;
        sunLight.shadow.camera.near = 10;
        sunLight.shadow.camera.far = 800;
        sunLight.shadow.camera.left = -320;
        sunLight.shadow.camera.right = 320;
        sunLight.shadow.camera.top = 320;
        sunLight.shadow.camera.bottom = -320;
        scene.add(sunLight);

        // Visual Heat Dome Sun Sphere with Radiant Corona
        const sunGeo = new THREE.SphereGeometry(26, 32, 32);
        const sunMat = new THREE.MeshBasicMaterial({{ color: 0xffedd5 }});
        const sunMesh = new THREE.Mesh(sunGeo, sunMat);
        sunMesh.position.set(280, 320, 200);
        scene.add(sunMesh);

        const coronaGeo = new THREE.SphereGeometry(36, 32, 32);
        const coronaMat = new THREE.MeshBasicMaterial({{ color: 0xf59e0b, transparent: true, opacity: 0.35 }});
        const coronaMesh = new THREE.Mesh(coronaGeo, coronaMat);
        sunMesh.add(coronaMesh);

        // ═════════════════════════════════════════════════════════════════════
        // LUSH TERRAIN, PARKS, ROADS & URBAN SECTORS
        // ═════════════════════════════════════════════════════════════════════

        // 1. Vibrant Green Park Landscape
        const groundGeo = new THREE.PlaneGeometry(1200, 1200, 32, 32);
        const groundMat = new THREE.MeshStandardMaterial({{
          color: 0x4ade80, // Lush Grass Green
          roughness: 0.85,
          metalness: 0.05
        }});
        const ground = new THREE.Mesh(groundGeo, groundMat);
        ground.rotation.x = -Math.PI / 2;
        ground.receiveShadow = true;
        scene.add(ground);

        // 2. Concrete Urban Core Plazas (Under commercial & residential blocks)
        const plazaGeo = new THREE.PlaneGeometry(440, 340);
        const plazaMat = new THREE.MeshStandardMaterial({{ color: 0xe2e8f0, roughness: 0.92 }});
        const plaza = new THREE.Mesh(plazaGeo, plazaMat);
        plaza.rotation.x = -Math.PI / 2;
        plaza.position.set(20, 0.06, 10);
        plaza.receiveShadow = true;
        scene.add(plaza);

        // 3. Sandy River Embankment along Kharun
        const bankGeo = new THREE.PlaneGeometry(90, 560);
        const bankMat = new THREE.MeshStandardMaterial({{ color: 0xfde68a, roughness: 0.95 }}); // Sandstone beige
        const bank = new THREE.Mesh(bankGeo, bankMat);
        bank.rotation.x = -Math.PI / 2;
        bank.position.set(-210, 0.08, 20);
        scene.add(bank);

        // 4. Great Eastern Road (GE Road / NH-53): Asphalt arterial highway
        const geRoadCurve = new THREE.CatmullRomCurve3([
          new THREE.Vector3(-220, 0.12, -30), // Tatibandh / AIIMS
          new THREE.Vector3(-95, 0.12, 30),   // Amanaka
          new THREE.Vector3(0, 0.12, 0),      // Ghadi Chowk / Jaistambh Chowk
          new THREE.Vector3(120, 0.12, 45),   // Pandri
          new THREE.Vector3(180, 0.12, 70)    // Telibandha Marine Drive
        ]);
        // Paved Concrete Sidewalk Curb alongside Great Eastern Road
        const sidewalkGeo = new THREE.TubeGeometry(geRoadCurve, 64, 6.4, 4, false);
        const sidewalkMat = new THREE.MeshStandardMaterial({{ color: 0xcbd5e1, roughness: 0.85 }});
        const sidewalkMesh = new THREE.Mesh(sidewalkGeo, sidewalkMat);
        sidewalkMesh.scale.set(1, 0.04, 1);
        sidewalkMesh.receiveShadow = true;
        scene.add(sidewalkMesh);

        const geRoadGeo = new THREE.TubeGeometry(geRoadCurve, 64, 5.0, 4, false);
        const geRoadMat = new THREE.MeshStandardMaterial({{ color: 0x1e293b, roughness: 0.75 }});
        const geRoadMesh = new THREE.Mesh(geRoadGeo, geRoadMat);
        geRoadMesh.scale.set(1, 0.05, 1);
        geRoadMesh.receiveShadow = true;
        scene.add(geRoadMesh);

        // Road White Center Striping
        const stripeGeo = new THREE.TubeGeometry(geRoadCurve, 64, 0.4, 4, false);
        const stripeMat = new THREE.MeshBasicMaterial({{ color: 0xffffff }});
        const stripeMesh = new THREE.Mesh(stripeGeo, stripeMat);
        stripeMesh.scale.set(1, 0.06, 1);
        scene.add(stripeMesh);

        // 5. CYCLES4CHANGE EMERALD GREEN TRACK (Raipur Smart City Limited)
        const cycleTrackCurve = new THREE.CatmullRomCurve3([
          new THREE.Vector3(-215, 0.20, -25),
          new THREE.Vector3(-92, 0.20, 35),
          new THREE.Vector3(0, 0.20, 5),
          new THREE.Vector3(122, 0.20, 50),
          new THREE.Vector3(175, 0.20, 75)
        ]);
        const cycleTrackGeo = new THREE.TubeGeometry(cycleTrackCurve, 64, 2.0, 4, false);
        const cycleTrackMat = new THREE.MeshStandardMaterial({{
          color: 0x10b981, // Vibrant Emerald Green Track
          roughness: 0.35,
          metalness: 0.25
        }});
        const cycleTrackMesh = new THREE.Mesh(cycleTrackGeo, cycleTrackMat);
        cycleTrackMesh.scale.set(1, 0.07, 1);
        scene.add(cycleTrackMesh);

        // 6. Kharun River: Sparkling Crystalline Cyan Water
        const kharunCurve = new THREE.CatmullRomCurve3([
          new THREE.Vector3(-240, 0.18, -220),
          new THREE.Vector3(-210, 0.18, -130),
          new THREE.Vector3(-180, 0.18, -30),
          new THREE.Vector3(-195, 0.18, 60),
          new THREE.Vector3(-230, 0.18, 180),
          new THREE.Vector3(-260, 0.18, 270)
        ]);
        const kharunGeo = new THREE.TubeGeometry(kharunCurve, 80, 20, 8, false);
        const kharunMat = new THREE.MeshStandardMaterial({{
          color: 0x06b6d4, // Tropical Cyan Water
          roughness: 0.12,
          metalness: 0.85,
          transparent: true,
          opacity: 0.92
        }});
        const kharunMesh = new THREE.Mesh(kharunGeo, kharunMat);
        kharunMesh.scale.set(1, 0.05, 1);
        scene.add(kharunMesh);

        // 7. Telibandha Talab (Marine Drive Lake): Deep Sapphire Blue with Waterfront
        const lakeGeo = new THREE.CylinderGeometry(30, 30, 0.4, 32);
        const lakeMat = new THREE.MeshStandardMaterial({{
          color: 0x0284c7, // Sapphire Lake Water
          roughness: 0.08,
          metalness: 0.9,
          transparent: true,
          opacity: 0.94
        }});
        const lakeMesh = new THREE.Mesh(lakeGeo, lakeMat);
        lakeMesh.position.set(165, 0.14, 72);
        scene.add(lakeMesh);

        // Promenade around Telibandha Lake
        const lakeRingGeo = new THREE.RingGeometry(30, 35, 32);
        const lakeRingMat = new THREE.MeshStandardMaterial({{ color: 0xe2e8f0, roughness: 0.8 }});
        const lakeRing = new THREE.Mesh(lakeRingGeo, lakeRingMat);
        lakeRing.rotation.x = -Math.PI / 2;
        lakeRing.position.set(165, 0.18, 72);
        scene.add(lakeRing);

        // "MOR RAIPUR" 3D Lakefront Civic Sign
        const signGroup = new THREE.Group();
        const signMatGreen = new THREE.MeshStandardMaterial({{ color: 0x10b981 }});
        const signMatOrange = new THREE.MeshStandardMaterial({{ color: 0xf97316 }});
        for (let i = 0; i < 9; i++) {{
          const letterGeo = new THREE.BoxGeometry(1.4, 2.6, 0.6);
          const lMesh = new THREE.Mesh(letterGeo, i % 2 === 0 ? signMatGreen : signMatOrange);
          lMesh.position.set(145 + i * 2.2, 1.4, 40);
          signGroup.add(lMesh);
        }}
        scene.add(signGroup);

        // Animated Lake Center Fountain
        const fountainGeo = new THREE.CylinderGeometry(1.0, 1.8, 2.2, 12);
        const fountainMat = new THREE.MeshStandardMaterial({{ color: 0xf8fafc, roughness: 0.3 }});
        const fountainMesh = new THREE.Mesh(fountainGeo, fountainMat);
        fountainMesh.position.set(165, 1.1, 72);
        scene.add(fountainMesh);

        const sprayCount = 70;
        const sprayGeo = new THREE.BufferGeometry();
        const sprayPos = new Float32Array(sprayCount * 3);
        const sprayVels = [];
        for (let i = 0; i < sprayCount; i++) {{
          sprayPos[i * 3] = 165;
          sprayPos[i * 3 + 1] = 2.2;
          sprayPos[i * 3 + 2] = 72;
          sprayVels.push({{
            x: (Math.random() - 0.5) * 5,
            y: Math.random() * 9 + 4,
            z: (Math.random() - 0.5) * 5
          }});
        }}
        sprayGeo.setAttribute('position', new THREE.BufferAttribute(sprayPos, 3));
        const sprayMat = new THREE.PointsMaterial({{ color: 0xe0f2fe, size: 1.4, transparent: true, opacity: 0.9 }});
        const sprayParticles = new THREE.Points(sprayGeo, sprayMat);
        scene.add(sprayParticles);

        // ═════════════════════════════════════════════════════════════════════
        // PROCEDURAL 3D TREES & URBAN FORESTRY (Over 70 Lush Trees)
        // ═════════════════════════════════════════════════════════════════════
        const treeGroup = new THREE.Group();
        const trunkGeo = new THREE.CylinderGeometry(0.35, 0.55, 3.0, 6);
        const trunkMat = new THREE.MeshStandardMaterial({{ color: 0x78350f, roughness: 0.9 }});
        const leafGeos = [
          new THREE.DodecahedronGeometry(2.2),
          new THREE.DodecahedronGeometry(1.6),
          new THREE.DodecahedronGeometry(1.2)
        ];
        const leafColors = [0x22c55e, 0x16a34a, 0x84cc16, 0x15803d, 0x4ade80];

        function createTree(x, z, scale = 1.0) {{
          const t = new THREE.Group();
          const trunk = new THREE.Mesh(trunkGeo, trunkMat);
          trunk.position.y = 1.5 * scale;
          trunk.scale.set(scale, scale, scale);
          trunk.castShadow = true;
          t.add(trunk);

          const lColor = leafColors[Math.floor(Math.random() * leafColors.length)];
          const lMat = new THREE.MeshStandardMaterial({{ color: lColor, roughness: 0.65 }});
          const f1 = new THREE.Mesh(leafGeos[0], lMat);
          f1.position.y = 3.4 * scale;
          f1.scale.set(scale, scale * 1.15, scale);
          f1.castShadow = true;
          t.add(f1);

          const f2 = new THREE.Mesh(leafGeos[1], lMat);
          f2.position.set(0.3 * scale, 4.6 * scale, -0.3 * scale);
          f2.scale.set(scale, scale, scale);
          f2.castShadow = true;
          t.add(f2);

          t.position.set(x, 0, z);
          return t;
        }}

        // Avenues along GE Road
        for (let i = -190; i <= 160; i += 24) {{
          treeGroup.add(createTree(i, -16 + (Math.random() - 0.5) * 6, 0.9 + Math.random() * 0.35));
          treeGroup.add(createTree(i + 12, 22 + (Math.random() - 0.5) * 6, 0.9 + Math.random() * 0.35));
        }}
        // Trees around Telibandha Marine Drive Lake
        for (let a = 0; a < Math.PI * 2; a += 0.38) {{
          const tx = 165 + Math.cos(a) * 36;
          const tz = 72 + Math.sin(a) * 36;
          treeGroup.add(createTree(tx, tz, 1.15));
        }}
        // Civil Lines Park Cluster
        for (let j = 0; j < 14; j++) {{
          const px = -30 + Math.random() * 50;
          const pz = -60 + Math.random() * 40;
          treeGroup.add(createTree(px, pz, 1.0 + Math.random() * 0.4));
        }}
        scene.add(treeGroup);

        // ═════════════════════════════════════════════════════════════════════
        // PROCEDURAL ARCHITECTURAL FACADE GENERATORS (Game-Engine Quality)
        // ═════════════════════════════════════════════════════════════════════
        function createCommercialFacade(primaryColor, windowColor, isGlassTower = false) {{
          const c = document.createElement('canvas');
          c.width = 512;
          c.height = 512;
          const ctx = c.getContext('2d');
          ctx.fillStyle = primaryColor;
          ctx.fillRect(0, 0, 512, 512);

          const floors = 8;
          const cols = 6;
          const floorH = 512 / floors;
          const colW = 512 / cols;

          if (isGlassTower) {{
            for (let f = 0; f < floors; f++) {{
              for (let cl = 0; cl < cols; cl++) {{
                const x = cl * colW;
                const y = f * floorH;
                ctx.fillStyle = (f + cl) % 4 === 0 ? '#60a5fa' : (f + cl) % 5 === 0 ? '#93c5fd' : '#1e3a8a';
                ctx.fillRect(x + 2, y + 2, colW - 4, floorH - 4);
                ctx.fillStyle = 'rgba(255, 255, 255, 0.25)';
                ctx.beginPath();
                ctx.moveTo(x + 2, y + 2);
                ctx.lineTo(x + colW * 0.7, y + 2);
                ctx.lineTo(x + 2, y + floorH * 0.7);
                ctx.closePath();
                ctx.fill();
              }}
            }}
            ctx.strokeStyle = '#cbd5e1';
            ctx.lineWidth = 3;
            for (let f = 0; f <= floors; f++) {{
              ctx.beginPath(); ctx.moveTo(0, f * floorH); ctx.lineTo(512, f * floorH); ctx.stroke();
            }}
            for (let cl = 0; cl <= cols; cl++) {{
              ctx.beginPath(); ctx.moveTo(cl * colW, 0); ctx.lineTo(cl * colW, 512); ctx.stroke();
            }}
          }} else {{
            for (let f = 0; f < floors; f++) {{
              const y = f * floorH;
              ctx.fillStyle = 'rgba(0, 0, 0, 0.16)';
              ctx.fillRect(0, y + floorH - 3, 512, 3);

              for (let cl = 0; cl < cols; cl++) {{
                const x = cl * colW;
                const wx = x + colW * 0.16;
                const wy = y + floorH * 0.18;
                const ww = colW * 0.68;
                const wh = floorH * 0.64;

                if (f === floors - 1) {{
                  // Ground floor store awning & illuminated entrance
                  ctx.fillStyle = cl % 2 === 0 ? '#ef4444' : '#f59e0b';
                  ctx.fillRect(x + 3, y + 2, colW - 6, floorH * 0.38);
                  ctx.fillStyle = '#0f172a';
                  ctx.fillRect(x + 5, y + floorH * 0.40, colW - 10, floorH * 0.58);
                  ctx.fillStyle = 'rgba(254, 240, 138, 0.55)';
                  ctx.fillRect(x + 8, y + floorH * 0.48, colW - 16, floorH * 0.44);
                }} else {{
                  // Upper floor punched windows with frames & sills
                  ctx.fillStyle = '#1e293b';
                  ctx.fillRect(wx - 2, wy - 2, ww + 4, wh + 4);
                  const isLit = (f * 3 + cl * 2) % 4 === 0;
                  ctx.fillStyle = isLit ? '#fef08a' : windowColor;
                  ctx.fillRect(wx, wy, ww, wh);

                  ctx.fillStyle = 'rgba(255, 255, 255, 0.35)';
                  ctx.beginPath();
                  ctx.moveTo(wx, wy);
                  ctx.lineTo(wx + ww * 0.6, wy);
                  ctx.lineTo(wx, wy + wh * 0.8);
                  ctx.closePath();
                  ctx.fill();

                  ctx.fillStyle = 'rgba(255, 255, 255, 0.5)';
                  ctx.fillRect(wx - 3, wy + wh, ww + 6, 3);
                }}
              }}
            }}
          }}

          const tex = new THREE.CanvasTexture(c);
          tex.wrapS = THREE.RepeatWrapping;
          tex.wrapT = THREE.RepeatWrapping;
          return tex;
        }}

        function createHospitalTexture() {{
          const c = document.createElement('canvas');
          c.width = 512;
          c.height = 512;
          const ctx = c.getContext('2d');
          ctx.fillStyle = '#f8fafc';
          ctx.fillRect(0, 0, 512, 512);

          const floors = 6;
          const floorH = 512 / floors;
          for (let f = 0; f < floors; f++) {{
            const y = f * floorH;
            ctx.fillStyle = '#0284c7';
            ctx.fillRect(0, y + floorH * 0.28, 512, floorH * 0.44);
            ctx.fillStyle = '#0f172a';
            for (let x = 0; x < 512; x += 32) {{
              ctx.fillRect(x, y + floorH * 0.28, 3, floorH * 0.44);
            }}
          }}

          // Red Cross Emblem
          ctx.fillStyle = '#ef4444';
          ctx.fillRect(18, 12, 36, 12);
          ctx.fillRect(30, 0, 12, 36);

          const tex = new THREE.CanvasTexture(c);
          tex.wrapS = THREE.RepeatWrapping;
          tex.wrapT = THREE.RepeatWrapping;
          return tex;
        }}

        function createSubstationTexture() {{
          const c = document.createElement('canvas');
          c.width = 512;
          c.height = 512;
          const ctx = c.getContext('2d');
          ctx.fillStyle = '#475569';
          ctx.fillRect(0, 0, 512, 512);

          ctx.strokeStyle = '#334155';
          ctx.lineWidth = 4;
          for (let x = 0; x < 512; x += 16) {{
            ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, 512); ctx.stroke();
          }}

          // Yellow/Black Hazard Stripes
          ctx.fillStyle = '#facc15';
          ctx.fillRect(0, 230, 512, 52);
          ctx.fillStyle = '#0f172a';
          for (let x = -50; x < 550; x += 40) {{
            ctx.beginPath();
            ctx.moveTo(x, 230);
            ctx.lineTo(x + 20, 230);
            ctx.lineTo(x - 10, 282);
            ctx.lineTo(x - 30, 282);
            ctx.closePath();
            ctx.fill();
          }}

          const tex = new THREE.CanvasTexture(c);
          tex.wrapS = THREE.RepeatWrapping;
          tex.wrapT = THREE.RepeatWrapping;
          return tex;
        }}

        function createSlumRoofTexture() {{
          const c = document.createElement('canvas');
          c.width = 512;
          c.height = 512;
          const ctx = c.getContext('2d');
          ctx.fillStyle = '#94a3b8';
          ctx.fillRect(0, 0, 512, 512);

          for (let x = 0; x < 512; x += 12) {{
            ctx.fillStyle = x % 24 === 0 ? '#cbd5e1' : '#64748b';
            ctx.fillRect(x, 0, 6, 512);
          }}
          ctx.fillStyle = 'rgba(180, 83, 9, 0.45)';
          ctx.fillRect(40, 100, 120, 180);
          ctx.fillRect(260, 220, 180, 140);
          ctx.fillRect(100, 360, 160, 100);

          const tex = new THREE.CanvasTexture(c);
          tex.wrapS = THREE.RepeatWrapping;
          tex.wrapT = THREE.RepeatWrapping;
          return tex;
        }}

        const texFacadeSandstone = createCommercialFacade('#fef3c7', '#0284c7', false);
        const texFacadeGlass = createCommercialFacade('#ffffff', '#38bdf8', true);
        const texFacadeSaffron = createCommercialFacade('#fed7aa', '#1e293b', false);
        const texFacadeCoral = createCommercialFacade('#fce7f3', '#0369a1', false);
        const texFacadeMint = createCommercialFacade('#dcfce7', '#15803d', false);
        const texFacadeHospital = createHospitalTexture();
        const texFacadeSubstation = createSubstationTexture();
        const texSlumRoof = createSlumRoofTexture();

        const facadePool = [texFacadeSandstone, texFacadeGlass, texFacadeSaffron, texFacadeCoral, texFacadeMint];

        // ═════════════════════════════════════════════════════════════════════
        // VIBRANT GAME-QUALITY ARCHITECTURAL BUILDINGS (Stepped Massing)
        // ═════════════════════════════════════════════════════════════════════
        const cityObjectsGroup = new THREE.Group();
        const tinRoofsList = [];
        const interactiveBuildings = [];
        const windowMeshesList = [];
        const substationPositions = {{}};

        // Common Rooftop Assets
        const tankGeo = new THREE.CylinderGeometry(0.8, 0.8, 1.8, 10);
        const tankMat = new THREE.MeshStandardMaterial({{ color: 0x0f172a, roughness: 0.7 }});
        const solarGeo = new THREE.PlaneGeometry(3.2, 2.0);
        const solarMat = new THREE.MeshStandardMaterial({{ color: 0x1d4ed8, roughness: 0.2, metalness: 0.9 }});
        solarGeo.rotateX(-Math.PI / 3);

        let buildingIdx = 0;
        Object.entries(RAIPUR_CITY_JSON.CityObjects).forEach(([objId, objData]) => {{
          const attrs = objData.attributes;
          const [cx, cy, cz] = objData.center;
          const [w, h, d] = objData.dimensions;

          const bGroup = new THREE.Group();
          bGroup.position.set(cx, 0, cz);

          let bTex = facadePool[buildingIdx % facadePool.length];
          buildingIdx++;

          if (attrs.class === 'Hospital') bTex = texFacadeHospital;
          else if (attrs.class === 'ElectricalSubstation') bTex = texFacadeSubstation;
          else if (attrs.class === 'WaterTreatmentPlant') bTex = texFacadeGlass;

          // 1. Ground Floor Commercial Storefront / Plinth
          const plinthH = Math.min(3.5, h * 0.28);
          const plinthGeo = new THREE.BoxGeometry(w * 1.04, plinthH, d * 1.04);
          const plinthMat = new THREE.MeshStandardMaterial({{ color: 0x334155, roughness: 0.6 }});
          const plinthMesh = new THREE.Mesh(plinthGeo, plinthMat);
          plinthMesh.position.y = plinthH / 2;
          plinthMesh.castShadow = true;
          plinthMesh.receiveShadow = true;
          bGroup.add(plinthMesh);

          // 2. Main Architectural Tower Body with Repeating Window Grid
          const towerH = h - plinthH;
          const towerGeo = new THREE.BoxGeometry(w, towerH, d);
          const customTex = bTex.clone();
          customTex.needsUpdate = true;
          customTex.wrapS = THREE.RepeatWrapping;
          customTex.wrapT = THREE.RepeatWrapping;
          customTex.repeat.set(Math.max(1, Math.round(w / 4)), Math.max(1, Math.round(towerH / 3)));

          const towerMat = new THREE.MeshStandardMaterial({{
            map: customTex,
            roughness: 0.35,
            metalness: 0.25
          }});
          const towerMesh = new THREE.Mesh(towerGeo, towerMat);
          towerMesh.position.y = plinthH + towerH / 2;
          towerMesh.castShadow = true;
          towerMesh.receiveShadow = true;
          towerMesh.userData = {{ id: objId, attrs: attrs }};
          bGroup.add(towerMesh);
          interactiveBuildings.push(towerMesh);

          // 3. Architectural Roof Parapet Rim
          const parapetGeo = new THREE.BoxGeometry(w * 1.02, 0.8, d * 1.02);
          const parapetMat = new THREE.MeshStandardMaterial({{ color: 0xe2e8f0, roughness: 0.8 }});
          const parapet = new THREE.Mesh(parapetGeo, parapetMat);
          parapet.position.y = h + 0.4;
          bGroup.add(parapet);

          // 4. Rooftop Mechanical Penthouse / Elevator Shaft
          if (w > 8 && d > 8) {{
            const pentGeo = new THREE.BoxGeometry(w * 0.35, 3.2, d * 0.35);
            const pentMat = new THREE.MeshStandardMaterial({{ color: 0x64748b, roughness: 0.7 }});
            const pent = new THREE.Mesh(pentGeo, pentMat);
            pent.position.set(0, h + 1.6, 0);
            bGroup.add(pent);
          }}

          // 5. Rooftop Sintex Tanks & Solar PV & Antennas
          if (w > 12 && d > 10 && attrs.class === 'ResidentialCommercial') {{
            const tank = new THREE.Mesh(tankGeo, tankMat);
            tank.position.set(-w * 0.25, h + 1.0, -d * 0.25);
            bGroup.add(tank);

            const solar = new THREE.Mesh(solarGeo, solarMat);
            solar.position.set(w * 0.2, h + 1.2, d * 0.2);
            bGroup.add(solar);

            const antGeo = new THREE.CylinderGeometry(0.08, 0.12, 6.0, 6);
            const antMat = new THREE.MeshStandardMaterial({{ color: 0xe2e8f0, metalness: 0.9 }});
            const ant = new THREE.Mesh(antGeo, antMat);
            ant.position.set(w * 0.2, h + 3.0, -d * 0.2);
            bGroup.add(ant);

            const beacon = new THREE.Mesh(new THREE.SphereGeometry(0.35, 8, 8), new THREE.MeshBasicMaterial({{ color: 0xef4444 }}));
            beacon.position.set(w * 0.2, h + 6.0, -d * 0.2);
            bGroup.add(beacon);
          }}

          // 6. Ghadi Chowk (Raipur Clock Tower) Superstructure
          if (objId === 'MON_GHADI_CHOWK') {{
            const clockMat = new THREE.MeshBasicMaterial({{ color: 0xfef08a }});
            const clockGeo = new THREE.CylinderGeometry(1.8, 1.8, 0.4, 16);
            clockGeo.rotateX(Math.PI / 2);

            const d1 = new THREE.Mesh(clockGeo, clockMat); d1.position.set(0, 19, d/2 + 0.2); bGroup.add(d1);
            const d2 = new THREE.Mesh(clockGeo, clockMat); d2.position.set(0, 19, -d/2 - 0.2); bGroup.add(d2);
            const d3 = new THREE.Mesh(clockGeo, clockMat); d3.position.set(w/2 + 0.2, 19, 0); d3.rotation.y = Math.PI/2; bGroup.add(d3);
            const d4 = new THREE.Mesh(clockGeo, clockMat); d4.position.set(-w/2 - 0.2, 19, 0); d4.rotation.y = Math.PI/2; bGroup.add(d4);

            const spireGeo = new THREE.ConeGeometry(w * 0.65, 8, 4);
            const spireMat = new THREE.MeshStandardMaterial({{ color: 0xd97706, metalness: 0.85, roughness: 0.2 }});
            const spire = new THREE.Mesh(spireGeo, spireMat);
            spire.position.set(0, h + 4.0, 0);
            spire.rotation.y = Math.PI / 4;
            bGroup.add(spire);

            const flagPole = new THREE.Mesh(new THREE.CylinderGeometry(0.12, 0.12, 6, 8), new THREE.MeshStandardMaterial({{ color: 0xe2e8f0, metalness: 0.9 }}));
            flagPole.position.set(0, h + 11.0, 0);
            bGroup.add(flagPole);

            const flagMesh = new THREE.Mesh(new THREE.PlaneGeometry(2.6, 1.6), new THREE.MeshBasicMaterial({{ color: 0xf97316, side: THREE.DoubleSide }}));
            flagMesh.position.set(1.3, h + 12.5, 0);
            bGroup.add(flagMesh);

            const ghadiLight = new THREE.PointLight(0xf59e0b, 3.5, 70);
            ghadiLight.position.set(0, 16, 0);
            bGroup.add(ghadiLight);
          }}

          // 7. Hospital Complexes (Mekahara & Ram Krishna Care)
          if (attrs.class === 'Hospital') {{
            // Covered Emergency Portico Bay
            const porticoGeo = new THREE.BoxGeometry(w * 0.5, 4.0, 8.0);
            const porticoMat = new THREE.MeshStandardMaterial({{ color: 0xe2e8f0, roughness: 0.4 }});
            const portico = new THREE.Mesh(porticoGeo, porticoMat);
            portico.position.set(0, 2.0, d / 2 + 4.0);
            bGroup.add(portico);

            const pSign = new THREE.Mesh(new THREE.BoxGeometry(w * 0.45, 0.8, 0.2), new THREE.MeshBasicMaterial({{ color: 0xef4444 }}));
            pSign.position.set(0, 3.6, d / 2 + 8.1);
            bGroup.add(pSign);

            // Rooftop Helipad
            const helipad = new THREE.Mesh(new THREE.CylinderGeometry(6.0, 6.0, 0.4, 24), new THREE.MeshStandardMaterial({{ color: 0x334155, roughness: 0.8 }}));
            helipad.position.set(0, h + 0.2, 0);
            bGroup.add(helipad);

            const hRing = new THREE.Mesh(new THREE.RingGeometry(4.8, 5.2, 24), new THREE.MeshBasicMaterial({{ color: 0xffffff }}));
            hRing.rotation.x = -Math.PI / 2;
            hRing.position.set(0, h + 0.42, 0);
            bGroup.add(hRing);

            // Glowing Red Crosses
            const crossH = new THREE.BoxGeometry(8, 1.4, 2.2);
            const crossV = new THREE.BoxGeometry(2.2, 1.4, 8);
            const crossMat = new THREE.MeshBasicMaterial({{ color: 0xef4444 }});
            const ch = new THREE.Mesh(crossH, crossMat); ch.position.set(0, h + 1.2, 0); bGroup.add(ch);
            const cv = new THREE.Mesh(crossV, crossMat); cv.position.set(0, h + 1.2, 0); bGroup.add(cv);
          }}

          // 8. Electrical Substations (S01 - S06)
          if (attrs.class === 'ElectricalSubstation') {{
            const subId = objId.replace('SUB_', '');
            substationPositions[subId] = new THREE.Vector3(cx, h + 2, cz);

            const gravel = new THREE.Mesh(new THREE.PlaneGeometry(w * 1.6, d * 1.6), new THREE.MeshStandardMaterial({{ color: 0x475569, roughness: 0.95 }}));
            gravel.rotation.x = -Math.PI / 2;
            gravel.position.y = 0.08;
            bGroup.add(gravel);

            const tower = new THREE.Mesh(new THREE.CylinderGeometry(0.6, 3.2, 36, 4), new THREE.MeshStandardMaterial({{ color: 0x94a3b8, wireframe: true }}));
            tower.position.set(0, 18, 0);
            bGroup.add(tower);

            const transGroup = new THREE.Group();
            const tankBody = new THREE.Mesh(new THREE.BoxGeometry(5.0, 4.0, 4.0), new THREE.MeshStandardMaterial({{ color: 0x1e293b, metalness: 0.8 }}));
            tankBody.position.y = 2.0;
            transGroup.add(tankBody);
            for (let bi = -1; bi <= 1; bi++) {{
              const bush = new THREE.Mesh(new THREE.CylinderGeometry(0.18, 0.28, 1.6, 8), new THREE.MeshStandardMaterial({{ color: 0xd97706, roughness: 0.3 }}));
              bush.position.set(bi * 1.4, 4.8, 0);
              transGroup.add(bush);
            }}
            transGroup.position.set(w * 0.35, 0, d * 0.35);
            bGroup.add(transGroup);
          }}

          // 9. Informal Slums (Tikrapara)
          if (attrs.roofType === 'corrugated_tin') {{
            towerMesh.material = new THREE.MeshStandardMaterial({{ color: 0xb45309, roughness: 0.9 }});

            const customTinTex = texSlumRoof.clone();
            customTinTex.needsUpdate = true;
            customTinTex.repeat.set(Math.max(1, Math.round(w / 3)), Math.max(1, Math.round(d / 3)));
            const roofMesh = new THREE.Mesh(
              new THREE.BoxGeometry(w * 1.1, 0.8, d * 1.1),
              new THREE.MeshStandardMaterial({{ map: customTinTex, metalness: 0.8, roughness: 0.35 }})
            );
            roofMesh.position.set(0, h + 0.4, 0);
            roofMesh.rotation.z = (Math.random() - 0.5) * 0.12;
            bGroup.add(roofMesh);
            tinRoofsList.push(roofMesh);

            for (let b = 0; b < 3; b++) {{
              const barrel = new THREE.Mesh(new THREE.CylinderGeometry(0.5, 0.5, 1.2, 8), new THREE.MeshStandardMaterial({{ color: 0x0284c7, roughness: 0.4 }}));
              barrel.position.set(w / 2 + 1.2 + b * 0.8, 0.6, d / 2 - b * 0.7);
              bGroup.add(barrel);
            }}
          }}

          cityObjectsGroup.add(bGroup);
        }});
        scene.add(cityObjectsGroup);

        // ═════════════════════════════════════════════════════════════════════
        // 3D HIGHWAY STREETLIGHT POLES & ZEBRA CROSSWALKS
        // ═════════════════════════════════════════════════════════════════════
        const poleMat = new THREE.MeshStandardMaterial({{ color: 0x64748b, metalness: 0.85, roughness: 0.2 }});
        const lampBulbMat = new THREE.MeshBasicMaterial({{ color: 0xfef08a }});

        for (let lx = -200; lx <= 170; lx += 22) {{
          const poleGroup = new THREE.Group();
          const post = new THREE.Mesh(new THREE.CylinderGeometry(0.2, 0.3, 9.0, 8), poleMat);
          post.position.y = 4.5;
          post.castShadow = true;
          poleGroup.add(post);

          const arm = new THREE.Mesh(new THREE.BoxGeometry(2.4, 0.2, 0.2), poleMat);
          arm.position.set(0.9, 8.8, 0);
          poleGroup.add(arm);

          const bulb = new THREE.Mesh(new THREE.BoxGeometry(0.8, 0.2, 0.5), lampBulbMat);
          bulb.position.set(1.8, 8.6, 0);
          poleGroup.add(bulb);

          poleGroup.position.set(lx, 0.1, -7.5);
          scene.add(poleGroup);

          const pole2 = poleGroup.clone();
          pole2.position.set(lx + 11, 0.1, 7.5);
          pole2.rotation.y = Math.PI;
          scene.add(pole2);
        }}

        // Pedestrian Zebra Crossings at Major Intersections
        const crosswalkLocations = [-95, 0, 120];
        crosswalkLocations.forEach(cx => {{
          const cwGroup = new THREE.Group();
          for (let z = -5.0; z <= 5.0; z += 1.2) {{
            const bar = new THREE.Mesh(new THREE.PlaneGeometry(3.0, 0.7), new THREE.MeshBasicMaterial({{ color: 0xffffff }}));
            bar.rotation.x = -Math.PI / 2;
            bar.position.set(0, 0.15, z);
            cwGroup.add(bar);
          }}
          cwGroup.position.set(cx, 0, 0);
          scene.add(cwGroup);
        }});

        // ═════════════════════════════════════════════════════════════════════
        // FLOATING 3D CUMULUS CLOUDS & TELIBANDHA LAKE BOAT
        // ═════════════════════════════════════════════════════════════════════
        const cloudsGroup = new THREE.Group();
        const cloudMat = new THREE.MeshStandardMaterial({{
          color: 0xffffff,
          roughness: 0.95,
          transparent: true,
          opacity: 0.90
        }});

        function createCloud() {{
          const cGroup = new THREE.Group();
          const puffs = 5 + Math.floor(Math.random() * 4);
          for (let p = 0; p < puffs; p++) {{
            const rad = 6.0 + Math.random() * 5.0;
            const puff = new THREE.Mesh(new THREE.DodecahedronGeometry(rad, 1), cloudMat);
            puff.position.set(
              (p - puffs / 2) * 7.0 + (Math.random() - 0.5) * 4.0,
              (Math.random() - 0.5) * 2.5,
              (Math.random() - 0.5) * 5.0
            );
            puff.castShadow = true;
            cGroup.add(puff);
          }}
          return cGroup;
        }}

        const cloudsList = [];
        for (let ci = 0; ci < 16; ci++) {{
          const cloud = createCloud();
          cloud.position.set(
            (Math.random() - 0.5) * 600,
            85 + Math.random() * 35,
            (Math.random() - 0.5) * 600
          );
          cloud.scale.setScalar(0.7 + Math.random() * 0.6);
          cloudsGroup.add(cloud);
          cloudsList.push({{
            obj: cloud,
            speed: 0.08 + Math.random() * 0.06
          }});
        }}
        scene.add(cloudsGroup);

        // Floating Pleasure Boat on Telibandha Lake
        const boatMesh = new THREE.Group();
        const hull = new THREE.Mesh(new THREE.BoxGeometry(4.2, 1.2, 2.2), new THREE.MeshStandardMaterial({{ color: 0xd97706, roughness: 0.5 }}));
        hull.position.y = 0.4;
        boatMesh.add(hull);
        const canopy = new THREE.Mesh(new THREE.BoxGeometry(2.8, 0.2, 2.0), new THREE.MeshStandardMaterial({{ color: 0xef4444 }}));
        canopy.position.y = 1.6;
        boatMesh.add(canopy);
        boatMesh.position.set(152, 0.15, 62);
        scene.add(boatMesh);

        // ═════════════════════════════════════════════════════════════════════
        // AUTHENTIC RAIPUR SMART CITY FBX ASSETS & SKELETAL ANIMATIONS
        // Cloned from AkshaySharmaDEV/Cycle4Change-SmartCityRaipur
        // ═════════════════════════════════════════════════════════════════════
        const animMixers = [];
        const walkingCitizens = [];
        const activeCyclists = [];
        const cityTraffic = [];
        const cyclesFleet = [];

        function parseBase64FBX(b64Str) {{
          if (!b64Str) return null;
          const bin = window.atob(b64Str);
          const len = bin.length;
          const bytes = new Uint8Array(len);
          for (let i = 0; i < len; i++) {{
            bytes[i] = bin.charCodeAt(i);
          }}
          return bytes.buffer;
        }}

        let fbxLoader = null;
        if (typeof THREE.FBXLoader === 'function') {{
          fbxLoader = new THREE.FBXLoader();
        }}

        function normalizeAndScaleFBX(obj, targetHeight, targetWidth, targetDepth) {{
          if (!obj) return 1.0;
          const box = new THREE.Box3().setFromObject(obj);
          const size = box.getSize(new THREE.Vector3());
          let scale = 1.0;
          if (targetHeight && size.y > 0.0001) {{
            scale = targetHeight / size.y;
          }} else if (targetWidth && size.x > 0.0001) {{
            scale = targetWidth / size.x;
          }} else if (targetDepth && size.z > 0.0001) {{
            scale = targetDepth / size.z;
          }}
          obj.scale.set(scale, scale, scale);
          const scaledBox = new THREE.Box3().setFromObject(obj);
          obj.position.y -= scaledBox.min.y;
          return scale;
        }}

        function loadSmartCityFBX(key, onLoad) {{
          if (!fbxLoader || !SMARTCITY_ASSETS || !SMARTCITY_ASSETS[key]) return;
          try {{
            const buf = parseBase64FBX(SMARTCITY_ASSETS[key]);
            const obj = fbxLoader.parse(buf, '');
            if (onLoad) onLoad(obj);
          }} catch (e) {{
            console.warn("Could not parse FBX asset: " + key, e);
          }}
        }}

        // 1. Authentic Ghadi Chowk (Raipur Historic Clock Tower Landmark)
        loadSmartCityFBX('ghadi_chowk', (model) => {{
          normalizeAndScaleFBX(model, 32.0);
          model.position.set(0, 0, 0);
          model.traverse(c => {{
            if (c.isMesh) {{
              c.castShadow = true;
              c.receiveShadow = true;
              c.material = new THREE.MeshStandardMaterial({{
                color: 0xd97706,
                roughness: 0.45,
                metalness: 0.25
              }});
            }}
          }});
          scene.add(model);
        }});

        loadSmartCityFBX('pro_clocktower', (tower) => {{
          normalizeAndScaleFBX(tower, 28.0);
          tower.position.set(22, 0, -18);
          tower.traverse(c => {{
            if (c.isMesh) {{
              c.castShadow = true;
              c.material = new THREE.MeshStandardMaterial({{ color: 0xb45309, roughness: 0.55 }});
            }}
          }});
          scene.add(tower);
        }});

        // 2. Authentic "Mor Raipur" (मोर रायपुर) 3D Civic Monument at Telibandha
        loadSmartCityFBX('mor_raipur', (mor) => {{
          normalizeAndScaleFBX(mor, 6.0, 14.0);
          mor.position.set(145, 0.25, 40);
          mor.rotation.y = -Math.PI / 4;
          mor.traverse(c => {{
            if (c.isMesh) {{
              c.castShadow = true;
              c.material = new THREE.MeshStandardMaterial({{
                color: 0x10b981,
                roughness: 0.35,
                metalness: 0.45
              }});
            }}
          }});
          scene.add(mor);
        }});

        // 3. Authentic Telibandha Marine Drive Lakefront Promenade
        loadSmartCityFBX('marine_drive', (md) => {{
          normalizeAndScaleFBX(md, null, 65.0);
          md.position.set(165, 0.16, 72);
          md.rotation.y = Math.PI / 2;
          md.traverse(c => {{
            if (c.isMesh) {{
              c.receiveShadow = true;
              c.material = new THREE.MeshStandardMaterial({{
                color: 0xf1f5f9,
                roughness: 0.75
              }});
            }}
          }});
          scene.add(md);
        }});

        // 4. Cycles4Change Protected Corridor Divider Railings
        loadSmartCityFBX('divider_railing', (railing) => {{
          normalizeAndScaleFBX(railing, 1.2);
          railing.traverse(c => {{
            if (c.isMesh) {{
              c.castShadow = true;
              c.material = new THREE.MeshStandardMaterial({{ color: 0x334155, metalness: 0.7 }});
            }}
          }});
          for (let rx = -180; rx <= 140; rx += 16) {{
            const clone = railing.clone();
            clone.position.set(rx, 0.22, 2.5);
            scene.add(clone);
          }}
        }});

        // 5. Smart Traffic Light Poles at Key Junctions
        loadSmartCityFBX('traffic_light', (tlight) => {{
          normalizeAndScaleFBX(tlight, 6.5);
          tlight.traverse(c => {{
            if (c.isMesh) {{
              c.castShadow = true;
              c.material = new THREE.MeshStandardMaterial({{ color: 0x1e293b, roughness: 0.5 }});
            }}
          }});
          const junctions = [
            [-16, 0.12, -12],
            [16, 0.12, 12],
            [-96, 0.12, 24],
            [128, 0.12, 48]
          ];
          junctions.forEach(([jx, jy, jz]) => {{
            const tl = tlight.clone();
            tl.position.set(jx, jy, jz);
            scene.add(tl);
          }});
        }});

        // 6. Animated Walking Citizens (Skeletal Mixers) on Marine Drive
        loadSmartCityFBX('walking_citizen', (citizen) => {{
          normalizeAndScaleFBX(citizen, 1.8);
          citizen.position.set(160, 0.2, 50);
          citizen.traverse(c => {{
            if (c.isMesh) {{
              c.castShadow = true;
              c.material = new THREE.MeshStandardMaterial({{ color: 0x3b82f6, roughness: 0.5 }});
            }}
          }});
          if (citizen.animations && citizen.animations.length > 0) {{
            const m = new THREE.AnimationMixer(citizen);
            m.clipAction(citizen.animations[0]).play();
            animMixers.push(m);
          }}
          scene.add(citizen);
          walkingCitizens.push({{ obj: citizen, minZ: 42, maxZ: 96, speed: 0.18, dir: 1 }});

          const c2 = citizen.clone();
          normalizeAndScaleFBX(c2, 1.8);
          c2.position.set(172, 0.2, 85);
          c2.traverse(c => {{
            if (c.isMesh) c.material = new THREE.MeshStandardMaterial({{ color: 0xf472b6, roughness: 0.5 }});
          }});
          if (citizen.animations && citizen.animations.length > 0) {{
            const m2 = new THREE.AnimationMixer(c2);
            m2.clipAction(citizen.animations[0]).play();
            animMixers.push(m2);
          }}
          scene.add(c2);
          walkingCitizens.push({{ obj: c2, minZ: 42, maxZ: 96, speed: 0.15, dir: -1 }});
        }});

        // 7. Animated Cyclist Rider (Skeletal Mixer) on Cycles4Change Track
        loadSmartCityFBX('cycling_rider', (cyclist) => {{
          normalizeAndScaleFBX(cyclist, 1.7);
          cyclist.position.set(-60, 0.22, 5);
          cyclist.rotation.y = Math.PI / 2;
          cyclist.traverse(c => {{
            if (c.isMesh) {{
              c.castShadow = true;
              c.material = new THREE.MeshStandardMaterial({{ color: 0x10b981, roughness: 0.4 }});
            }}
          }});
          if (cyclist.animations && cyclist.animations.length > 0) {{
            const m = new THREE.AnimationMixer(cyclist);
            m.clipAction(cyclist.animations[0]).play();
            animMixers.push(m);
          }}
          scene.add(cyclist);
          activeCyclists.push({{ obj: cyclist, minX: -200, maxX: 160, speed: 0.45 }});
        }});

        // 8. Sitting Citizen at Telibandha Promenade Bench
        loadSmartCityFBX('sitting_citizen', (sitter) => {{
          normalizeAndScaleFBX(sitter, 1.2);
          sitter.position.set(152, 0.2, 48);
          sitter.rotation.y = -Math.PI / 3;
          sitter.traverse(c => {{
            if (c.isMesh) {{
              c.castShadow = true;
              c.material = new THREE.MeshStandardMaterial({{ color: 0xa855f7, roughness: 0.5 }});
            }}
          }});
          scene.add(sitter);
        }});

        // 9. Authentic Raipur Apartment Blocks
        loadSmartCityFBX('apartment', (apt) => {{
          normalizeAndScaleFBX(apt, 24.0);
          apt.position.set(-40, 0.1, -50);
          apt.traverse(c => {{
            if (c.isMesh) {{
              c.castShadow = true;
              c.receiveShadow = true;
            }}
          }});
          scene.add(apt);

          const apt2 = apt.clone();
          apt2.position.set(60, 0.1, -45);
          scene.add(apt2);
        }});

        // 10. Authentic Civilian City Car (Toyota Prius) in Traffic
        loadSmartCityFBX('prius', (car) => {{
          normalizeAndScaleFBX(car, null, null, 4.6);
          car.position.set(-80, 0.25, 0);
          car.traverse(c => {{
            if (c.isMesh) {{
              c.castShadow = true;
              c.material = new THREE.MeshStandardMaterial({{ color: 0x2563eb, roughness: 0.25, metalness: 0.75 }});
            }}
          }});
          scene.add(car);
          cityTraffic.push({{
            group: car,
            speed: 0.55,
            direction: 1,
            startX: -190,
            endX: 160
          }});
        }});

        // ═════════════════════════════════════════════════════════════════════
        // RSCL SMART SENSOR POLES & CYCLISTS
        // ═════════════════════════════════════════════════════════════════════
        const iotPoles = [
          new THREE.Vector3(0, 0, 8),     // Ghadi Chowk IoT
          new THREE.Vector3(165, 0, 60),  // Marine Drive IoT
          new THREE.Vector3(-95, 0, 36),  // Amanaka IoT
          new THREE.Vector3(-101, 0, 90)  // Tikrapara Slum Sensor
        ];
        const iotLightList = [];
        iotPoles.forEach(pt => {{
          const poleGeo = new THREE.CylinderGeometry(0.35, 0.45, 12, 8);
          const poleMat = new THREE.MeshStandardMaterial({{ color: 0x334155, metalness: 0.8 }});
          const pole = new THREE.Mesh(poleGeo, poleMat);
          pole.position.set(pt.x, 6, pt.z);
          scene.add(pole);

          // Glowing Environmental Status Orb
          const orbGeo = new THREE.SphereGeometry(0.8, 16, 16);
          const orbMat = new THREE.MeshBasicMaterial({{ color: 0x10b981 }});
          const orb = new THREE.Mesh(orbGeo, orbMat);
          orb.position.set(pt.x, 12, pt.z);
          scene.add(orb);
          iotLightList.push(orbMat);
        }});

        // Smart Cyclists on Cycles4Change Track
        const cyclistColors = [0x10b981, 0xf59e0b, 0x3b82f6, 0xef4444];
        for (let i = 0; i < 4; i++) {{
          const bikeGroup = new THREE.Group();
          // Frame
          const frameGeo = new THREE.BoxGeometry(1.8, 0.8, 0.4);
          const frameMat = new THREE.MeshStandardMaterial({{ color: cyclistColors[i % cyclistColors.length] }});
          const frame = new THREE.Mesh(frameGeo, frameMat);
          frame.position.y = 0.8;
          bikeGroup.add(frame);
          // Wheels
          const wheelGeo = new THREE.CylinderGeometry(0.5, 0.5, 0.15, 12);
          const wheelMat = new THREE.MeshBasicMaterial({{ color: 0x0f172a }});
          const w1 = new THREE.Mesh(wheelGeo, wheelMat); w1.rotation.z = Math.PI/2; w1.position.set(-0.7, 0.5, 0); bikeGroup.add(w1);
          const w2 = new THREE.Mesh(wheelGeo, wheelMat); w2.rotation.z = Math.PI/2; w2.position.set(0.7, 0.5, 0); bikeGroup.add(w2);
          // Rider Torso & Helmet
          const riderGeo = new THREE.BoxGeometry(0.8, 1.2, 0.6);
          const riderMat = new THREE.MeshStandardMaterial({{ color: 0xffffff }});
          const rider = new THREE.Mesh(riderGeo, riderMat); rider.position.set(0, 1.6, 0); bikeGroup.add(rider);
          const helmGeo = new THREE.SphereGeometry(0.45, 8, 8);
          const helmMat = new THREE.MeshBasicMaterial({{ color: cyclistColors[i] }});
          const helm = new THREE.Mesh(helmGeo, helmMat); helm.position.set(0, 2.3, 0); bikeGroup.add(helm);

          bikeGroup.position.set(-150 + i * 80, 0.2, 10 + i * 15);
          scene.add(bikeGroup);
          cyclesFleet.push({{
            group: bikeGroup,
            speed: 0.4 + i * 0.05,
            startX: -190,
            endX: 160
          }});
        }}

        // ═════════════════════════════════════════════════════════════════════
        // KHARUN WATER MAIN PIPELINE
        // ═════════════════════════════════════════════════════════════════════
        const wp01Pos = new THREE.Vector3(-81, 2, -82);
        const pipeCurve = new THREE.CatmullRomCurve3([
          wp01Pos,
          new THREE.Vector3(-45, 2, -20),
          new THREE.Vector3(0, 2, 0),
          new THREE.Vector3(45, 2, 50),
          new THREE.Vector3(125, 2, 50)
        ]);
        const pipeGeo = new THREE.TubeGeometry(pipeCurve, 40, 1.6, 8, false);
        const pipeMat = new THREE.MeshBasicMaterial({{ color: 0x06b6d4 }});
        const pipeMesh = new THREE.Mesh(pipeGeo, pipeMat);
        scene.add(pipeMesh);

        // ═════════════════════════════════════════════════════════════════════
        // CSPTCL TRANSMISSION GRID & IEEE 738 CATENARY SAG
        // ═════════════════════════════════════════════════════════════════════
        const catenaryLines = [];
        const gridConnections = [
          ['S01', 'S02'],
          ['S01', 'S03'],
          ['S01', 'S04'],
          ['S03', 'S06'],
          ['S04', 'S05']
        ];

        gridConnections.forEach(([fromId, toId]) => {{
          const p1 = substationPositions[fromId];
          const p2 = substationPositions[toId];
          if (p1 && p2) {{
            const midX = (p1.x + p2.x) / 2;
            const midZ = (p1.z + p2.z) / 2;
            const curve = new THREE.QuadraticBezierCurve3(
              new THREE.Vector3(p1.x, 30, p1.z),
              new THREE.Vector3(midX, 22, midZ),
              new THREE.Vector3(p2.x, 30, p2.z)
            );
            const pts = curve.getPoints(24);
            const lineGeo = new THREE.BufferGeometry().setFromPoints(pts);
            const lineMat = new THREE.LineBasicMaterial({{
              color: (fromId === 'S03' || toId === 'S03') ? 0xff3366 : 0x38bdf8,
              linewidth: 2
            }});
            const lineMesh = new THREE.Line(lineGeo, lineMat);
            scene.add(lineMesh);
            catenaryLines.push({{ mesh: lineMesh, p1, p2, midX, midZ }});
          }}
        }});

        // ═════════════════════════════════════════════════════════════════════
        // S03 AMANAKA ARC FLASH SHORT-CIRCUIT EXPLOSION
        // ═════════════════════════════════════════════════════════════════════
        const s03Pos = substationPositions['S03'] || new THREE.Vector3(-93, 10, 148);
        const sparkCount = 160;
        const sparkGeo = new THREE.BufferGeometry();
        const sparkPositions = new Float32Array(sparkCount * 3);
        const sparkVelocities = [];

        for (let i = 0; i < sparkCount; i++) {{
          sparkPositions[i * 3] = s03Pos.x;
          sparkPositions[i * 3 + 1] = s03Pos.y;
          sparkPositions[i * 3 + 2] = s03Pos.z;
          sparkVelocities.push(new THREE.Vector3(
            (Math.random() - 0.5) * 28,
            Math.random() * 32 + 8,
            (Math.random() - 0.5) * 28
          ));
        }}
        sparkGeo.setAttribute('position', new THREE.BufferAttribute(sparkPositions, 3));
        const sparkMat = new THREE.PointsMaterial({{
          color: 0x38bdf8,
          size: 2.8,
          transparent: true,
          opacity: 0.95,
          blending: THREE.AdditiveBlending
        }});
        const sparkParticles = new THREE.Points(sparkGeo, sparkMat);
        scene.add(sparkParticles);

        const arcStrobe = new THREE.PointLight(0x38bdf8, 8, 120);
        arcStrobe.position.copy(s03Pos);
        scene.add(arcStrobe);

        // ═════════════════════════════════════════════════════════════════════
        // LIVING CITY VEHICLES (Auto-rickshaws, Buses, Ambulances & Tankers)
        // ═════════════════════════════════════════════════════════════════════

        // 1. Municipal Relief Water Tankers (HiGHS MILP Fleet)
        for (let i = 0; i < 5; i++) {{
          const tankerGroup = new THREE.Group();
          // Golden Cab
          const cabGeo = new THREE.BoxGeometry(2.8, 2.3, 2.4);
          const cabMat = new THREE.MeshStandardMaterial({{ color: 0xf59e0b }});
          const cab = new THREE.Mesh(cabGeo, cabMat); cab.position.set(2, 1.3, 0); tankerGroup.add(cab);
          // Cylindrical Water Tank
          const tankGeo = new THREE.CylinderGeometry(1.4, 1.4, 5.8, 16);
          const tankMat = new THREE.MeshStandardMaterial({{ color: 0x0284c7, metalness: 0.6, roughness: 0.3 }});
          const tank = new THREE.Mesh(tankGeo, tankMat); tank.rotation.z = Math.PI / 2; tank.position.set(-1.6, 1.6, 0); tankerGroup.add(tank);
          // Amber Beacon
          const beaconGeo = new THREE.SphereGeometry(0.5, 8, 8);
          const beaconMat = new THREE.MeshBasicMaterial({{ color: 0xf59e0b }});
          const beacon = new THREE.Mesh(beaconGeo, beaconMat); beacon.position.set(2, 2.8, 0); tankerGroup.add(beacon);

          tankerGroup.position.set(-120 + i * 26, 0.4, 30 + i * 18);
          scene.add(tankerGroup);
          cityTraffic.push({{
            group: tankerGroup,
            speed: 0.35 + i * 0.04,
            direction: 1,
            startX: -140,
            endX: 60
          }});
        }}

        // 2. Iconic Indian Auto-rickshaws (Yellow & Green Tuktuks)
        for (let j = 0; j < 4; j++) {{
          const autoGroup = new THREE.Group();
          // Lower Green Body
          const bodyGeo = new THREE.BoxGeometry(1.8, 1.0, 1.4);
          const bodyMat = new THREE.MeshStandardMaterial({{ color: 0x15803d }});
          const aBody = new THREE.Mesh(bodyGeo, bodyMat); aBody.position.y = 0.6; autoGroup.add(aBody);
          // Yellow Canvas Roof
          const roofGeo = new THREE.BoxGeometry(1.9, 0.7, 1.5);
          const roofMat = new THREE.MeshStandardMaterial({{ color: 0xfacc15 }});
          const aRoof = new THREE.Mesh(roofGeo, roofMat); aRoof.position.set(0, 1.4, 0); autoGroup.add(aRoof);
          // Headlight
          const headGeo = new THREE.SphereGeometry(0.3, 8, 8);
          const headMat = new THREE.MeshBasicMaterial({{ color: 0xfef08a }});
          const head = new THREE.Mesh(headGeo, headMat); head.position.set(1.0, 0.8, 0); autoGroup.add(head);

          autoGroup.position.set(-100 + j * 50, 0.3, -25 + (j % 2) * 50);
          scene.add(autoGroup);
          cityTraffic.push({{
            group: autoGroup,
            speed: 0.5 + j * 0.06,
            direction: 1,
            startX: -180,
            endX: 130
          }});
        }}

        // 3. Emergency Ambulance with Flashing Red/Blue Beacons
        const ambuGroup = new THREE.Group();
        const ambuBodyGeo = new THREE.BoxGeometry(4.2, 2.2, 2.0);
        const ambuBodyMat = new THREE.MeshStandardMaterial({{ color: 0xffffff }});
        const ambuBody = new THREE.Mesh(ambuBodyGeo, ambuBodyMat); ambuBody.position.y = 1.3; ambuGroup.add(ambuBody);
        // Red Cross Stripe
        const stripeRedGeo = new THREE.BoxGeometry(4.3, 0.5, 2.1);
        const stripeRedMat = new THREE.MeshBasicMaterial({{ color: 0xef4444 }});
        const stripeRed = new THREE.Mesh(stripeRedGeo, stripeRedMat); stripeRed.position.y = 1.3; ambuGroup.add(stripeRed);
        // Strobe Beacons
        const strobeRed = new THREE.Mesh(new THREE.SphereGeometry(0.4, 8, 8), new THREE.MeshBasicMaterial({{ color: 0xef4444 }}));
        strobeRed.position.set(0.6, 2.6, 0.5); ambuGroup.add(strobeRed);
        const strobeBlue = new THREE.Mesh(new THREE.SphereGeometry(0.4, 8, 8), new THREE.MeshBasicMaterial({{ color: 0x3b82f6 }}));
        strobeBlue.position.set(0.6, 2.6, -0.5); ambuGroup.add(strobeBlue);

        ambuGroup.position.set(-50, 0.4, 15);
        scene.add(ambuGroup);
        cityTraffic.push({{
          group: ambuGroup,
          speed: 0.65,
          direction: 1,
          startX: -160,
          endX: 140
        }});

        // ═════════════════════════════════════════════════════════════════════
        // CAMERA CONTROLLER & LANDMARK SWITCHING
        // ═════════════════════════════════════════════════════════════════════
        let currentCamTarget = new THREE.Vector3(0, 5, 0);
        let targetCamPos = new THREE.Vector3(-65, 55, 195);

        function switchCam(mode) {{
          document.querySelectorAll('.cam-pill').forEach(p => p.classList.remove('active'));
          if (mode === 's03') {{
            targetCamPos.set(-75, 42, 115);
            currentCamTarget.set(s03Pos.x, s03Pos.y + 4, s03Pos.z);
          }} else if (mode === 'ghadi') {{
            targetCamPos.set(24, 30, 34);
            currentCamTarget.set(0, 14, 0); // Ghadi Chowk Tower
          }} else if (mode === 'cycle') {{
            targetCamPos.set(65, 22, 55);
            currentCamTarget.set(45, 2, 30); // Cycles4Change Track
          }} else if (mode === 'drone') {{
            targetCamPos.set(160, 140, 180);
            currentCamTarget.set(0, 0, 0);
          }} else if (mode === 'kharun') {{
            targetCamPos.set(-140, 42, -40);
            currentCamTarget.set(-195, 5, -30);
          }} else if (mode === 'slum') {{
            targetCamPos.set(-80, 24, 125);
            currentCamTarget.set(-101, 4, 95); // Tikrapara
          }} else if (mode === 'hospital') {{
            targetCamPos.set(65, 36, 12);
            currentCamTarget.set(43, 8, -12); // Mekahara Hospital
          }} else if (mode === 'telibandha') {{
            targetCamPos.set(195, 48, 118);
            currentCamTarget.set(165, 2, 72); // Marine Drive Lake
          }} else if (mode === 'top') {{
            targetCamPos.set(0, 320, 0.1);
            currentCamTarget.set(0, 0, 0);
          }}
        }}
        window.switchCam = switchCam;

        // Apply initial camera selection from Streamlit dropdown
        const initialCam = "{cam_view}";
        if (initialCam.includes("Ghadi")) switchCam('ghadi');
        else if (initialCam.includes("Cycles4Change")) switchCam('cycle');
        else if (initialCam.includes("S03") || initialCam.includes("Arc Fault")) switchCam('s03');
        else if (initialCam.includes("Kharun")) switchCam('kharun');
        else if (initialCam.includes("Slum")) switchCam('slum');
        else if (initialCam.includes("Hospital")) switchCam('hospital');
        else if (initialCam.includes("Telibandha") || initialCam.includes("Marine")) switchCam('telibandha');
        else if (initialCam.includes("Top-Down") || initialCam.includes("Blueprint")) switchCam('top');
        else switchCam('drone');

        camera.position.copy(targetCamPos);
        controls.target.copy(currentCamTarget);
        controls.update();

        // Playback Transport Controls
        function togglePlayPause() {{
          isPlaying = !isPlaying;
          const btn = document.getElementById('btn-play-pause');
          btn.innerText = isPlaying ? '⏸' : '▶';
          btn.classList.toggle('active', !isPlaying);
        }}
        window.togglePlayPause = togglePlayPause;

        function resetSim() {{
          simTimeHours = 0.0;
        }}
        window.resetSim = resetSim;

        function cycleSpeed() {{
          if (simSpeed === 1.0) simSpeed = 2.0;
          else if (simSpeed === 2.0) simSpeed = 5.0;
          else simSpeed = 1.0;
          document.getElementById('btn-speed').innerText = simSpeed + 'x';
        }}
        window.cycleSpeed = cycleSpeed;

        function seekTimeline(e) {{
          const rect = e.currentTarget.getBoundingClientRect();
          const ratio = Math.max(0, Math.min(1, (e.clientX - rect.left) / rect.width));
          simTimeHours = ratio * maxTimeHours;
        }}
        window.seekTimeline = seekTimeline;

        // ═════════════════════════════════════════════════════════════════════
        // OPENCITYMODEL RAYCASTING & ASSET INSPECTOR
        // ═════════════════════════════════════════════════════════════════════
        const raycaster = new THREE.Raycaster();
        const mouse = new THREE.Vector2();
        const inspectorCard = document.getElementById('inspector-card');

        window.addEventListener('click', (e) => {{
          mouse.x = (e.clientX / window.innerWidth) * 2 - 1;
          mouse.y = -(e.clientY / window.innerHeight) * 2 + 1;
          raycaster.setFromCamera(mouse, camera);

          const intersects = raycaster.intersectObjects(interactiveBuildings);
          if (intersects.length > 0) {{
            const hit = intersects[0].object;
            const attrs = hit.userData.attrs;
            if (attrs) {{
              inspectorCard.style.display = 'block';
              document.getElementById('insp-title').innerText = attrs.name || (attrs.zone_name ? 'Zone ' + attrs.zone_name : 'OpenCityModel Building');
              document.getElementById('insp-type').innerText = hit.userData.id;
              document.getElementById('insp-class').innerText = attrs.class || 'Building (LOD1)';
              document.getElementById('insp-roof').innerText = attrs.roofType || 'flat_concrete';
              document.getElementById('insp-pen').innerText = attrs.tin_roof_penalty_c ? '+' + attrs.tin_roof_penalty_c + '°C' : (attrs.voltage_kv ? attrs.voltage_kv + ' kV' : 'N/A');
              document.getElementById('insp-coords').innerText = attrs.lat ? attrs.lat.toFixed(4) + '° N, ' + attrs.lon.toFixed(4) + '° E' : '21.2514° N, 81.6296° E';
              document.getElementById('insp-prov').innerText = attrs.source || 'Raipur Smart City (RSCL)';
            }}
          }} else if (e.clientY > 160 && e.clientY < window.innerHeight - 80) {{
            inspectorCard.style.display = 'none';
          }}
        }});

        // ═════════════════════════════════════════════════════════════════════
        // MAIN SIMULATION LOOP (60 FPS)
        // ═════════════════════════════════════════════════════════════════════
        let clock = new THREE.Clock();

        function animate() {{
          requestAnimationFrame(animate);
          const delta = clock.getDelta();

          if (isPlaying) {{
            simTimeHours += (delta * 1.5 * simSpeed);
            if (simTimeHours > maxTimeHours) simTimeHours = 0.0;
          }}

          camera.position.lerp(targetCamPos, 0.04);
          controls.target.lerp(currentCamTarget, 0.04);
          controls.update();

          const tProgress = simTimeHours / maxTimeHours;
          document.getElementById('scrubber-fill').style.width = (tProgress * 100) + '%';
          document.getElementById('label-curr-time').innerText = 'Hour ' + simTimeHours.toFixed(1) + ':00';

          const isCrisis = simTimeHours >= 36.0 && simTimeHours <= 68.0;
          const isPostRecovery = simTimeHours > 68.0;

          // Temperature curve
          let currentTemp = 38.0;
          if (simTimeHours <= 48.0) {{
            currentTemp = 38.0 + (simTimeHours / 48.0) * 9.9;
          }} else {{
            currentTemp = 47.9 - ((simTimeHours - 48.0) / 48.0) * 7.5;
          }}

          let currentLoad = 310.0 + (currentTemp - 38.0) * 16.5;
          let tHotspot = 85.0 + (currentTemp - 38.0) * 5.2;

          document.getElementById('val-temp').innerText = currentTemp.toFixed(1) + '°C';
          document.getElementById('val-load').innerText = currentLoad.toFixed(0) + ' MW';
          document.getElementById('val-hotspot').innerText = tHotspot.toFixed(1) + '°C';

          // Animate Lake Fountain Spray Particles
          const sprayPositions = sprayParticles.geometry.attributes.position.array;
          for (let i = 0; i < sprayCount; i++) {{
            sprayPositions[i * 3] += sprayVels[i].x * delta * 0.5;
            sprayPositions[i * 3 + 1] += sprayVels[i].y * delta;
            sprayPositions[i * 3 + 2] += sprayVels[i].z * delta * 0.5;
            sprayVels[i].y -= 9.8 * delta; // Gravity
            if (sprayPositions[i * 3 + 1] < 1.0) {{
              sprayPositions[i * 3] = 165;
              sprayPositions[i * 3 + 1] = 2.2;
              sprayPositions[i * 3 + 2] = 72;
              sprayVels[i].y = Math.random() * 9 + 4;
            }}
          }}
          sprayParticles.geometry.attributes.position.needsUpdate = true;

          // Dynamic Skybox & Sun Transitions
          if (currentTemp > 44.0) {{
            scene.background.lerp(skyPalette.heat, 0.05);
            scene.fog.color.lerp(skyPalette.warm, 0.05);
            sunLight.color.setHex(0xffaa44);
            sunLight.intensity = 2.8;
            hemiLight.intensity = 1.6;
            sunMesh.scale.setScalar(1.0 + Math.sin(Date.now() * 0.003) * 0.15);
          }} else {{
            scene.background.lerp(skyPalette.day, 0.05);
            scene.fog.color.setHex(0xdbeafe);
            sunLight.color.setHex(0xfffbeb);
            sunLight.intensity = 2.3;
            hemiLight.intensity = 1.45;
            sunMesh.scale.setScalar(1.0);
          }}

          // Pulse Smart Environmental IoT Poles
          const iotColor = isCrisis ? 0xef4444 : 0x10b981;
          iotLightList.forEach(m => m.color.setHex(iotColor));

          // Tin Roof Heat Trap (Turn blazing red under heatwave)
          const tinFactor = Math.max(0, Math.min(1, (currentTemp - 40.0) / 7.9));
          tinRoofsList.forEach(r => {{
            r.material.color.setRGB(0.88 + tinFactor * 0.12, 0.90 - tinFactor * 0.70, 0.94 - tinFactor * 0.85);
          }});

          // IEEE 738 Conductor Catenary Sag
          const sag = (currentTemp - 38.0) * 0.35;
          catenaryLines.forEach(cl => {{
            const curve = new THREE.QuadraticBezierCurve3(
              new THREE.Vector3(cl.p1.x, 30, cl.p1.z),
              new THREE.Vector3(cl.midX, 22 - sag, cl.midZ),
              new THREE.Vector3(cl.p2.x, 30, cl.p2.z)
            );
            cl.mesh.geometry.setFromPoints(curve.getPoints(24));
          }});

          // S03 Arc Flash Short Circuit Sparks
          const isArcActive = tHotspot >= 125.0;
          if (isArcActive) {{
            arcStrobe.intensity = Math.random() > 0.3 ? 7.5 : 0.4;
            arcStrobe.color.setHex(Math.random() > 0.5 ? 0x38bdf8 : 0xff3366);

            const positions = sparkParticles.geometry.attributes.position.array;
            for (let i = 0; i < sparkCount; i++) {{
              positions[i * 3] += sparkVelocities[i].x * delta;
              positions[i * 3 + 1] += sparkVelocities[i].y * delta;
              positions[i * 3 + 2] += sparkVelocities[i].z * delta;

              if (positions[i * 3 + 1] < 2 || positions[i * 3 + 1] > 40) {{
                positions[i * 3] = s03Pos.x + (Math.random() - 0.5) * 4;
                positions[i * 3 + 1] = s03Pos.y + Math.random() * 2;
                positions[i * 3 + 2] = s03Pos.z + (Math.random() - 0.5) * 4;
              }}
            }}
            sparkParticles.geometry.attributes.position.needsUpdate = true;
            sparkParticles.visible = true;

            if (typeof windowMeshesList !== 'undefined' && windowMeshesList.length > 0) {{
              windowMeshesList.forEach((w, idx) => {{
                if (w && w.material && idx % 2 === 0) w.material.opacity = 0.05;
              }});
            }}

            pipeMat.color.setHex(0xef4444);
            document.getElementById('hud-badge').innerText = 'STAGE 4 // S03 ARC FLASH TRIP';
            document.getElementById('hud-badge').style.background = '#EF4444';
            document.getElementById('val-water').innerText = '90 / 180 MLD (WP02 TRIP)';
            document.getElementById('ticker-text').innerText = 'S03 Amanaka Transformer T-03 tripped on overtemperature flashover! Kharun WP02 lost feeder power. Tikrapara slum water pressure zero.';
          }} else if (isPostRecovery) {{
            arcStrobe.intensity = 0;
            sparkParticles.visible = false;
            pipeMat.color.setHex(0x10b981);
            document.getElementById('hud-badge').innerText = 'STAGE 6 // MUNICIPAL RECOVERY';
            document.getElementById('hud-badge').style.background = '#10B981';
            document.getElementById('val-water').innerText = '165 MLD (DG RESTORED)';
            document.getElementById('ticker-text').innerText = 'Mobile DG operational at Kharun WP02. 20 potable water tankers actively relieving Tikrapara & Gudhiyari wards. System resilience Q(t) rebounding.';
          }} else {{
            arcStrobe.intensity = 0;
            sparkParticles.visible = false;
            pipeMat.color.setHex(0x06b6d4);
            if (typeof windowMeshesList !== 'undefined' && windowMeshesList.length > 0) {{
              windowMeshesList.forEach(w => {{
                if (w && w.material) w.material.opacity = 0.35;
              }});
            }}
            document.getElementById('hud-badge').innerText = 'STAGE 2 // NORMAL OPERATIONS';
            document.getElementById('hud-badge').style.background = '#3B82F6';
            document.getElementById('val-water').innerText = '180 MLD (NOMINAL)';
            document.getElementById('ticker-text').innerText = 'Grid demand rising along saturating ODE curve. Winding hot-spots monitored across all 6 substations. ACSR Zebra conductors within statutory clearance.';
          }}

          // Animate Living City Traffic (Tankers, Autos, Ambulances)
          cityTraffic.forEach(veh => {{
            veh.group.position.x += veh.speed * veh.direction;
            if (veh.group.position.x > veh.endX) {{
              veh.direction = -1;
              veh.group.rotation.y = Math.PI;
            }} else if (veh.group.position.x < veh.startX) {{
              veh.direction = 1;
              veh.group.rotation.y = 0;
            }}
          }});

          // Animate Smart Cyclists along Cycles4Change Green Track
          cyclesFleet.forEach(c => {{
            c.group.position.x += c.speed;
            if (c.group.position.x > c.endX) {{
              c.group.position.x = c.startX;
            }}
          }});

          // Animate Skeletal Animation Mixers (Walking Citizens & Cycling Riders)
          animMixers.forEach(m => {{
            try {{ m.update(delta); }} catch (e) {{}}
          }});

          // Animate Walking Pedestrians along Telibandha Marine Drive Promenade
          walkingCitizens.forEach(w => {{
            w.obj.position.z += w.speed * w.dir;
            if (w.obj.position.z > w.maxZ) {{
              w.dir = -1;
              w.obj.rotation.y = Math.PI;
            }} else if (w.obj.position.z < w.minZ) {{
              w.dir = 1;
              w.obj.rotation.y = 0;
            }}
          }});

          // Animate Active Cyclists along Cycles4Change Track
          activeCyclists.forEach(c => {{
            c.obj.position.x += c.speed;
            if (c.obj.position.x > c.maxX) {{
              c.obj.position.x = c.minX;
            }}
          }});

          // Drift 3D Cumulus Clouds across the sky
          cloudsList.forEach(c => {{
            c.obj.position.x += c.speed;
            if (c.obj.position.x > 320) c.obj.position.x = -320;
          }});

          // Bob Pleasure Boat on Telibandha Lake
          if (boatMesh) {{
            boatMesh.position.y = 0.15 + Math.sin(Date.now() * 0.003) * 0.12;
            boatMesh.rotation.z = Math.sin(Date.now() * 0.002) * 0.04;
          }}

          renderer.render(scene, camera);
        }}

        animate();

        window.addEventListener('resize', () => {{
          camera.aspect = window.innerWidth / window.innerHeight;
          camera.updateProjectionMatrix();
          renderer.setSize(window.innerWidth, window.innerHeight);
        }});
      </script>
    </body>
    </html>
    """


    # Embed WebGL Canvas
    components.html(html_code, height=720, scrolling=False)

    st.markdown("---")

    # Companion Narrative & Multi-Model Physics Breakdown
    st.markdown('<div class="section-head">OpenCityModel (CityJSON) Architectural Ingestion & Physics Grounding</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-subhead">Grounding the 3D theatre in IEEE, CSERC, and biometeorological standards: '
        'how macroclimate extremes propagate through interconnected physical infrastructure.</div>',
        unsafe_allow_html=True
    )

    t1, t2, t3, t4 = st.tabs([
        "OpenCityModel Raipur Spatial Geometry",
        "Raipur Smart City (RSCL) & Cycles4Change",
        "Physical Twin Telemetry Breakdown",
        "Municipal Intervention & Tanker Dispatch"
    ])

    with t1:
        st.markdown(f"""
        <div class="bento-tile tile-grid" style="margin-bottom:12px;">
          <div class="stat-eyebrow">OpenCityModel CityJSON LOD1 Dataset Metrics</div>
          <div style="font-size:12.5px;color:#CBD5E1;line-height:1.6;margin-top:6px;">
            <b>• Dataset Specification:</b> OpenCityModel (CityJSON 1.0) &middot; EPSG:4979 WGS84 Geographic Datum.<br/>
            <b>• Ingested Buildings:</b> <b>{raipur_city_json['metadata']['total_buildings']} 3D Building Objects</b> across 12 Raipur municipal planning zones.<br/>
            <b>• Physical Anchor Coordinates:</b> Center Datum at Jaistambh Chowk / Civil Lines (21.2514° N, 81.6296° E).<br/>
            <b>• Landmark Features:</b> Ghadi Chowk (Clock Tower), Telibandha Marine Drive, Kharun River western boundary, and Great Eastern Road (GE Road / NH-53).
          </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="step-ribbon">
          <div class="step-ribbon-item">
            <span class="step-num">ACT 1</span>
            <span class="step-label">Solar Onset (38°C)</span>
          </div>
          <div class="step-ribbon-item">
            <span class="step-num">ACT 2</span>
            <span class="step-label">Load Surge (43°C)</span>
          </div>
          <div class="step-ribbon-item">
            <span class="step-num">ACT 3</span>
            <span class="step-label">Conductor Sag (46.5°C)</span>
          </div>
          <div class="step-ribbon-item">
            <span class="step-num" style="background:#EF4444;color:#FFF;">ACT 4</span>
            <span class="step-label" style="color:#EF4444;">Arc Flash & Trip (47.9°C)</span>
          </div>
          <div class="step-ribbon-item">
            <span class="step-num">ACT 5</span>
            <span class="step-label">Lifeline Blackout</span>
          </div>
          <div class="step-ribbon-item">
            <span class="step-num" style="background:#10B981;color:#FFF;">ACT 6</span>
            <span class="step-label" style="color:#10B981;">Tankers & Recovery</span>
          </div>
        </div>
        """, unsafe_allow_html=True)

    with t2:
        c_rscl1, c_rscl2 = st.columns(2)
        with c_rscl1:
            st.markdown("""
            <div class="bento-tile tile-civic" style="margin-bottom:12px;">
              <div class="stat-eyebrow">Raipur Smart City Limited (RSCL) Assets</div>
              <div style="font-size:12.5px;color:#CBD5E1;line-height:1.6;margin-top:6px;">
                <b>• Ghadi Chowk Landmark:</b> Historic clock tower at Jaistambh / Raj Bhavan intersection on GE Road; serves as the city's central civic coordinate anchor.<br/>
                <b>• Telibandha Marine Drive:</b> 2.5 km lakefront non-motorized transport boulevard and public recreation hub.<br/>
                <b>• Cycles4Change Green Corridor:</b> Dedicated cycling corridor along GE Road prioritized for sustainable transit and emergency relief access during crises.<br/>
                <b>• Smart Environmental IoT Poles:</b> Distributed sensor nodes monitoring ambient microclimate temperatures and air quality.
              </div>
            </div>
            """, unsafe_allow_html=True)

        with c_rscl2:
            st.markdown("""
            <div class="bento-tile tile-gold" style="margin-bottom:12px;">
              <div class="stat-eyebrow">Emergency Climate Repurposing</div>
              <div style="font-size:12.5px;color:#CBD5E1;line-height:1.6;margin-top:6px;">
                <b>• Shaded Cooling Kiosks:</b> During heatwave triggers (>44°C), RSCL activates shaded misting kiosks along the Cycles4Change track.<br/>
                <b>• Express Relief Lane:</b> The non-motorized corridor provides unimpeded express access for municipal water tankers and medical emergency responders avoiding highway traffic bottlenecks.<br/>
                <b>• Sensor-Driven Alerts:</b> Real-time IoT pole telemetry feeds directly into AGNAYA's biometeorological UTCI and trilingual alert generators.
              </div>
            </div>
            """, unsafe_allow_html=True)

    with t3:
        col_m1, col_m2, col_m3, col_m4 = st.columns(4)
        with col_m1:
            st.markdown(f"""
            <div class="bento-tile tile-heat">
              <div class="stat-eyebrow">Peak Ambient Telemetry</div>
              <div class="stat-figure-row">
                <span class="stat-number critical">{T_peak:.1f}</span>
                <span class="stat-unit">°C</span>
              </div>
              <div class="stat-caption">IMD Mana Airport #42809</div>
            </div>
            """, unsafe_allow_html=True)

        with col_m2:
            st.markdown("""
            <div class="bento-tile tile-grid">
              <div class="stat-eyebrow">S03 Amanaka Transformer</div>
              <div class="stat-figure-row">
                <span class="stat-number critical">134.8</span>
                <span class="stat-unit">°C</span>
              </div>
              <div class="stat-caption">Winding hot-spot &theta;<sub>H</sub> (Trip point)</div>
            </div>
            """, unsafe_allow_html=True)

        with col_m3:
            st.markdown("""
            <div class="bento-tile tile-civic">
              <div class="stat-eyebrow">Kharun Pumping Capacity</div>
              <div class="stat-figure-row">
                <span class="stat-number warning">90 / 180</span>
                <span class="stat-unit">MLD</span>
              </div>
              <div class="stat-caption">WP02 tripped (50% deficit)</div>
            </div>
            """, unsafe_allow_html=True)

        with col_m4:
            st.markdown(f"""
            <div class="bento-tile tile-gold">
              <div class="stat-eyebrow">Tin-Roof Slum Heat Trap</div>
              <div class="stat-figure-row">
                <span class="stat-number critical">+{min(6.5, 4.0 * 0.35 + 2.0):.1f}</span>
                <span class="stat-unit">°C</span>
              </div>
              <div class="stat-caption">Tikrapara indoor microclimate</div>
            </div>
            """, unsafe_allow_html=True)

    with t4:
        st.markdown(f"""
        <div class="callout-box">
          <strong style="color:#F8FAFC;">Municipal Dispatch Operations (Budget: ₹{budget_lakh:.1f} Lakhs):</strong><br/>
          In the 3D theatre above, observe the <b>yellow-cabbed mobile water tankers</b> circulating continuously between the Kharun river intake depot and the informal slum clusters in Tikrapara and Gudhiyari. Under the active HiGHS optimization plan, <b>20 tankers</b> deliver potable water directly to low-pressure nodes, preventing acute dehydration while mobile emergency generators restore pumping at WP02.
        </div>
        """, unsafe_allow_html=True)
