# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_dynamic_libs

binaries = [('C:\\\\Program Files\\\\VideoLAN\\\\VLC\\\\libvlc.dll', '.'), ('C:\\\\Program Files\\\\VideoLAN\\\\VLC\\\\libvlccore.dll', '.')]
binaries += collect_dynamic_libs('D:\\downloads\\Python312')


a = Analysis(
    ['run.py'],
    pathex=[],
    binaries=binaries,
    datas=[('F:\\\\jarvis\\\\www\\\\assets\\\\images\\\\IronMan-ЕnergoReaktor.jpg', 'www/assets/images'), ('F:\\\\jarvis\\\\device.bat', '.'), ('F:\\\\jarvis\\\\envcharlie\\\\Lib\\\\site-packages\\\\pvporcupine\\\\resources\\\\keyword_files', 'pvporcupine/resources/keyword_files'), ('F:\\\\jarvis\\\\www', 'www'), ('F:\\\\jarvis\\\\www\\\\assets\\\\audio', 'www/assets/audio'), ('F:\\\\jarvis\\\\www\\\\assets\\\\images', 'www/assets/images'), ('F:\\\\jarvis\\\\www\\\\assets\\\\images\\\\hack.png', 'www/assets/images'), ('F:\\\\jarvis\\\\www\\\\assets\\\\vendore', 'www/assets/vendore'), ('F:\\\\jarvis\\\\envcharlie\\\\Lib\\\\site-packages\\\\mediapipe\\\\modules\\\\face_landmark', 'mediapipe/modules/face_landmark'), ('F:\\\\jarvis\\\\envcharlie\\\\Lib\\\\site-packages\\\\mediapipe\\\\modules\\\\hand_landmark', 'mediapipe/modules/hand_landmark'), ('F:\\\\jarvis\\\\envcharlie\\\\Lib\\\\site-packages\\\\mediapipe\\\\modules\\\\palm_detection', 'mediapipe/modules/palm_detection'), ('F:\\\\jarvis\\\\powerpoint\\\\Designs', 'powerpoint/Designs')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
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
    name='run',
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
    icon=['F:\\jarvis\\www\\assets\\images\\IronMan-ЕnergoReaktor.jpg'],
)
