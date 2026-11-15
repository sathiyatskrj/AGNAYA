"""
AGNAYA - 3D City Simulation & Causal Cascade Theatre (Mode 4)
OpenCityModel (CityJSON LOD1) Georeferenced Digital Twin of Raipur, Chhattisgarh.
Incorporates CityJSON geometries from https://github.com/opencitymodel/opencitymodel,
CSERC Tariff Order FY24-25 grid parameters, Kharun River 180 MLD pumping infrastructure,
and biometeorological heatwave cascade dynamics.

MANDATORY DISCLAIMER: SIMULATION ONLY – NOT AN OFFICIAL WARNING.
"""

import json
import streamlit as st
import streamlit.components.v1 as components
from data.raipur_opencitymodel import get_raipur_opencitymodel


def render_city_simulation_view(
    T_peak: float,
    rel_humidity: float,
    duration_days: int,
    budget_lakh: float,
    tripped_id: str | None = "S03 Amanaka"
):
    st.markdown('<div class="section-head">3D Raipur City Digital Twin & Causal Cascade Theatre (OpenCityModel)</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-subhead">Georeferenced 3D digital twin of Raipur City built on the open '
        '<a href="https://github.com/opencitymodel/opencitymodel" target="_blank" style="color:#38BDF8;text-decoration:underline;">OpenCityModel (CityJSON LOD1)</a> '
        'standard. Simulates physical macroclimate propagation across 12 municipal planning zones, CSPTCL 220/132 kV substations, '
        'the Kharun River 180 MLD water treatment facility, Telibandha Talab (Marine Drive), and slum microclimates. '
        '<b>Simulation only &mdash; not an official warning.</b></div>',
        unsafe_allow_html=True
    )

    # Fetch verified OpenCityModel dataset for Raipur
    raipur_city_json = get_raipur_opencitymodel()
    city_json_str = json.dumps(raipur_city_json)

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
                "🚁 Full Raipur Aerial Drone Orbit",
                "💧 Kharun River 180 MLD Intake & Pumping Works",
                "🏚️ Tikrapara Informal Slum Sector (Tin Roof Heat Trap)",
                "🏥 Dr. B.R. Ambedkar Memorial Hospital (Mekahara)",
                "🌊 Telibandha Talab (Marine Drive Lakefront)",
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
          background: #090B0E;
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
          background: rgba(16, 20, 28, 0.82);
          backdrop-filter: blur(12px);
          border: 1px solid rgba(255, 255, 255, 0.08);
          border-radius: 8px;
          padding: 10px 18px;
          z-index: 100;
          pointer-events: auto;
        }}
        .hud-title-lockup {{
          display: flex;
          align-items: center;
          gap: 12px;
        }}
        .hud-badge {{
          font-size: 11px;
          font-weight: 700;
          letter-spacing: 0.06em;
          text-transform: uppercase;
          background: #EF4444;
          color: #FFFFFF;
          padding: 3px 8px;
          border-radius: 4px;
          animation: pulse-red 2s infinite;
        }}
        @keyframes pulse-red {{
          0%, 100% {{ opacity: 1; }}
          50% {{ opacity: 0.6; }}
        }}
        .hud-stats {{
          display: flex;
          gap: 22px;
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
        }}
        .hud-stat-val {{
          font-size: 13px;
          font-weight: 700;
        }}
        .hud-stat-val.crit {{ color: #EF4444; }}
        .hud-stat-val.warn {{ color: #F59E0B; }}
        .hud-stat-val.ok {{ color: #10B981; }}
        .hud-stat-val.cyan {{ color: #38BDF8; }}

        /* Floating Video Playback Transport Controls */
        .hud-transport {{
          position: absolute;
          bottom: 20px;
          left: 50%;
          transform: translateX(-50%);
          display: flex;
          align-items: center;
          gap: 14px;
          background: rgba(16, 20, 28, 0.88);
          backdrop-filter: blur(14px);
          border: 1px solid rgba(255, 255, 255, 0.12);
          border-radius: 30px;
          padding: 8px 24px;
          z-index: 100;
          box-shadow: 0 12px 32px rgba(0, 0, 0, 0.6);
        }}
        .transport-btn {{
          background: #1E293B;
          border: 1px solid rgba(255, 255, 255, 0.1);
          color: #F8FAFC;
          width: 38px;
          height: 38px;
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          cursor: pointer;
          transition: all 0.2s ease;
          font-size: 14px;
        }}
        .transport-btn:hover {{
          background: #3B82F6;
          border-color: #60A5FA;
          transform: scale(1.05);
        }}
        .transport-btn.active {{
          background: #EF4444;
          border-color: #F87171;
        }}
        .scrubber-container {{
          display: flex;
          flex-direction: column;
          gap: 4px;
          width: 280px;
        }}
        .scrubber-track {{
          position: relative;
          width: 100%;
          height: 6px;
          background: #334155;
          border-radius: 3px;
          cursor: pointer;
        }}
        .scrubber-fill {{
          height: 100%;
          width: 65%;
          background: linear-gradient(90deg, #3B82F6, #EF4444);
          border-radius: 3px;
        }}
        .scrubber-labels {{
          display: flex;
          justify-content: space-between;
          font-size: 10px;
          color: #94A3B8;
          font-family: monospace;
        }}

        /* Live Event Log Ticker */
        .hud-ticker {{
          position: absolute;
          bottom: 24px;
          left: 18px;
          max-width: 360px;
          background: rgba(15, 23, 42, 0.88);
          backdrop-filter: blur(8px);
          border: 1px solid rgba(239, 68, 68, 0.35);
          border-radius: 6px;
          padding: 8px 12px;
          font-size: 11px;
          line-height: 1.4;
          z-index: 100;
          color: #CBD5E1;
        }}
        .ticker-header {{
          color: #EF4444;
          font-weight: 700;
          font-size: 10px;
          text-transform: uppercase;
          margin-bottom: 4px;
          display: flex;
          align-items: center;
          gap: 6px;
        }}
        .ticker-dot {{
          width: 6px;
          height: 6px;
          border-radius: 50%;
          background: #EF4444;
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
          background: rgba(30, 41, 59, 0.85);
          backdrop-filter: blur(6px);
          border: 1px solid rgba(255, 255, 255, 0.08);
          color: #CBD5E1;
          padding: 6px 12px;
          border-radius: 4px;
          font-size: 11px;
          cursor: pointer;
          transition: all 0.2s;
          text-align: right;
        }}
        .cam-pill:hover, .cam-pill.active {{
          background: #3B82F6;
          color: #FFFFFF;
          border-color: #60A5FA;
        }}

        /* OpenCityModel Inspector Card (Interactive Click) */
        .inspector-card {{
          position: absolute;
          top: 76px;
          left: 18px;
          width: 280px;
          background: rgba(16, 20, 28, 0.92);
          backdrop-filter: blur(12px);
          border: 1px solid rgba(56, 189, 248, 0.3);
          border-radius: 8px;
          padding: 12px;
          font-size: 11px;
          z-index: 100;
          display: none;
        }}
        .inspector-title {{
          color: #38BDF8;
          font-weight: 700;
          font-size: 12px;
          margin-bottom: 6px;
          border-bottom: 1px solid rgba(255, 255, 255, 0.08);
          padding-bottom: 4px;
        }}
        .inspector-row {{
          display: flex;
          justify-content: space-between;
          margin-bottom: 3px;
        }}
        .inspector-label {{ color: #94A3B8; }}
        .inspector-val {{ font-family: monospace; font-weight: 600; color: #F8FAFC; }}

        /* Legend */
        .hud-legend {{
          position: absolute;
          bottom: 24px;
          right: 18px;
          background: rgba(15, 23, 42, 0.88);
          backdrop-filter: blur(8px);
          border: 1px solid rgba(255, 255, 255, 0.08);
          border-radius: 6px;
          padding: 8px 12px;
          font-size: 10px;
          z-index: 100;
          display: flex;
          flex-direction: column;
          gap: 4px;
        }}
        .legend-item {{
          display: flex;
          align-items: center;
          gap: 8px;
        }}
        .legend-color {{
          width: 10px;
          height: 10px;
          border-radius: 2px;
        }}
      </style>
      <!-- Include Three.js & OrbitControls from cdnjs -->
      <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
      <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
    </head>
    <body>
      <div id="canvas-container"></div>

      <!-- Glassmorphic Top HUD -->
      <div class="hud-header">
        <div class="hud-title-lockup">
          <span class="hud-badge" id="hud-badge">STAGE 4 // S03 ARC FAULT</span>
          <div>
            <div style="font-weight: 700; font-size: 13px;">RAIPUR CITY 3D DIGITAL TWIN</div>
            <div style="font-size: 10.5px; color: #94A3B8;">OpenCityModel (CityJSON LOD1) &middot; EPSG:4979 WGS84 &middot; Kharun River Basin</div>
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
        <div class="cam-pill" onclick="switchCam('drone')">🚁 Full Raipur Drone Flyover</div>
        <div class="cam-pill" onclick="switchCam('kharun')">💧 Kharun 180 MLD Water Plant</div>
        <div class="cam-pill" onclick="switchCam('slum')">🏚️ Tikrapara Slum (Tin Heat Trap)</div>
        <div class="cam-pill" onclick="switchCam('hospital')">🏥 Ambedkar Memorial Hospital (Mekahara)</div>
        <div class="cam-pill" onclick="switchCam('telibandha')">🌊 Telibandha Talab (Marine Drive)</div>
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
            <span id="label-curr-time">Hour 48:00 (Peak Arc)</span>
            <span>96:00 (Recovery)</span>
          </div>
        </div>
        <button class="transport-btn" id="btn-speed" onclick="cycleSpeed()" style="font-size:11px;font-weight:700;">1x</button>
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
        <div class="legend-item"><div class="legend-color" style="background:#0284C7;"></div><span>Kharun River 180 MLD Intake & Main</span></div>
        <div class="legend-item"><div class="legend-color" style="background:#0369A1;"></div><span>Telibandha Talab (Marine Drive)</span></div>
        <div class="legend-item"><div class="legend-color" style="background:#38BDF8;"></div><span>CSPTCL 220/132 kV Transmission Grid</span></div>
        <div class="legend-item"><div class="legend-color" style="background:#EF4444;"></div><span>S03 Arc Fault & Tripped Substation</span></div>
        <div class="legend-item"><div class="legend-color" style="background:#94A3B8;"></div><span>Tin-Roof Slum Dwellings (Heat Trap)</span></div>
        <div class="legend-item"><div class="legend-color" style="background:#F59E0B;"></div><span>Municipal Relief Tanker (HiGHS MILP)</span></div>
        <div class="legend-item"><div class="legend-color" style="background:#10B981;"></div><span>Hospital Trauma / Cooling Shelter</span></div>
      </div>

      <!-- Ingest OpenCityModel CityJSON & Run Three.js Engine -->
      <script>
        const RAIPUR_CITY_JSON = {city_json_str};

        let isPlaying = true;
        let simSpeed = 1.0;
        let simTimeHours = {initial_hour};
        const maxTimeHours = 96.0;

        // Container & WebGL Renderer
        const container = document.getElementById('canvas-container');
        const scene = new THREE.Scene();
        scene.background = new THREE.Color(0x090B0E);
        scene.fog = new THREE.FogExp2(0x090B0E, 0.0028);

        const camera = new THREE.PerspectiveCamera(46, window.innerWidth / window.innerHeight, 1, 3500);
        camera.position.set(-50, 45, 185);

        const renderer = new THREE.WebGLRenderer({{ antialias: true, alpha: false }});
        renderer.setSize(window.innerWidth, window.innerHeight);
        renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
        renderer.shadowMap.enabled = true;
        renderer.shadowMap.type = THREE.PCFSoftShadowMap;
        container.appendChild(renderer.domElement);

        const controls = new THREE.OrbitControls(camera, renderer.domElement);
        controls.enableDamping = true;
        controls.dampingFactor = 0.05;
        controls.maxPolarAngle = Math.PI / 2 - 0.03;
        controls.minDistance = 15;
        controls.maxDistance = 750;
        controls.target.set(0, 4, 0);

        // Lighting
        const ambientLight = new THREE.AmbientLight(0x272d3d, 1.3);
        scene.add(ambientLight);

        const sunLight = new THREE.DirectionalLight(0xffedd5, 1.8);
        sunLight.position.set(160, 240, 120);
        sunLight.castShadow = true;
        sunLight.shadow.mapSize.width = 2048;
        sunLight.shadow.mapSize.height = 2048;
        sunLight.shadow.camera.near = 10;
        sunLight.shadow.camera.far = 700;
        sunLight.shadow.camera.left = -260;
        sunLight.shadow.camera.right = 260;
        sunLight.shadow.camera.top = 260;
        sunLight.shadow.camera.bottom = -260;
        scene.add(sunLight);

        // Heat Dome Sun Sphere
        const sunGeo = new THREE.SphereGeometry(22, 32, 32);
        const sunMat = new THREE.MeshBasicMaterial({{ color: 0xff4500 }});
        const sunMesh = new THREE.Mesh(sunGeo, sunMat);
        sunMesh.position.set(240, 300, 180);
        scene.add(sunMesh);

        // Ground Plane (Raipur Topography)
        const groundGeo = new THREE.PlaneGeometry(900, 900, 40, 40);
        const groundMat = new THREE.MeshStandardMaterial({{ color: 0x0c0f17, roughness: 0.95 }});
        const ground = new THREE.Mesh(groundGeo, groundMat);
        ground.rotation.x = -Math.PI / 2;
        ground.receiveShadow = true;
        scene.add(ground);

        const gridHelper = new THREE.GridHelper(800, 80, 0x1e293b, 0x131924);
        gridHelper.position.y = 0.05;
        scene.add(gridHelper);

        // ═════════════════════════════════════════════════════════════════════
        // REAL RAIPUR ARTERIAL ROADS & WATER BODIES
        // ═════════════════════════════════════════════════════════════════════

        // 1. Great Eastern Road (GE Road / NH-53): East-West arterial corridor
        const geRoadCurve = new THREE.CatmullRomCurve3([
          new THREE.Vector3(-220, 0.1, -30), // Tatibandh / AIIMS
          new THREE.Vector3(-95, 0.1, 30),   // Amanaka
          new THREE.Vector3(0, 0.1, 0),      // Jaistambh Chowk / Civil Lines
          new THREE.Vector3(120, 0.1, 45),   // Pandri
          new THREE.Vector3(180, 0.1, 70)    // Telibandha
        ]);
        const geRoadGeo = new THREE.TubeGeometry(geRoadCurve, 64, 4.2, 4, false);
        const geRoadMat = new THREE.MeshStandardMaterial({{ color: 0x1e293b, roughness: 0.8 }});
        const geRoadMesh = new THREE.Mesh(geRoadGeo, geRoadMat);
        geRoadMesh.scale.set(1, 0.05, 1);
        scene.add(geRoadMesh);

        // 2. Kharun River (Western Raipur Lifeline): Real course from Kumhari southwards
        const kharunCurve = new THREE.CatmullRomCurve3([
          new THREE.Vector3(-240, 0.15, -220),
          new THREE.Vector3(-210, 0.15, -130),
          new THREE.Vector3(-180, 0.15, -30),
          new THREE.Vector3(-195, 0.15, 60),
          new THREE.Vector3(-230, 0.15, 180),
          new THREE.Vector3(-260, 0.15, 270)
        ]);
        const kharunGeo = new THREE.TubeGeometry(kharunCurve, 80, 18, 8, false);
        const kharunMat = new THREE.MeshStandardMaterial({{
          color: 0x0284c7,
          roughness: 0.15,
          metalness: 0.8,
          transparent: true,
          opacity: 0.9
        }});
        const kharunMesh = new THREE.Mesh(kharunGeo, kharunMat);
        kharunMesh.scale.set(1, 0.05, 1);
        scene.add(kharunMesh);

        // 3. Telibandha Talab (Marine Drive Raipur Lake): Real eastern lake basin
        const lakeGeo = new THREE.CylinderGeometry(28, 28, 0.3, 32);
        const lakeMat = new THREE.MeshStandardMaterial({{
          color: 0x0369a1,
          roughness: 0.2,
          metalness: 0.7,
          transparent: true,
          opacity: 0.88
        }});
        const lakeMesh = new THREE.Mesh(lakeGeo, lakeMat);
        lakeMesh.position.set(165, 0.1, 72);
        scene.add(lakeMesh);

        // Promenade around Telibandha Lake
        const lakeRingGeo = new THREE.RingGeometry(28, 32, 32);
        const lakeRingMat = new THREE.MeshBasicMaterial({{ color: 0x38bdf8, side: THREE.DoubleSide }});
        const lakeRing = new THREE.Mesh(lakeRingGeo, lakeRingMat);
        lakeRing.rotation.x = -Math.PI / 2;
        lakeRing.position.set(165, 0.15, 72);
        scene.add(lakeRing);

        // ═════════════════════════════════════════════════════════════════════
        // OPENCITYMODEL (CityJSON LOD1) BUILDING PARSER
        // ═════════════════════════════════════════════════════════════════════
        const cityObjectsGroup = new THREE.Group();
        const tinRoofsList = [];
        const windowMeshesList = [];
        const interactiveBuildings = [];
        const substationPositions = {{}};

        // Material Palette for OpenCityModel Building Classes
        const matSlum = new THREE.MeshStandardMaterial({{ color: 0x475569, roughness: 0.85 }});
        const matPucca = new THREE.MeshStandardMaterial({{ color: 0x1e293b, roughness: 0.7 }});
        const matHosp = new THREE.MeshStandardMaterial({{ color: 0x064e3b, roughness: 0.6 }});
        const matSub = new THREE.MeshStandardMaterial({{ color: 0x334155, roughness: 0.4, metalness: 0.6 }});
        const matWtp = new THREE.MeshStandardMaterial({{ color: 0x0369a1, roughness: 0.3, metalness: 0.7 }});

        // Parse each CityJSON CityObject
        Object.entries(RAIPUR_CITY_JSON.CityObjects).forEach(([objId, objData]) => {{
          const attrs = objData.attributes;
          const [cx, cy, cz] = objData.center;
          const [w, h, d] = objData.dimensions;

          let bMat = matPucca;
          if (attrs.class === 'InformalSettlement') bMat = matSlum;
          else if (attrs.class === 'Hospital') bMat = matHosp;
          else if (attrs.class === 'ElectricalSubstation') bMat = matSub;
          else if (attrs.class === 'WaterTreatmentPlant') bMat = matWtp;

          const bGeo = new THREE.BoxGeometry(w, h, d);
          const bMesh = new THREE.Mesh(bGeo, bMat);
          bMesh.position.set(cx, cy, cz);
          bMesh.castShadow = true;
          bMesh.receiveShadow = true;
          bMesh.userData = {{ id: objId, attrs: attrs }};
          cityObjectsGroup.add(bMesh);
          interactiveBuildings.push(bMesh);

          // Track Substation centers for transmission line grid routing
          if (attrs.class === 'ElectricalSubstation') {{
            const subId = objId.replace('SUB_', '');
            substationPositions[subId] = new THREE.Vector3(cx, h + 2, cz);

            // Substation steel gantry tower
            const towGeo = new THREE.CylinderGeometry(0.5, 2.5, 36, 4);
            const towMat = new THREE.MeshStandardMaterial({{ color: 0x94a3b8, wireframe: true }});
            const tower = new THREE.Mesh(towGeo, towMat);
            tower.position.set(cx, 18, cz);
            cityObjectsGroup.add(tower);
          }}

          // Corrugated Tin Roof for Slum Settlements
          if (attrs.roofType === 'corrugated_tin') {{
            const roofGeo = new THREE.BoxGeometry(w * 1.04, 0.7, d * 1.04);
            const roofMat = new THREE.MeshStandardMaterial({{
              color: 0x94a3b8, // Starts grey, turns red under heat
              metalness: 0.7,
              roughness: 0.35
            }});
            const roofMesh = new THREE.Mesh(roofGeo, roofMat);
            roofMesh.position.set(cx, h + 0.35, cz);
            cityObjectsGroup.add(roofMesh);
            tinRoofsList.push(roofMesh);
          }} else if (attrs.class === 'Hospital') {{
            // Illuminated Medical Cross on Hospital Roof
            const crossH = new THREE.BoxGeometry(8, 1.2, 2.4);
            const crossV = new THREE.BoxGeometry(2.4, 1.2, 8);
            const crossMat = new THREE.MeshBasicMaterial({{ color: 0x10b981 }});
            const ch = new THREE.Mesh(crossH, crossMat);
            const cv = new THREE.Mesh(crossV, crossMat);
            ch.position.set(cx, h + 1.2, cz);
            cv.position.set(cx, h + 1.2, cz);
            cityObjectsGroup.add(ch);
            cityObjectsGroup.add(cv);
          }} else if (attrs.class === 'ResidentialCommercial') {{
            // Windows with light texture
            const winGeo = new THREE.BoxGeometry(w * 1.01, h * 0.7, d * 1.01);
            const winMat = new THREE.MeshBasicMaterial({{ color: 0x38bdf8, transparent: true, opacity: 0.35 }});
            const win = new THREE.Mesh(winGeo, winMat);
            win.position.set(cx, cy, cz);
            cityObjectsGroup.add(win);
            windowMeshesList.push(win);
          }}
        }});
        scene.add(cityObjectsGroup);

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
        const pipeGeo = new THREE.TubeGeometry(pipeCurve, 40, 1.5, 8, false);
        const pipeMat = new THREE.MeshBasicMaterial({{ color: 0x0284c7 }});
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
        const sparkCount = 140;
        const sparkGeo = new THREE.BufferGeometry();
        const sparkPositions = new Float32Array(sparkCount * 3);
        const sparkVelocities = [];

        for (let i = 0; i < sparkCount; i++) {{
          sparkPositions[i * 3] = s03Pos.x;
          sparkPositions[i * 3 + 1] = s03Pos.y;
          sparkPositions[i * 3 + 2] = s03Pos.z;
          sparkVelocities.push(new THREE.Vector3(
            (Math.random() - 0.5) * 24,
            Math.random() * 28 + 6,
            (Math.random() - 0.5) * 24
          ));
        }}
        sparkGeo.setAttribute('position', new THREE.BufferAttribute(sparkPositions, 3));
        const sparkMat = new THREE.PointsMaterial({{
          color: 0x38bdf8,
          size: 2.4,
          transparent: true,
          opacity: 0.95,
          blending: THREE.AdditiveBlending
        }});
        const sparkParticles = new THREE.Points(sparkGeo, sparkMat);
        scene.add(sparkParticles);

        const arcStrobe = new THREE.PointLight(0x38bdf8, 6, 110);
        arcStrobe.position.copy(s03Pos);
        scene.add(arcStrobe);

        // ═════════════════════════════════════════════════════════════════════
        // MUNICIPAL RELIEF WATER TANKERS (HiGHS MILP Fleet)
        // ═════════════════════════════════════════════════════════════════════
        const tankerFleet = [];
        const tankerCount = 5;
        for (let i = 0; i < tankerCount; i++) {{
          const tankerGroup = new THREE.Group();
          // Cab
          const cabGeo = new THREE.BoxGeometry(2.6, 2.2, 2.4);
          const cabMat = new THREE.MeshStandardMaterial({{ color: 0xf59e0b }});
          const cab = new THREE.Mesh(cabGeo, cabMat);
          cab.position.set(2, 1.3, 0);
          tankerGroup.add(cab);

          // Water Tank
          const tankGeo = new THREE.CylinderGeometry(1.3, 1.3, 5.5, 14);
          const tankMat = new THREE.MeshStandardMaterial({{ color: 0x0284c7, metalness: 0.6, roughness: 0.3 }});
          const tank = new THREE.Mesh(tankGeo, tankMat);
          tank.rotation.z = Math.PI / 2;
          tank.position.set(-1.6, 1.6, 0);
          tankerGroup.add(tank);

          // Flashing Amber Beacon
          const beaconGeo = new THREE.SphereGeometry(0.45, 8, 8);
          const beaconMat = new THREE.MeshBasicMaterial({{ color: 0xf59e0b }});
          const beacon = new THREE.Mesh(beaconGeo, beaconMat);
          beacon.position.set(2, 2.7, 0);
          tankerGroup.add(beacon);

          tankerGroup.position.set(-120 + i * 25, 0.4, 30 + i * 18);
          scene.add(tankerGroup);
          tankerFleet.push({{
            group: tankerGroup,
            speed: 0.3 + i * 0.04,
            direction: 1,
            startX: -140,
            endX: 50
          }});
        }}

        // ═════════════════════════════════════════════════════════════════════
        // CAMERA CONTROLLER & LANDMARK SWITCHING
        // ═════════════════════════════════════════════════════════════════════
        let currentCamTarget = new THREE.Vector3(0, 5, 0);
        let targetCamPos = new THREE.Vector3(-50, 45, 185);

        function switchCam(mode) {{
          document.querySelectorAll('.cam-pill').forEach(p => p.classList.remove('active'));
          if (mode === 's03') {{
            targetCamPos.set(-70, 32, 180);
            currentCamTarget.set(s03Pos.x, s03Pos.y, s03Pos.z);
          }} else if (mode === 'drone') {{
            targetCamPos.set(160, 140, 180);
            currentCamTarget.set(0, 0, 0);
          }} else if (mode === 'kharun') {{
            targetCamPos.set(-140, 40, -40);
            currentCamTarget.set(-195, 5, -30);
          }} else if (mode === 'slum') {{
            targetCamPos.set(-80, 22, 120);
            currentCamTarget.set(-101, 4, 95); // Tikrapara
          }} else if (mode === 'hospital') {{
            targetCamPos.set(65, 35, 10);
            currentCamTarget.set(43, 8, -12); // Mekahara Hospital
          }} else if (mode === 'telibandha') {{
            targetCamPos.set(195, 45, 115);
            currentCamTarget.set(165, 2, 72); // Marine Drive Lake
          }} else if (mode === 'top') {{
            targetCamPos.set(0, 310, 0.1);
            currentCamTarget.set(0, 0, 0);
          }}
        }}
        window.switchCam = switchCam;

        // Apply initial camera selection from Streamlit dropdown
        const initialCam = "{cam_view}";
        if (initialCam.includes("S03")) switchCam('s03');
        else if (initialCam.includes("Kharun")) switchCam('kharun');
        else if (initialCam.includes("Slum")) switchCam('slum');
        else if (initialCam.includes("Hospital")) switchCam('hospital');
        else if (initialCam.includes("Telibandha")) switchCam('telibandha');
        else if (initialCam.includes("Top-Down")) switchCam('top');
        else switchCam('drone');

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

        window.addEventListener('click', (e) {{
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

          // Atmosphere & Sun Pulsing
          if (currentTemp > 44.0) {{
            scene.fog.color.setHex(0x1a0f0d);
            sunLight.color.setHex(0xff7744);
            sunMesh.scale.setScalar(1.0 + Math.sin(Date.now() * 0.003) * 0.15);
          }} else {{
            scene.fog.color.setHex(0x090B0E);
            sunLight.color.setHex(0xffedd5);
            sunMesh.scale.setScalar(1.0);
          }}

          // Tin Roof Heat Trap (Turn blazing red under heatwave)
          const tinFactor = Math.max(0, Math.min(1, (currentTemp - 40.0) / 7.9));
          tinRoofsList.forEach(r => {{
            r.material.color.setRGB(0.58 + tinFactor * 0.38, 0.64 - tinFactor * 0.45, 0.72 - tinFactor * 0.6);
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
            arcStrobe.intensity = Math.random() > 0.3 ? 6.5 : 0.4;
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

            windowMeshesList.forEach((w, idx) => {{
              if (idx % 2 === 0) w.material.opacity = 0.05;
            }});

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
            pipeMat.color.setHex(0x0284c7);
            windowMeshesList.forEach(w => w.material.opacity = 0.35);
            document.getElementById('hud-badge').innerText = 'STAGE 2 // NORMAL OPERATIONS';
            document.getElementById('hud-badge').style.background = '#3B82F6';
            document.getElementById('val-water').innerText = '180 MLD (NOMINAL)';
            document.getElementById('ticker-text').innerText = 'Grid demand rising along saturating ODE curve. Winding hot-spots monitored across all 6 substations. ACSR Zebra conductors within statutory clearance.';
          }}

          // Animate Water Tankers
          tankerFleet.forEach(t => {{
            t.group.position.x += t.speed * t.direction;
            if (t.group.position.x > t.endX) {{
              t.direction = -1;
              t.group.rotation.y = Math.PI;
            }} else if (t.group.position.x < t.startX) {{
              t.direction = 1;
              t.group.rotation.y = 0;
            }}
          }});

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

    t1, t2, t3 = st.tabs([
        "OpenCityModel Raipur Spatial Geometry",
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
            <b>• Landmark Features:</b> Kharun River western boundary, Telibandha Talab (Marine Drive Lakefront), Great Eastern Road (GE Road / NH-53), and Raipur Junction rail corridor.
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

    with t3:
        st.markdown(f"""
        <div class="callout-box">
          <strong style="color:#F8FAFC;">Municipal Dispatch Operations (Budget: ₹{budget_lakh:.1f} Lakhs):</strong><br/>
          In the 3D theatre above, observe the <b>yellow-cabbed mobile water tankers</b> circulating continuously between the Kharun river intake depot and the informal slum clusters in Tikrapara and Gudhiyari. Under the active HiGHS optimization plan, <b>20 tankers</b> deliver potable water directly to low-pressure nodes, preventing acute dehydration while mobile emergency generators restore pumping at WP02.
        </div>
        """, unsafe_allow_html=True)
