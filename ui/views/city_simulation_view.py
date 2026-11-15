"""
AGNAYA - 3D City Simulation & Causal Cascade Theatre (Mode 4)
Interactive Three.js WebGL digital twin rendering Raipur's urban grid, biometeorological heat buildup,
conductor catenary sag (IEEE 738), transformer winding arc flash (IEEE C57.91), Kharun water pump trip,
and municipal water tanker fleet dispatch.

MANDATORY DISCLAIMER: SIMULATION ONLY – NOT AN OFFICIAL WARNING.
"""

import streamlit as st
import streamlit.components.v1 as components


def render_city_simulation_view(
    T_peak: float,
    rel_humidity: float,
    duration_days: int,
    budget_lakh: float,
    tripped_id: str | None = "S03 Amanaka"
):
    st.markdown('<div class="section-head">3D Urban Digital Twin & Causal Cascade Simulation Theatre</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-subhead">Full 3D cinematic simulation demonstrating the complete physics lifecycle of a Raipur heatwave: '
        'from solar radiation buildup and IEEE 738 conductor catenary sag to transformer winding flashover at S03 Amanaka, '
        'cascading loss of Kharun River 180 MLD water pumping, and municipal tanker dispatch. '
        '<b>Simulation only &mdash; not an official warning.</b></div>',
        unsafe_allow_html=True
    )

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
    with c_cam:
        cam_view = st.selectbox(
            "Cinematic Camera Director:",
            [
                "Substation S03 Arc Fault Cam",
                "Cinematic Drone Orbit",
                "Kharun River 180 MLD Water Plant",
                "Tikrapara Slum Tin-Roof Trap",
                "Ambedkar Memorial Hospital",
                "Top-Down Urban Grid Blueprint"
            ],
            index=0
        )
    with c_spd:
        st.selectbox("Sim Speed:", ["1x Normal", "2x Accelerated", "5x Hyper-lapse"], index=0)
    with c_int:
        st.checkbox("Deploy Municipal Relief Fleet (HiGHS MILP)", value=True)

    # Mapping stage index
    stage_idx = 4
    if "Act 1" in sim_stage:
        stage_idx = 1
    elif "Act 2" in sim_stage:
        stage_idx = 2
    elif "Act 3" in sim_stage:
        stage_idx = 3
    elif "Act 4" in sim_stage:
        stage_idx = 4
    elif "Act 5" in sim_stage:
        stage_idx = 5
    elif "Act 6" in sim_stage:
        stage_idx = 6

    # Build the self-contained Three.js WebGL simulation HTML
    html_code = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8">
      <title>AGNAYA 3D City Simulation</title>
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
          background: rgba(16, 20, 28, 0.78);
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
          max-width: 340px;
          background: rgba(15, 23, 42, 0.85);
          backdrop-filter: blur(8px);
          border: 1px solid rgba(239, 68, 68, 0.3);
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

        /* Compass / Water Legend */
        .hud-legend {{
          position: absolute;
          bottom: 24px;
          right: 18px;
          background: rgba(15, 23, 42, 0.85);
          backdrop-filter: blur(8px);
          border: 1px solid rgba(255, 255, 255, 0.08);
          border-radius: 6px;
          padding: 8px 12px;
          font-size: 10.5px;
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
          <span class="hud-badge" id="hud-badge">STAGE 4 // ARC FAULT</span>
          <div>
            <div style="font-weight: 700; font-size: 13px;">RAIPUR MUNICIPAL & GRID SIMULATOR</div>
            <div style="font-size: 10.5px; color: #94A3B8;">IEEE Std C57.91 &middot; IEEE Std 738 &middot; CSERC 220/132 kV</div>
          </div>
        </div>
        <div class="hud-stats">
          <div class="hud-stat-item">
            <span class="hud-stat-label">Ambient Air (IMD)</span>
            <span class="hud-stat-val crit" id="val-temp">{T_peak:.1f}°C</span>
          </div>
          <div class="hud-stat-item">
            <span class="hud-stat-label">Grid Load (MW)</span>
            <span class="hud-stat-val crit" id="val-load">475.9 MW</span>
          </div>
          <div class="hud-stat-item">
            <span class="hud-stat-label">T-03 Hotspot</span>
            <span class="hud-stat-val crit" id="val-hotspot">134.8°C</span>
          </div>
          <div class="hud-stat-item">
            <span class="hud-stat-label">Kharun Pumping</span>
            <span class="hud-stat-val warn" id="val-water">90 MLD (WP02 TRIP)</span>
          </div>
          <div class="hud-stat-item">
            <span class="hud-stat-label">Relief Tankers</span>
            <span class="hud-stat-val cyan" id="val-tankers">20 Active</span>
          </div>
        </div>
      </div>

      <!-- Camera Angle Presets -->
      <div class="hud-cam-pills">
        <div class="cam-pill" onclick="switchCam('s03')">⚡ S03 Substation Arc Fault</div>
        <div class="cam-pill" onclick="switchCam('drone')">🚁 Cinematic Drone Flyover</div>
        <div class="cam-pill" onclick="switchCam('kharun')">💧 Kharun 180 MLD Water Plant</div>
        <div class="cam-pill" onclick="switchCam('slum')">🏚️ Tikrapara Tin-Roof Slum</div>
        <div class="cam-pill" onclick="switchCam('hospital')">🏥 Ambedkar Memorial Hospital</div>
        <div class="cam-pill" onclick="switchCam('top')">📐 Urban Blueprint Top-Down</div>
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
          <span id="ticker-time">14:32 IST // CASCADING FAULT IN PROGRESS</span>
        </div>
        <div id="ticker-text">
          S03 Amanaka 132/33 kV Transformer winding hotspot reached 134.8°C (Arrhenius F_AA = 18.2). High-voltage bushing arc flash triggered differential protection trip. Kharun River WP02 feeder de-energized!
        </div>
      </div>

      <!-- Legend -->
      <div class="hud-legend">
        <div class="legend-item"><div class="legend-color" style="background:#38BDF8;"></div><span>220/132 kV Transmission Grid</span></div>
        <div class="legend-item"><div class="legend-color" style="background:#0284C7;"></div><span>Kharun River 180 MLD Main</span></div>
        <div class="legend-item"><div class="legend-color" style="background:#EF4444;"></div><span>Tripped Substation & Spark Arc</span></div>
        <div class="legend-item"><div class="legend-color" style="background:#F59E0B;"></div><span>Municipal Relief Tanker Route</span></div>
        <div class="legend-item"><div class="legend-color" style="background:#10B981;"></div><span>Hospital Trauma / Cooling Shelter</span></div>
      </div>

      <!-- Simulation Core JavaScript -->
      <script>
        const initialStage = {stage_idx};
        let isPlaying = true;
        let simSpeed = 1.0;
        let simTimeHours = 48.0; // Starts at hour 48 (Arc trip)
        const maxTimeHours = 96.0;

        // Container & Renderer
        const container = document.getElementById('canvas-container');
        const scene = new THREE.Scene();
        scene.background = new THREE.Color(0x0a0d14);
        scene.fog = new THREE.FogExp2(0x0a0d14, 0.0035);

        const camera = new THREE.PerspectiveCamera(48, window.innerWidth / window.innerHeight, 1, 3000);
        camera.position.set(120, 95, 140);

        const renderer = new THREE.WebGLRenderer({{ antialias: true, alpha: false }});
        renderer.setSize(window.innerWidth, window.innerHeight);
        renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
        renderer.shadowMap.enabled = true;
        renderer.shadowMap.type = THREE.PCFSoftShadowMap;
        container.appendChild(renderer.domElement);

        const controls = new THREE.OrbitControls(camera, renderer.domElement);
        controls.enableDamping = true;
        controls.dampingFactor = 0.05;
        controls.maxPolarAngle = Math.PI / 2 - 0.04;
        controls.minDistance = 20;
        controls.maxDistance = 650;
        controls.target.set(0, 5, 0);

        // Lighting Rig
        const ambientLight = new THREE.AmbientLight(0x272d3d, 1.4);
        scene.add(ambientLight);

        const sunLight = new THREE.DirectionalLight(0xffedd5, 1.8);
        sunLight.position.set(150, 220, 100);
        sunLight.castShadow = true;
        sunLight.shadow.mapSize.width = 2048;
        sunLight.shadow.mapSize.height = 2048;
        sunLight.shadow.camera.near = 10;
        sunLight.shadow.camera.far = 600;
        sunLight.shadow.camera.left = -220;
        sunLight.shadow.camera.right = 220;
        sunLight.shadow.camera.top = 220;
        sunLight.shadow.camera.bottom = -220;
        scene.add(sunLight);

        // Heat Dome Pulsing Sun in Sky
        const sunGeo = new THREE.SphereGeometry(18, 32, 32);
        const sunMat = new THREE.MeshBasicMaterial({{ color: 0xff4500, wireframe: false }});
        const sunMesh = new THREE.Mesh(sunGeo, sunMat);
        sunMesh.position.set(220, 280, 160);
        scene.add(sunMesh);

        // Terrain Ground Plane
        const groundGeo = new THREE.PlaneGeometry(800, 800, 40, 40);
        const groundMat = new THREE.MeshStandardMaterial({{
          color: 0x0e131d,
          roughness: 0.9,
          metalness: 0.1
        }});
        const ground = new THREE.Mesh(groundGeo, groundMat);
        ground.rotation.x = -Math.PI / 2;
        ground.receiveShadow = true;
        scene.add(ground);

        // Grid Floor Lines
        const gridHelper = new THREE.GridHelper(700, 70, 0x1e293b, 0x141b27);
        gridHelper.position.y = 0.05;
        scene.add(gridHelper);

        // ═════════════════════════════════════════════════════════════════════
        // KHARUN RIVER (Water Lifeline Geometry)
        // ═════════════════════════════════════════════════════════════════════
        const riverCurve = new THREE.CatmullRomCurve3([
          new THREE.Vector3(-320, 0.2, -180),
          new THREE.Vector3(-180, 0.2, -110),
          new THREE.Vector3(-90, 0.2, 0),
          new THREE.Vector3(-130, 0.2, 120),
          new THREE.Vector3(-240, 0.2, 260)
        ]);
        const riverGeo = new THREE.TubeGeometry(riverCurve, 64, 18, 8, false);
        const riverMat = new THREE.MeshStandardMaterial({{
          color: 0x0284c7,
          roughness: 0.2,
          metalness: 0.8,
          transparent: true,
          opacity: 0.85
        }});
        const riverMesh = new THREE.Mesh(riverGeo, riverMat);
        riverMesh.scale.set(1, 0.05, 1);
        scene.add(riverMesh);

        // ═════════════════════════════════════════════════════════════════════
        // CITY BUILDINGS GENERATION (12 Zones)
        // ═════════════════════════════════════════════════════════════════════
        const buildingsGroup = new THREE.Group();
        const tinRoofsList = [];
        const windowsList = [];

        // Procedural blocks
        const zoneCenters = [
          {{ name: "Central", x: 20, z: -20, isSlum: false }},
          {{ name: "Pandri", x: 70, z: -60, isSlum: false }},
          {{ name: "Amanaka", x: -40, z: 40, isSlum: false }},
          {{ name: "Gudhiyari", x: -30, z: -70, isSlum: true }},
          {{ name: "Tikrapara", x: 30, z: 80, isSlum: true }},
          {{ name: "Tatibandh", x: -90, z: 90, isSlum: false }},
          {{ name: "Devendra Nagar", x: 60, z: 20, isSlum: false }},
          {{ name: "Birgaon", x: 90, z: -110, isSlum: true }}
        ];

        zoneCenters.forEach(z => {{
          const count = z.isSlum ? 22 : 14;
          for (let i = 0; i < count; i++) {{
            const ox = z.x + (Math.random() - 0.5) * 60;
            const oz = z.z + (Math.random() - 0.5) * 60;
            const w = z.isSlum ? 6 + Math.random() * 4 : 8 + Math.random() * 8;
            const d = z.isSlum ? 6 + Math.random() * 4 : 8 + Math.random() * 8;
            const h = z.isSlum ? 4 + Math.random() * 3 : 10 + Math.random() * 28;

            const bGeo = new THREE.BoxGeometry(w, h, d);
            const bMat = new THREE.MeshStandardMaterial({{
              color: z.isSlum ? 0x64748b : 0x1e293b,
              roughness: 0.8
            }});
            const bMesh = new THREE.Mesh(bGeo, bMat);
            bMesh.position.set(ox, h / 2, oz);
            bMesh.castShadow = true;
            bMesh.receiveShadow = true;
            buildingsGroup.add(bMesh);

            // Tin roof cap for informal slums
            if (z.isSlum) {{
              const roofGeo = new THREE.BoxGeometry(w * 1.05, 0.8, d * 1.05);
              const roofMat = new THREE.MeshStandardMaterial({{
                color: 0x94a3b8, // Starts grey, turns red under heat
                roughness: 0.4,
                metalness: 0.7
              }});
              const roofMesh = new THREE.Mesh(roofGeo, roofMat);
              roofMesh.position.set(ox, h + 0.4, oz);
              buildingsGroup.add(roofMesh);
              tinRoofsList.push(roofMesh);
            }} else {{
              // Windows on commercial buildings
              const winGeo = new THREE.BoxGeometry(w * 1.01, h * 0.7, d * 1.01);
              const winMat = new THREE.MeshBasicMaterial({{
                color: 0x38bdf8,
                transparent: true,
                opacity: 0.35
              }});
              const winMesh = new THREE.Mesh(winGeo, winMat);
              winMesh.position.set(ox, h / 2, oz);
              buildingsGroup.add(winMesh);
              windowsList.push(winMesh);
            }}
          }}
        }});
        scene.add(buildingsGroup);

        // ═════════════════════════════════════════════════════════════════════
        // DISTRICT HOSPITALS (Dr. B.R. Ambedkar Memorial & AIIMS)
        // ═════════════════════════════════════════════════════════════════════
        const hospitalGroup = new THREE.Group();
        const hospBaseGeo = new THREE.BoxGeometry(32, 20, 26);
        const hospBaseMat = new THREE.MeshStandardMaterial({{ color: 0x0f2b24, roughness: 0.6 }});
        const hospMesh = new THREE.Mesh(hospBaseGeo, hospBaseMat);
        hospMesh.position.set(50, 10, -10);
        hospMesh.castShadow = true;
        hospitalGroup.add(hospMesh);

        // Glowing Medical Cross on Hospital Roof
        const crossH = new THREE.BoxGeometry(10, 1.5, 3);
        const crossV = new THREE.BoxGeometry(3, 1.5, 10);
        const crossMat = new THREE.MeshBasicMaterial({{ color: 0x10b981 }});
        const chMesh = new THREE.Mesh(crossH, crossMat);
        const cvMesh = new THREE.Mesh(crossV, crossMat);
        chMesh.position.set(50, 20.8, -10);
        cvMesh.position.set(50, 20.8, -10);
        hospitalGroup.add(chMesh);
        hospitalGroup.add(cvMesh);
        scene.add(hospitalGroup);

        // ═════════════════════════════════════════════════════════════════════
        // KHARUN WATER TREATMENT PLANTS (WP01 180 MLD & WP02 Pumping)
        // ═════════════════════════════════════════════════════════════════════
        const waterPlantGroup = new THREE.Group();
        const wtpGeo = new THREE.CylinderGeometry(14, 14, 12, 24);
        const wtpMat = new THREE.MeshStandardMaterial({{ color: 0x0369a1, roughness: 0.4, metalness: 0.5 }});
        const wtp1 = new THREE.Mesh(wtpGeo, wtpMat);
        wtp1.position.set(-110, 6, 10);
        wtp1.castShadow = true;
        waterPlantGroup.add(wtp1);

        const wtp2 = new THREE.Mesh(wtpGeo, wtpMat);
        wtp2.position.set(-85, 6, 30);
        wtp2.castShadow = true;
        waterPlantGroup.add(wtp2);

        // Water Main Pipeline (Glowing blue pipe traversing city)
        const pipeCurve = new THREE.CatmullRomCurve3([
          new THREE.Vector3(-90, 2, 20),
          new THREE.Vector3(-40, 2, 10),
          new THREE.Vector3(10, 2, 0),
          new THREE.Vector3(45, 2, 60)
        ]);
        const pipeGeo = new THREE.TubeGeometry(pipeCurve, 32, 1.4, 8, false);
        const pipeMat = new THREE.MeshBasicMaterial({{ color: 0x0284c7 }});
        const pipeMesh = new THREE.Mesh(pipeGeo, pipeMat);
        waterPlantGroup.add(pipeMesh);
        scene.add(waterPlantGroup);

        // ═════════════════════════════════════════════════════════════════════
        // ELECTRICAL TRANSMISSION GRID & SUBSTATIONS (220 kV & S03 Arc)
        // ═════════════════════════════════════════════════════════════════════
        const gridGroup = new THREE.Group();
        const towers = [
          {{ id: "S01", x: 20, z: -30, name: "S01 Central (132 kV)" }},
          {{ id: "S02", x: 90, z: -80, name: "S02 Pandri (132 kV)" }},
          {{ id: "S03", x: -45, z: 35, name: "S03 Amanaka (132/33 kV - TRIP TARGET)" }},
          {{ id: "S04", x: -40, z: -80, name: "S04 Gudhiyari (132 kV)" }},
          {{ id: "S05", x: 40, z: 90, name: "S05 Tikrapara (132 kV)" }},
          {{ id: "RaipurMain", x: -110, z: -120, name: "Raipur Main (220 kV Bulk)" }}
        ];

        // Substation Buildings & Transformers
        const subStationMeshes = {{}};
        towers.forEach(t => {{
          // Substation switchyard yard
          const yardGeo = new THREE.BoxGeometry(16, 3, 16);
          const yardMat = new THREE.MeshStandardMaterial({{ color: 0x1f2937 }});
          const yard = new THREE.Mesh(yardGeo, yardMat);
          yard.position.set(t.x, 1.5, t.z);
          gridGroup.add(yard);

          // Transformer Tank with Radiator Fins
          const transGeo = new THREE.BoxGeometry(8, 7, 6);
          const transMat = new THREE.MeshStandardMaterial({{
            color: t.id === "S03" ? 0x991b1b : 0x374151,
            metalness: 0.6,
            roughness: 0.4
          }});
          const trans = new THREE.Mesh(transGeo, transMat);
          trans.position.set(t.x, 6, t.z);
          trans.castShadow = true;
          gridGroup.add(trans);
          subStationMeshes[t.id] = trans;

          // Steel Lattice Tower Framework
          const towGeo = new THREE.CylinderGeometry(0.6, 2.8, 38, 4);
          const towMat = new THREE.MeshStandardMaterial({{ color: 0x64748b, wireframe: true }});
          const towerMesh = new THREE.Mesh(towGeo, towMat);
          towerMesh.position.set(t.x, 19, t.z);
          gridGroup.add(towerMesh);
        }});

        // Overhead Transmission Lines with Catenary Sag (IEEE 738)
        const lineConnections = [
          ["RaipurMain", "S04"],
          ["RaipurMain", "S03"],
          ["S04", "S01"],
          ["S03", "S01"],
          ["S01", "S02"],
          ["S03", "S05"]
        ];

        const catenaryLines = [];
        lineConnections.forEach(([fromId, toId]) => {{
          const tFrom = towers.find(t => t.id === fromId);
          const tTo = towers.find(t => t.id === toId);
          const p1 = new THREE.Vector3(tFrom.x, 32, tFrom.z);
          const p2 = new THREE.Vector3(tTo.x, 32, tTo.z);

          // Midpoint with dynamic sag
          const midX = (p1.x + p2.x) / 2;
          const midZ = (p1.z + p2.z) / 2;
          const curve = new THREE.QuadraticBezierCurve3(
            p1,
            new THREE.Vector3(midX, 22, midZ), // Sags down to y=22
            p2
          );
          const pts = curve.getPoints(24);
          const lineGeo = new THREE.BufferGeometry().setFromPoints(pts);
          const lineMat = new THREE.LineBasicMaterial({{
            color: (fromId === "S03" || toId === "S03") ? 0xff3366 : 0x38bdf8,
            linewidth: 2
          }});
          const lineMesh = new THREE.Line(lineGeo, lineMat);
          gridGroup.add(lineMesh);
          catenaryLines.push({{ mesh: lineMesh, fromId, toId, p1, p2, midX, midZ }});
        }});
        scene.add(gridGroup);

        // ═════════════════════════════════════════════════════════════════════
        // ELECTRICAL ARC FLASH SHORT-CIRCUIT PARTICLE SYSTEM (At S03 Amanaka)
        // ═════════════════════════════════════════════════════════════════════
        const s03Pos = new THREE.Vector3(-45, 10, 35);
        const sparkCount = 120;
        const sparkGeo = new THREE.BufferGeometry();
        const sparkPositions = new Float32Array(sparkCount * 3);
        const sparkVelocities = [];

        for (let i = 0; i < sparkCount; i++) {{
          sparkPositions[i * 3] = s03Pos.x;
          sparkPositions[i * 3 + 1] = s03Pos.y;
          sparkPositions[i * 3 + 2] = s03Pos.z;
          sparkVelocities.push(new THREE.Vector3(
            (Math.random() - 0.5) * 22,
            Math.random() * 26 + 6,
            (Math.random() - 0.5) * 22
          ));
        }}
        sparkGeo.setAttribute('position', new THREE.BufferAttribute(sparkPositions, 3));
        const sparkMat = new THREE.PointsMaterial({{
          color: 0x38bdf8,
          size: 2.2,
          transparent: true,
          opacity: 0.95,
          blending: THREE.AdditiveBlending
        }});
        const sparkParticles = new THREE.Points(sparkGeo, sparkMat);
        scene.add(sparkParticles);

        // Arc Flash Strobe Light at S03
        const arcStrobe = new THREE.PointLight(0x38bdf8, 5, 90);
        arcStrobe.position.copy(s03Pos);
        scene.add(arcStrobe);

        // ═════════════════════════════════════════════════════════════════════
        // MUNICIPAL RELIEF FLEET: WATER TANKERS ON ROAD
        // ═════════════════════════════════════════════════════════════════════
        const tankerFleet = [];
        const tankerCount = 4;
        for (let i = 0; i < tankerCount; i++) {{
          const tankerGroup = new THREE.Group();
          // Cab
          const cabGeo = new THREE.BoxGeometry(2.4, 2, 2.2);
          const cabMat = new THREE.MeshStandardMaterial({{ color: 0xf59e0b }});
          const cab = new THREE.Mesh(cabGeo, cabMat);
          cab.position.set(2, 1.2, 0);
          tankerGroup.add(cab);

          // Water Tank Cylinder
          const tankGeo = new THREE.CylinderGeometry(1.2, 1.2, 5, 12);
          const tankMat = new THREE.MeshStandardMaterial({{ color: 0x0284c7, metalness: 0.5, roughness: 0.3 }});
          const tank = new THREE.Mesh(tankGeo, tankMat);
          tank.rotation.z = Math.PI / 2;
          tank.position.set(-1.4, 1.5, 0);
          tankerGroup.add(tank);

          // Amber Beacon
          const beaconGeo = new THREE.SphereGeometry(0.4, 8, 8);
          const beaconMat = new THREE.MeshBasicMaterial({{ color: 0xf59e0b }});
          const beacon = new THREE.Mesh(beaconGeo, beaconMat);
          beacon.position.set(2, 2.5, 0);
          tankerGroup.add(beacon);

          tankerGroup.position.set(-80 + i * 20, 0.4, 20 + i * 14);
          scene.add(tankerGroup);
          tankerFleet.push({{
            group: tankerGroup,
            speed: 0.25 + i * 0.05,
            direction: 1,
            startX: -90,
            endX: 30,
            z: 20 + i * 16
          }});
        }}

        // ═════════════════════════════════════════════════════════════════════
        // CAMERA MODES & SWITCHING
        // ═════════════════════════════════════════════════════════════════════
        let currentCamTarget = new THREE.Vector3(0, 5, 0);
        let targetCamPos = new THREE.Vector3(120, 95, 140);

        function switchCam(mode) {{
          document.querySelectorAll('.cam-pill').forEach(p => p.classList.remove('active'));
          if (mode === 's03') {{
            targetCamPos.set(-25, 28, 65);
            currentCamTarget.set(-45, 10, 35);
          }} else if (mode === 'drone') {{
            targetCamPos.set(130, 110, 150);
            currentCamTarget.set(0, 0, 0);
          }} else if (mode === 'kharun') {{
            targetCamPos.set(-70, 35, 70);
            currentCamTarget.set(-100, 5, 20);
          }} else if (mode === 'slum') {{
            targetCamPos.set(50, 22, 105);
            currentCamTarget.set(30, 4, 80);
          }} else if (mode === 'hospital') {{
            targetCamPos.set(75, 30, 20);
            currentCamTarget.set(50, 10, -10);
          }} else if (mode === 'top') {{
            targetCamPos.set(0, 260, 0.1);
            currentCamTarget.set(0, 0, 0);
          }}
        }}

        // Auto-initialize camera to user's selected mode
        window.switchCam = switchCam;

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

        // Set camera angle based on dropdown selection
        const camViewSel = "{cam_view}";
        if (camViewSel.includes("S03")) switchCam('s03');
        else if (camViewSel.includes("Kharun")) switchCam('kharun');
        else if (camViewSel.includes("Slum")) switchCam('slum');
        else if (camViewSel.includes("Hospital")) switchCam('hospital');
        else if (camViewSel.includes("Top-Down")) switchCam('top');
        else switchCam('drone');

        // ═════════════════════════════════════════════════════════════════════
        // MAIN ANIMATION LOOP
        // ═════════════════════════════════════════════════════════════════════
        let clock = new THREE.Clock();

        function animate() {{
          requestAnimationFrame(animate);
          const delta = clock.getDelta();

          // Advance simulation timeline if playing
          if (isPlaying) {{
            simTimeHours += (delta * 1.5 * simSpeed);
            if (simTimeHours > maxTimeHours) simTimeHours = 0.0;
          }}

          // Smooth Camera Lerp
          camera.position.lerp(targetCamPos, 0.04);
          controls.target.lerp(currentCamTarget, 0.04);
          controls.update();

          // Compute dynamic metrics based on simTimeHours (0h to 96h)
          // Peak heat and arc fault happens between hour 40 and 60
          const tProgress = simTimeHours / maxTimeHours;
          document.getElementById('scrubber-fill').style.width = (tProgress * 100) + '%';
          document.getElementById('label-curr-time').innerText = 'Hour ' + simTimeHours.toFixed(1) + ':00';

          const isCrisis = simTimeHours >= 36.0 && simTimeHours <= 68.0;
          const isPostRecovery = simTimeHours > 68.0;

          // Ambient Temp curve: 38°C -> 47.9°C at peak -> 41°C
          let currentTemp = 38.0;
          if (simTimeHours <= 48.0) {{
            currentTemp = 38.0 + (simTimeHours / 48.0) * 9.9;
          }} else {{
            currentTemp = 47.9 - ((simTimeHours - 48.0) / 48.0) * 7.5;
          }}

          // Demand curve
          let currentLoad = 310.0 + (currentTemp - 38.0) * 16.5;

          // Transformer Hotspot
          let tHotspot = 85.0 + (currentTemp - 38.0) * 5.2;

          // HUD Updates
          document.getElementById('val-temp').innerText = currentTemp.toFixed(1) + '°C';
          document.getElementById('val-load').innerText = currentLoad.toFixed(0) + ' MW';
          document.getElementById('val-hotspot').innerText = tHotspot.toFixed(1) + '°C';

          // Sun color & sky fog interpolation based on heat
          if (currentTemp > 44.0) {{
            scene.fog.color.setHex(0x1a0f0d);
            sunLight.color.setHex(0xff7744);
            sunMesh.scale.setScalar(1.0 + Math.sin(Date.now() * 0.003) * 0.15);
          }} else {{
            scene.fog.color.setHex(0x0a0d14);
            sunLight.color.setHex(0xffedd5);
            sunMesh.scale.setScalar(1.0);
          }}

          // Tin roofs heat up: turn blazing reddish-orange under extreme temperature
          const tinColorFactor = Math.max(0, Math.min(1, (currentTemp - 40.0) / 7.9));
          tinRoofsList.forEach(r => {{
            r.material.color.setRGB(0.58 + tinColorFactor * 0.38, 0.64 - tinColorFactor * 0.45, 0.72 - tinColorFactor * 0.6);
          }});

          // Conductor catenary sag (IEEE 738 thermal expansion)
          const sagAmount = (currentTemp - 38.0) * 0.35; // lines sag downwards
          catenaryLines.forEach(cl => {{
            const sagY = 22 - sagAmount;
            const curve = new THREE.QuadraticBezierCurve3(
              cl.p1,
              new THREE.Vector3(cl.midX, sagY, cl.midZ),
              cl.p2
            );
            const pts = curve.getPoints(24);
            cl.mesh.geometry.setFromPoints(pts);
          }});

          // ARC FLASH ANIMATION AT S03 (Active when hotspot > 125°C)
          const isArcActive = tHotspot >= 125.0;
          if (isArcActive) {{
            arcStrobe.intensity = Math.random() > 0.3 ? 6.0 : 0.5;
            arcStrobe.color.setHex(Math.random() > 0.5 ? 0x38bdf8 : 0xff3366);

            // Animate spark particles
            const positions = sparkParticles.geometry.attributes.position.array;
            for (let i = 0; i < sparkCount; i++) {{
              positions[i * 3] += sparkVelocities[i].x * delta;
              positions[i * 3 + 1] += sparkVelocities[i].y * delta;
              positions[i * 3 + 2] += sparkVelocities[i].z * delta;

              // Reset spark if it falls or travels too far
              if (positions[i * 3 + 1] < 2 || positions[i * 3 + 1] > 40) {{
                positions[i * 3] = s03Pos.x + (Math.random() - 0.5) * 4;
                positions[i * 3 + 1] = s03Pos.y + Math.random() * 2;
                positions[i * 3 + 2] = s03Pos.z + (Math.random() - 0.5) * 4;
              }}
            }}
            sparkParticles.geometry.attributes.position.needsUpdate = true;
            sparkParticles.visible = true;

            // Blackout effects: turn off windows in Amanaka/Gudhiyari
            windowsList.forEach((w, idx) => {{
              if (idx % 2 === 0) w.material.opacity = 0.05; // blackout
            }});

            // Kharun WP02 goes dead
            pipeMat.color.setHex(0xef4444); // Empty water pipe
            document.getElementById('hud-badge').innerText = 'STAGE 4 // ARC FLASH TRIP';
            document.getElementById('hud-badge').style.background = '#EF4444';
            document.getElementById('val-water').innerText = '90 MLD (WP02 OUTAGE)';
            document.getElementById('ticker-text').innerText = 'S03 Amanaka Transformer T-03 tripped on overtemperature flashover! Kharun WP02 pump lost feeder power. Tikrapara slum water pressure zero.';
          }} else if (isPostRecovery) {{
            arcStrobe.intensity = 0;
            sparkParticles.visible = false;
            pipeMat.color.setHex(0x10b981); // Recovered
            document.getElementById('hud-badge').innerText = 'STAGE 6 // MUNICIPAL RECOVERY';
            document.getElementById('hud-badge').style.background = '#10B981';
            document.getElementById('val-water').innerText = '165 MLD (DG RESTORED)';
            document.getElementById('ticker-text').innerText = 'Mobile DG set operational at Kharun WP02. 20 potable water tankers actively relieving Tikrapara & Gudhiyari wards. System resilience Q(t) rebounding.';
          }} else {{
            arcStrobe.intensity = 0;
            sparkParticles.visible = false;
            pipeMat.color.setHex(0x0284c7);
            windowsList.forEach(w => w.material.opacity = 0.35);
            document.getElementById('hud-badge').innerText = 'STAGE 2 // NORMAL OPERATIONS';
            document.getElementById('hud-badge').style.background = '#3B82F6';
            document.getElementById('val-water').innerText = '180 MLD (NOMINAL)';
            document.getElementById('ticker-text').innerText = 'Grid demand rising along saturating ODE curve. Winding hot-spots monitored across all 6 substations. ACSR Zebra conductors within statutory clearance.';
          }}

          // Animate Relief Water Tankers driving on streets
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

        // Responsive Resizing
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
    st.markdown('<div class="section-head">Causal Engineering Narrative & Scientific Foundations</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-subhead">Grounding the 3D theatre in IEEE, CSERC, and biometeorological standards: '
        'how macroclimate extremes propagate through interconnected physical infrastructure.</div>',
        unsafe_allow_html=True
    )

    t1, t2, t3 = st.tabs([
        "6-Stage Causal Storyboard",
        "Physical Twin Telemetry Breakdown",
        "Municipal Intervention & Tanker Dispatch"
    ])

    with t1:
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

        c_a1, c_a2 = st.columns(2)
        with c_a1:
            st.markdown("""
            <div class="bento-tile tile-heat" style="margin-bottom:12px;">
              <div class="stat-eyebrow">Act 1 to 3: Macroclimate to Grid Strain</div>
              <div style="font-size:12.5px;color:#CBD5E1;line-height:1.6;margin-top:6px;">
                <b>• Atmospheric Radiation:</b> Clear skies and adiabatic subsidence over central India elevate ambient air to 47.9°C (matching Raipur's historical all-time peak on May 28, 2024).<br/>
                <b>• Saturating Demand ODE:</b> Air conditioning penetration triggers a non-linear load surge from 310 MW to 475.9 MW, piercing the contracted summer baseline of 420 MW.<br/>
                <b>• IEEE Std 738-2012 Dynamic Line Sag:</b> ACSR Zebra overhead conductors experience thermal elongation; clearance above roadways reduces from nominal 7.8 m toward statutory minimum 6.1 m.
              </div>
            </div>
            """, unsafe_allow_html=True)

        with c_a2:
            st.markdown("""
            <div class="bento-tile tile-grid" style="margin-bottom:12px;">
              <div class="stat-eyebrow">Act 4 to 6: Arc Fault & Municipal Response</div>
              <div style="font-size:12.5px;color:#CBD5E1;line-height:1.6;margin-top:6px;">
                <b>• IEEE Std C57.91 Clause 7 Arrhenius Aging:</b> Transformer winding hot-spot at S03 Amanaka reaches 134.8°C, accelerating thermal aging rate <i>F<sub>AA</sub></i> to 18.2× nominal. Winding insulation flashover triggers differential protection trip.<br/>
                <b>• Cascading Lifeline Severance:</b> Kharun River Pumping Station WP02 (without on-site backup DG) trips immediately, cutting potable water transmission into Gudhiyari and Tikrapara.<br/>
                <b>• HiGHS MILP Intervention:</b> Municipal deployment of 20 mobile water tankers (200 kL/day) and 3 mobile DG sets at WP02 restores minimum survival lifelines within 6 hours.
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
