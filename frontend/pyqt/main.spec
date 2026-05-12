# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('resources/images/edit.png', 'resources/images'),
        ('resources/images/icon.ico', 'resources/images'),
        ('resources/images/refresh.png', 'resources/images'),
        ('resources/images/rotate_left.png', 'resources/images'),
        ('resources/images/rotate_right.png', 'resources/images'),
        ('resources/images/trash.png', 'resources/images'),
        ('resources/translations/ca_VA/compiled/ca_VA.qm', 'resources/translations/ca_VA/compiled'),
        ('resources/translations/en_US/compiled/en_US.qm', 'resources/translations/en_US/compiled'),
        ('resources/translations/es_ES/compiled/es_ES.qm', 'resources/translations/es_ES/compiled')
        ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='Gestor_archivo_amvr',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='resources/images/icon.ico'
)
