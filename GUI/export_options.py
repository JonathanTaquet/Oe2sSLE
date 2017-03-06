# -*- coding: utf-8 -*-
"""
Copyright (C) 2016-2017 Jonathan Taquet

This file is part of Oe2sSLE (Open e2sSample.all Library Editor).

Oe2sSLE is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Oe2sSLE is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Oe2sSLE.  If not, see <http://www.gnu.org/licenses/>
"""

import e2s_sample_all as e2s

import tkinter as tk

from GUI.widgets import ROCombobox

class ExportOptions:
    """e2sSample export options"""

    def __init__(self):
        # default values
        self.export_smpl = 1 # export loop info in smpl chunk
        self.export_cue = 1 # export slices info in cue chunk

class ExportOptionsDialog(tk.Toplevel):

    def __init__(self, parent, options, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.transient(parent)
        self.title('Export options')

        self.parent = parent
        self.options = options

        self.export_smpl = tk.IntVar()
        self.export_cue = tk.IntVar()
        self.export_smpl.set(options.export_smpl)
        self.export_cue.set(options.export_cue)

        fr = tk.Frame(self)

        tk.Checkbutton(
                fr,
                text="Export loop info in 'smpl' chunk",
                variable=self.export_smpl
            ).grid(row=0, column=0)
        tk.Checkbutton(
                fr,
                text="Export slices info in 'cue ' chunk",
                variable=self.export_cue
            ).grid(row=1, column=0)

        fr.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        fr = tk.Frame(self)

        box = tk.Frame(self)

        tk.Button(
                box,
                text="OK",
                width=10,
                command=self.ok,
                default=tk.ACTIVE
            ).pack(side=tk.LEFT, padx=5, pady=5)

        tk.Button(
                box,
                text="Cancel",
                width=10,
                command=self.cancel
            ).pack(side=tk.LEFT, padx=5, pady=5)

        self.bind("<Return>", self.ok)
        self.bind("<Escape>", self.cancel)

        box.pack()

        self.grab_set()

        # temporarily hide the window
        self.withdraw()
        self.update()
        width, height = (self.winfo_width(), self.winfo_height())
        self.minsize(width, height)
        px, py = (parent.winfo_rootx(), parent.winfo_rooty())
        pwidth, pheight = (parent.winfo_width(), parent.winfo_height())
        x, y = (px+pwidth/2-width/2, py+pheight/2-height/2)
        self.geometry("+{}+{}".format(int(x), int(y)))
        self.deiconify()

    def update_data(self):
        self.options.export_smpl = self.export_smpl.get()
        self.options.export_cue = self.export_cue.get()

    #
    # standard button semantics

    def ok(self, event=None):
        self.withdraw()
        self.update_idletasks()

        self.apply()

        self.cancel()

    def cancel(self, event=None):
        # put focus back to the parent window
        self.parent.focus_set()
        self.destroy()

    def apply(self):
        self.update_data()
