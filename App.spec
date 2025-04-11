# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['src/main.py'],
    pathex=[],
    binaries=[],
    datas=[('src/modules', 'modules')],  # モジュールを含める
    hiddenimports=[
        'modules.main_window', 
        'pydantic.deprecated.decorator',
        'pydantic.deprecated',
        'pydantic.json',
        'langchain_core',
        'langchain_openai',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
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
    name='DocumentEditorAI',
    debug=False,  # デバッグ時に有効にする
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # デバッグ時に有効にしても良い
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['app-icon.ico'],
)
app = BUNDLE(
    exe,
    name='DocumentEditorAI.app',
    icon='app-icon.ico',
    bundle_identifier=None,
)
