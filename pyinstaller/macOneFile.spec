# -*- mode: python -*-

# Run with `pyinstaller --windowed --onefile`

from uilib.fileIO import appVersionStr

block_cipher = None

a = Analysis(['../main.py'],
             pathex=['../'],
             binaries=[],
             datas=[],
             hiddenimports=['pywt._extensions._cwt'],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='openMotor',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          runtime_tmpdir=None,
          console=False )
app = BUNDLE(exe,
             name='openMotor.app',
             icon='../resources/oMIconCycles.icns',
             version=appVersionStr,
             info_plist={
              'NSHighResolutionCapable': True,
             },
             bundle_identifier=None)
