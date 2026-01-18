# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[('C:\\Program Files\\unrar\\UnRAR.exe','.')],
    datas=[
        ('data\\img\\edit.png','data\\img'),
        ('data\\img\\icon.ico','data\\img'),
        ('data\\img\\refresh.png','data\\img'),
        ('data\\img\\rotate_left.png','data\\img'),
        ('data\\img\\rotate_right.png','data\\img'),
        ('data\\img\\trash.png','data\\img'),
        ('data\\portada_dossier_partituras.pdf','data'),
        ('translate\\ca_VA\\compiled\\ca_VA.qm','translate\\ca_VA\\compiled'),
        ('translate\\en_US\\compiled\\en_US.qm','translate\\en_US\\compiled'),
        ('translate\\es_ES\\compiled\\es_ES.qm','translate\\es_ES\\compiled')
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
    icon='data/img/icon.ico'
)
