import os
...
a = Analysis(['Link_Checker_2.3.py'],
             pathex=['E:\\work\\project\\python\\test'],
             binaries=[],
             datas=[],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=None,
             noarchive=False)
...
pyz = PYZ(a.pure, a.zipped_data,
             cipher=None,
             )
...
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='Link_Checker_2.3',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=False, 
          icon='E:/WORK/project\Python/test/icon.ico',  
          )
