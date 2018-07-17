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

import os
import sys
import tkinter as tk

exchangeIcon=None
swap_nextIcon=None
swap_next10Icon=None
swap_next100Icon=None
swap_prevIcon=None
swap_prev10Icon=None
swap_prev100Icon=None
next_freeIcon=None
prev_freeIcon=None

replaceIcon=None
exportIcon=None
editIcon=None
trashIcon=None
playIcon=None
stopIcon=None
stop_smallIcon=None
donateEurIcon=None
donateUsdIcon=None

# for pyIntaller bundled executable
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def init():
    global exchangeIcon
    global swap_nextIcon
    global swap_next10Icon
    global swap_next100Icon
    global swap_prevIcon
    global swap_prev10Icon
    global swap_prev100Icon
    global next_freeIcon
    global prev_freeIcon

    global replaceIcon
    global exportIcon
    global editIcon
    global trashIcon
    global playIcon
    global stopIcon
    global stop_smallIcon
    global donateEurIcon
    global donateUsdIcon

    exchangeIcon=tk.PhotoImage(file=resource_path("images/exchange.gif"))
    swap_nextIcon=tk.PhotoImage(file=resource_path("images/swap-next.gif"))
    swap_next10Icon=tk.PhotoImage(file=resource_path("images/swap-next-10.gif"))
    swap_next100Icon=tk.PhotoImage(file=resource_path("images/swap-next-100.gif"))
    swap_prevIcon=tk.PhotoImage(file=resource_path("images/swap-prev.gif"))
    swap_prev10Icon=tk.PhotoImage(file=resource_path("images/swap-prev-10.gif"))
    swap_prev100Icon=tk.PhotoImage(file=resource_path("images/swap-prev-100.gif"))
    next_freeIcon=tk.PhotoImage(file=resource_path("images/next-free.gif"))
    prev_freeIcon=tk.PhotoImage(file=resource_path("images/prev-free.gif"))

    replaceIcon=tk.PhotoImage(file=resource_path("images/replace.gif"))
    exportIcon=tk.PhotoImage(file=resource_path("images/export.gif"))
    editIcon=tk.PhotoImage(file=resource_path("images/edit.gif"))
    trashIcon=tk.PhotoImage(file=resource_path("images/trash.gif"))
    playIcon=tk.PhotoImage(file=resource_path("images/play.gif"))
    stopIcon=tk.PhotoImage(file=resource_path("images/stop.gif"))
    stop_smallIcon=tk.PhotoImage(file=resource_path("images/stop-small.gif"))
    donateEurIcon=tk.PhotoImage(file=resource_path("images/donate-eur.gif"))
    donateUsdIcon=tk.PhotoImage(file=resource_path("images/donate-usd.gif"))