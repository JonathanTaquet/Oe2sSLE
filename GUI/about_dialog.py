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
import webbrowser
from version import Oe2sSLE_VERSION

class AboutDialog(tk.Toplevel):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.transient(parent)
        self.title('About Open e2sSample.all Library Editor')
        self.resizable(width=tk.FALSE, height=tk.FALSE)

        body = tk.Frame(self)
        self.text = tk.Text(body,state=tk.NORMAL,width=80)
        self.text.pack()
        body.pack(padx=5, pady=5)

        text = self.text
        text.config(cursor="arrow")
        text.insert(tk.INSERT,"Oe2sSLE "+str(Oe2sSLE_VERSION[0])+"."+str(Oe2sSLE_VERSION[1])+"."+str(Oe2sSLE_VERSION[2])+"\n")

        text.insert(tk.END,
"""
The Home of this application is its GitHub repository.
To contribute or support, visit """)
        text.tag_config("link-github", foreground="blue", underline=1)
        text.tag_bind("link-github", "<Button-1>", lambda event: webbrowser.open('https://github.com/JonathanTaquet/Oe2sSLE/'))
        text.insert(tk.END, "<https://github.com/JonathanTaquet/Oe2sSLE/>", "link-github")
        text.insert(tk.END,
"""

Copyright (C) 2015-2016 Jonathan Taquet

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see """)
        text.tag_config("link-gpl", foreground="blue", underline=1)
        text.tag_bind("link-gpl", "<Button-1>", lambda event: webbrowser.open('http://www.gnu.org/licenses/'))
        text.insert(tk.END, "<http://www.gnu.org/licenses/>", "link-gpl")

        text.config(state=tk.DISABLED)

        self.focus_set()
        self.grab_set()
        self.wait_window(self)