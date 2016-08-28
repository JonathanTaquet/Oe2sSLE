# -*- mode: python -*-

from importlib.machinery import SourceFileLoader

version = SourceFileLoader("module.name", os.path.abspath(".")+os.sep+"version.py").load_module()
Oe2sSLE_VERSION = version.Oe2sSLE_VERSION

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)
    
    
block_cipher = None


added_files = [
    ( 'images','images'),
    ]

a = Analysis(['Oe2sSLE_GUI.py'],
             pathex=['.'],
             binaries=None,
             datas=added_files,
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)

pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='Oe2sSLE-'+str(Oe2sSLE_VERSION[0])+'.'+str(Oe2sSLE_VERSION[1])+'.'+str(Oe2sSLE_VERSION[2])+'-win-x86',
          debug=False,
          strip=False,
          upx=True,
          console=False )
