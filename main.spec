# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['main.py'],
    pathex=['C:\\Users\\Elias6970\\Desktop\\archivo\\projecto\\'],
    binaries=[],
    datas=[('data\\img\\icon.ico','data'),('data\\img\\rotate_left.png','data'),('data\\img\\rotate_right.png','data'),('data\\portada_dossier_partituras.pdf','data')],
    hiddenimports=['PyQt5', 'PyQtWebEngine', 'openpyxl', 'xlrd', 'unidecode', 'rarfile', 'reportlab', 'PyPDF2', 'pdf2image'],
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
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['data/img/icon.ico']
)
