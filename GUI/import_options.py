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


class ImportOptions:
    def __init__(self):
        self.osc_cat = 'User'
        self.loop_type = 0
        self.plus_12_db = 0
        self.force_osc_cat = 0
        self.force_loop_type = 0
        self.force_plus_12_db = 0
        self.smp_num_from = 19


osc_cat_strs = tuple(
    e2s.esli_OSC_cat_to_str[k]
    for k in sorted(e2s.esli_OSC_cat_to_str))

loop_type = {
    0: '1-shot',
    1: 'full loop'
}
loop_type_from_str = {v: k for k, v in loop_type.items()}
loop_type_strs = tuple(loop_type[k] for k in sorted(loop_type))

plus_12_db = {
    0: '+0dB',
    1: '+12dB'
}
plus_12_db_from_str = {v: k for k, v in plus_12_db.items()}
plus_12_db_strs = tuple(plus_12_db[k] for k in sorted(plus_12_db))


class ImportOptionsDialog(tk.Toplevel):

    def __init__(self, parent, options, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.transient(parent)
        self.title('Import options')

        self.parent = parent
        self.options = options

        self.loop_type = tk.StringVar()
        self.plus_12_db = tk.StringVar()
        self.osc_cat = tk.StringVar()
        self.loop_type.set(loop_type[options.loop_type])
        self.plus_12_db.set(plus_12_db[options.plus_12_db])
        self.osc_cat.set(options.osc_cat)

        self.force_osc_cat = tk.IntVar()
        self.force_loop_type = tk.IntVar()
        self.force_plus_12_db = tk.IntVar()
        self.force_osc_cat.set(options.force_osc_cat)
        self.force_loop_type.set(options.force_loop_type)
        self.force_plus_12_db.set(options.force_plus_12_db)

        self.smp_num_from = tk.IntVar()
        self.smp_num_from.set(options.smp_num_from)

        fr = tk.Frame(self)

        tk.Label(fr, text="OSC Cat.").grid(row=0, column=1)
        tk.Label(fr, text="1-shot").grid(row=0, column=2)
        tk.Label(fr, text="+12dB").grid(row=0, column=3)

        tk.Label(fr, text="Default value :").grid(row=1, column=0, sticky='E')
        tk.Label(fr, text="Force to reset :").grid(row=2, column=0, sticky='E')

        ROCombobox(
                fr,
                values=osc_cat_strs,
                width=8,
                textvariable=self.osc_cat
            ).grid(row=1, column=1)
        ROCombobox(
                fr,
                values=loop_type_strs,
                width=8,
                textvariable=self.loop_type
            ).grid(row=1, column=2)
        ROCombobox(
                fr,
                values=plus_12_db_strs,
                width=8,
                textvariable=self.plus_12_db
            ).grid(row=1, column=3)

        tk.Checkbutton(
                fr,
                variable=self.force_osc_cat
            ).grid(row=2, column=1)
        tk.Checkbutton(
                fr,
                variable=self.force_loop_type
            ).grid(row=2, column=2)
        tk.Checkbutton(
                fr,
                variable=self.force_plus_12_db
            ).grid(row=2, column=3)

        fr.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        fr = tk.Frame(self)

        tk.Label(fr, text="From #Num : ").pack(side=tk.LEFT)
        ROCombobox(
                fr,
                values=list(range(19,422))+list(range(501,1000)),
                width=3,
                textvariable=self.smp_num_from
            ).pack(side=tk.LEFT)

        fr.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

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
        self.options.osc_cat = self.osc_cat.get()
        self.options.loop_type = loop_type_from_str[self.loop_type.get()]
        self.options.plus_12_db = plus_12_db_from_str[self.plus_12_db.get()]
        self.options.force_osc_cat = self.force_osc_cat.get()
        self.options.force_loop_type = self.force_loop_type.get()
        self.options.force_plus_12_db = self.force_plus_12_db.get()
        self.options.smp_num_from = self.smp_num_from.get()

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
