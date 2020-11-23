# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['main.py'],
             pathex=['P:\\GIT\\darkmode'],
             binaries=[],
             datas=[('greet.py', '.'), ('./icons/*', 'icons'), ('./config/*', 'config'), ('./gui/*', 'gui')],
             hiddenimports=[],
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
          [],
          exclude_binaries=True,
          name='Darkmode',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          icon='./icons/dm_on.ico',
          console=False )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='Darkmode for Windows')
