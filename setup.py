from distutils.core import setup
import py2exe

import Oe2sSLE_GUI as GUI


PY2EXE_VERBOSE=1

data = [('images', ['images/play.gif', 'images/stop.gif', 'images/pledgie-small.gif'])]

opts={
	"py2exe": {
        #"includes": "mod1, mod2",
        "dist_dir": "Oe2sSLE-"+str(GUI.Oe2sSLE_VERSION[0])+"."+str(GUI.Oe2sSLE_VERSION[1])+"."+str(GUI.Oe2sSLE_VERSION[2])+"-win-x86",
        "excludes": ["pdb", "doctest", "distutils"],
        "includes": ["tkinter", "pyglet.app", "pyglet.clock", "pyglet.resource"],
        #"bundle_files": 2,
        #"compressed": True,
        "optimize": 2
    }
}

setup(windows=['Oe2sSLE_GUI.py'],data_files=data,options=opts,
	  #zipfile=None
	  )