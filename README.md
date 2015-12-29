# Open e2sSample.all Library Editor (Oe2sSLE)

This is an editor for electribe sampler (e2s) sample library.
It allows library management and supports sample loops and slices editing.
You can also remove or replace factory samples with your own.

This code was developped for python 3.5, but shall be compatible with python 3.4 (because py2exe do no support python 3.5 yet).
Graphical user interface is using tkinter to reduce external dependencies. The only requierement is the media part of
[pyglet](https://bitbucket.org/pyglet/pyglet/wiki/Home) for audio sample listening (tested with pyglet 1.2.4):

`pip install pyglet`


Startup file is Oe2sSLE_GUI.py

Some screenshots:
---

![Main window screenshot](doc/images/screenshot_main.png?raw=true "Screen shot of the main interface window")

Screen shot of the main interface window

![Sample edit window screenshot 1](doc/images/screenshot_slice_edit_1.png?raw=true "Screen shot of the sample loop/sclices edition window: editing area for sample's and slices points")

Screen shot of the sample loop/sclices edition window: editing area for sample's and slices points

![Sample edit window screenshot 2](doc/images/screenshot_slice_edit_2.png?raw=true "Screen shot of the sample loop/sclices edition window: editing area for slices tempo")

Screen shot of the sample loop/sclices edition window: editing area for slices tempo



More documentation coming soon...
