# -*- mode: python ; coding: utf-8 -*-
import os
import sys
from PyInstaller.utils.hooks import collect_all, copy_metadata

block_cipher = None

# Base assets and application files
datas = [
    ('app.py', '.'),
    ('api.py', '.'),
    ('styles.css', '.'),
    ('.streamlit', '.streamlit'),
    ('models', 'models'),
    ('data', 'data'),
    ('assets', 'assets'),
]

binaries = []
hiddenimports = [
    'uvicorn.logging',
    'uvicorn.loops',
    'uvicorn.loops.auto',
    'uvicorn.protocols',
    'uvicorn.protocols.http',
    'uvicorn.protocols.http.auto',
    'uvicorn.lifespan',
    'uvicorn.lifespan.on',
    'streamlit.runtime.scriptrunner.magic_expressions',
    'streamlit.web.bootstrap',
    'streamlit.web.server.server',
    'scipy.spatial.transform._rotation_groups',
    'scipy.special._special_ufuncs',
]

packages_to_bundle = [
    'streamlit',
    'streamlit_folium',
    'folium',
    'branca',
    'altair',
    'plotly',
    'pydantic',
    'pydantic_core',
    'fastapi',
    'uvicorn',
    'starlette',
    'networkx',
    'pulp',
    'scipy',
    'pandas',
    'numpy',
]

for pkg in packages_to_bundle:
    try:
        d, b, h = collect_all(pkg)
        datas += d
        binaries += b
        hiddenimports += h
    except Exception as e:
        print(f"Warning: collect_all for {pkg}: {e}")

# Copy dist-info metadata
for mp in ['streamlit', 'altair', 'plotly', 'pandas', 'numpy', 'fastapi', 'pydantic', 'scipy', 'packaging']:
    try:
        datas += copy_metadata(mp)
    except Exception:
        pass

hiddenimports = list(set(hiddenimports))

a = Analysis(
    ['agnaya_launcher.py'],
    pathex=['.'],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['tkinter'],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='AGNAYA',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/agnaya_logo.ico',
)
