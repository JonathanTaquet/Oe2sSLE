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
        "includes": ["tkinter","imp"],
        "bundle_files": 2,
        #"compressed": True,
        "optimize": 2
    }
}

class Target:
    def __init__(self, **kw):
        self.__dict__.update(kw)
        self.version = str(GUI.Oe2sSLE_VERSION[0])+"."+str(GUI.Oe2sSLE_VERSION[1])+"."+str(GUI.Oe2sSLE_VERSION[2])
        self.copyright = "Copyright (C) 2015-2016 Jonathan Taquet"
        self.name = "Oe2sSLE"

target = Target(
    description = "Open e2sSample.all Library Editor for Electribe Sampler",
    script = 'Oe2sSLE_GUI.py')

setup(script_args=['py2exe'],
      windows=[target],data_files=data,options=opts,
	  zipfile=None
	  )