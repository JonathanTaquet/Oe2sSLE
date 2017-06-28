"""
Copyright (C) 2017 Jonathan Taquet

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

import tkinter as tk
import tkinter.ttk

from GUI.widgets import ROCombobox

class ExchangeSampleDialog(tk.Toplevel):
    def __init__(self, parent, smp, exchg_with, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.transient(parent)
        self.title('Exchange sample')

        self.parent = parent
        self.result = None
        self.exchg_with = exchg_with

        self.mix_var = tk.DoubleVar()

        body = tk.Frame(self)

        tk.Label(body, text="Exchange #{}: '{}' with: ".format(smp[0], smp[1])).pack(fill=tk.X)
        self.entryWith = ROCombobox(body, values=["#{}: '{}'".format(smp[0], smp[1]) for smp in exchg_with], width=24)
        self.entryWith.set("#{}: '{}'".format(smp[0], smp[1]))
        self.entryWith.pack()

        body.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        box = tk.Frame(self)

        w = tk.Button(box, text="OK", width=10, command=self.ok, default=tk.ACTIVE)
        w.pack(side=tk.LEFT, padx=5, pady=5)
        w = tk.Button(box, text="Cancel", width=10, command=self.cancel)
        w.pack(side=tk.LEFT, padx=5, pady=5)

        self.bind("<Return>", self.ok)
        self.bind("<Escape>", self.cancel)
        self.bind("<space>", lambda event: self.play())

        box.pack()

#        self.protocol("WM_DELETE_WINDOW", self.close)

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

        self.focus_set()
        self.grab_set()

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
        self.result = self.entryWith.current()