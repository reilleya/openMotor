# -*- mode: python -*-

# Run with `pyinstaller --windowed --onedir`

from uilib.fileIO import appVersionStr

block_cipher = None

a = Analysis(['../main.py'],
             pathex=['../'],
             binaries=[],
             datas=[('../resources/oMFile256.icns', '.')],
             hiddenimports=['pywt._extensions._cwt'],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False,
             target_arch=['x86_64', 'arm64'])
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='openMotor',
          debug=False,
          bootloader_ignore_signals=False,
          argv_emulation=True,
          strip=False,
          upx=True,
          runtime_tmpdir=None,
          console=False)
coll = COLLECT(exe,
              a.binaries,
              a.zipfiles,
              a.datas,
              strip=False,
              upx=True,
              name='openMotor')
app = BUNDLE(coll,
             name='openMotor.app',
             icon='../resources/oMIconCycles.icns',
             version=appVersionStr,
             info_plist={
              'NSHighResolutionCapable': True,
              'CFBundleDocumentTypes': [
               {
                'CFBundleTypeName': 'openMotor Motor File',
                'CFBundleTypeExtensions': ['ric'],
                'CFBundleTypeRole': 'Editor',
                'CFBundleTypeIconFile': 'oMFile256',
                'LSHandlerRank': 'Owner',
               }
              ],
             },
             bundle_identifier=None)
