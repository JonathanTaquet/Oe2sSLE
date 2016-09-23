# -*- coding: utf-8 -*-
"""
Copyright (C) 2015-2016 Jonathan Taquet

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

class ROCombobox(tk.ttk.Combobox):
    def __init__(self, parent, *arg, **kwarg):
        self._command=kwarg.pop('command',None)
        super().__init__(parent, *arg, **kwarg)
        self.config(state='readonly')

        if self._command:
            self.bind("<<ComboboxSelected>>", self._command)

class ROSpinbox(tk.Spinbox):
    def __init__(self, parent, *arg, **kwarg):
        super().__init__(parent, *arg, **kwarg)
        self.config(state='readonly')

        self.bind("<FocusIn>",self._focusin)
        self.bind("<FocusOut>",self._focusout)
        self.bind("<Button-1>",lambda event: self.focus_set())

        self.defaultrobg = self.cget('readonlybackground')
        self._focusout()

    def _focusin(self, event=None):
        self.config(readonlybackground="#C8C8C8")

    def _focusout(self, event=None):
        self.config(readonlybackground=self.defaultrobg)
