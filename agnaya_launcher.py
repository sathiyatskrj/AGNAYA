"""
AGNAYA - Adaptive Geospatial Network for heatwave Analytics and Yield Assessment
Raipur, Chhattisgarh | V3.0 Enterprise Multi-Model Operations Cockpit
Standalone Executable Launcher (Self-contained, Zero External Dependencies)
"""
import os
import sys
import time
import socket
import threading
import webbrowser
import multiprocessing

# Pre-import core C-extensions and web frameworks on the main thread
# This prevents race conditions and circular import errors when spawning background threads in frozen executables
import numpy as np
import pandas as pd
import plotly
import plotly.graph_objects as go
import plotly.express as px
import streamlit
import streamlit.web.bootstrap as bootstrap
import uvicorn
import fastapi
from api import app as fastapi_app

def is_port_in_use(port: int) -> bool:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(0.5)
            return s.connect_ex(('127.0.0.1', port)) == 0
    except Exception:
        return False

def find_available_port(start_port: int, max_attempts: int = 20) -> int:
    port = start_port
    while port < start_port + max_attempts:
        if not is_port_in_use(port):
            return port
        port += 1
    return start_port

def get_base_dir() -> str:
    """Return base extraction directory for PyInstaller frozen app or dev script."""
    if getattr(sys, 'frozen', False):
        return getattr(sys, '_MEIPASS', os.path.dirname(sys.executable))
    return os.path.dirname(os.path.abspath(__file__))

def start_fastapi_service(port: int):
    """Run FastAPI REST microservice in background daemon thread."""
    try:
        uvicorn.run(fastapi_app, host="127.0.0.1", port=port, log_level="warning")
    except Exception as e:
        print(f"[!] FastAPI background daemon note: {e}")

def open_browser_delayed(url: str, delay_sec: float = 2.5):
    """Auto-launch user default browser once web server is ready."""
    time.sleep(delay_sec)
    print(f"\n[+] Tactical Cockpit ready! Opening in default browser: {url}")
    try:
        webbrowser.open(url)
    except Exception as e:
        print(f"[!] Note on browser launch: {e}")

def main():
    multiprocessing.freeze_support()
    base_dir = get_base_dir()
    os.chdir(base_dir)
    
    if base_dir not in sys.path:
        sys.path.insert(0, base_dir)

    print("=" * 72)
    print("   AGNAYA V3.0 — Raipur Heatwave Intelligence & Grid Digital Twin")
    print("   Cascading Failure Simulation & Autonomous Decision Support System")
    print("   Unified Enterprise Standalone Edition (Self-Contained Executable)")
    print("=" * 72)
    print("\n[*] Initializing High-Performance Multi-Model Core...")

    # Determine free ports
    st_port = find_available_port(8501)
    api_port = find_available_port(8000)

    # 1. Start background FastAPI REST microservice
    print(f"[*] Starting background REST API on http://127.0.0.1:{api_port}/docs ...")
    t_api = threading.Thread(target=start_fastapi_service, args=(api_port,), daemon=True)
    t_api.start()

    # 2. Schedule auto-opening of browser
    cockpit_url = f"http://localhost:{st_port}"
    t_browser = threading.Thread(target=open_browser_delayed, args=(cockpit_url, 2.5), daemon=True)
    t_browser.start()

    # 3. Locate app.py script
    app_path = os.path.join(base_dir, "app.py")
    if not os.path.exists(app_path):
        # Fallback search
        candidate = os.path.join(os.path.dirname(sys.executable), "app.py")
        if os.path.exists(candidate):
            app_path = candidate

    print(f"[*] Starting AGNAYA Tactical Operations Cockpit on {cockpit_url} ...")
    print(f"[*] Running in-process with zero external Python runtime dependencies.")
    print("\n[!] Keep this console window open while operating AGNAYA.")
    print("[!] Press Ctrl+C in this console to shut down.\n")

    # 4. Run Streamlit directly on MAIN THREAD
    try:
        os.environ["STREAMLIT_GLOBAL_DEVELOPMENT_MODE"] = "false"
        os.environ["STREAMLIT_SERVER_PORT"] = str(st_port)
        os.environ["STREAMLIT_SERVER_HEADLESS"] = "true"

        import streamlit.config as st_config
        st_config.set_option("global.developmentMode", False)
        st_config.set_option("server.port", st_port)
        st_config.set_option("server.headless", True)
        st_config.set_option("browser.gatherUsageStats", False)
        st_config.set_option("server.enableCORS", False)
        st_config.set_option("server.enableXsrfProtection", False)

        bootstrap.run(
            main_script_path=app_path,
            is_hello=False,
            args=[],
            flag_options={
                "server_port": st_port,
                "server_headless": True,
                "global_developmentMode": False,
                "theme_base": "dark",
                "browser_gatherUsageStats": False,
                "server_enableCORS": False,
                "server_enableXsrfProtection": False
            }
        )
    except KeyboardInterrupt:
        print("\n[*] AGNAYA shutdown requested by user. Cleaning up and exiting...")
    except Exception as e:
        print(f"\n[!] Startup error: {e}")
        import traceback
        traceback.print_exc()
        input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()
