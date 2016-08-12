"""
Copyright (C) 2016 Jonathan Taquet

This file is part of Oe2sSLE (Open e2sSample.all Library Editor).

Foobar is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Foobar is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Oe2sSLE.  If not, see <http://www.gnu.org/licenses/>
"""

import tkinter as tk
import tkinter.ttk

import copy

import audio
import e2s_sample_all
import GUI.res
import RIFF
import wav_tools

class StereoToMonoDialog(tk.Toplevel):
    def __init__(self, parent, e2s_sample, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.transient(parent)
        self.title('Convert from stereo to mono ?')

        self.parent = parent
        self.e2s_sample = e2s_sample
        self.esli = e2s_sample_all.RIFF_korg_esli()
        self.esli.rawdata[:] = e2s_sample.get_esli().rawdata[:]
        self.fmt = copy.deepcopy(e2s_sample.get_fmt())
        self.fmt.channels=1
        self.fmt.avgBytesPerSec = self.fmt.avgBytesPerSec // 2
        self.fmt.blockAlign = self.fmt.blockAlign // 2
        self.esli.OSC_StartPoint_address = self.esli.OSC_StartPoint_address // 2
        self.esli.OSC_LoopStartPoint_offset = self.esli.OSC_LoopStartPoint_offset // 2
        self.esli.OSC_EndPoint_offset = self.esli.OSC_EndPoint_offset // 2
        self.esli.WAV_dataSize = self.esli.WAV_dataSize // 2
        self.esli.useChan1 = False
        self.w = (0,0)
        self.data = None
        self.result = None

        self.mix_var = tk.DoubleVar()

        tk.Label(self, text="Stereo to mono mix settings").pack(fill=tk.X)
        body = tk.Frame(self)

        tk.Label(body, text="L").pack(side=tk.LEFT)
        self.mix_scale = tk.Scale(body, variable = self.mix_var, orient=tk.HORIZONTAL, from_=-1, to=1, resolution=0.001)
        self.mix_scale.pack(fill=tk.X, side=tk.LEFT, expand=True)
        tk.Label(body, text="R").pack(side=tk.LEFT)
        self.buttonPlay = tk.Button(body, image=GUI.res.playIcon, command=self.play)
        self.buttonPlay.pack(side=tk.LEFT, padx=5, pady=5)
        self.buttonStop = tk.Button(body, image=GUI.res.stopIcon, command=self.stop)
        self.buttonStop.pack(side=tk.LEFT, padx=5, pady=5)
        #self.waitBar = tk.ttk.Progressbar(body, orient='horizontal', mode='indeterminate', length=320)
        #self.waitBar.pack(expand=True, fill=tk.BOTH, side=tk.TOP)
        #self.waitBar.start()
        body.pack(fill=tk.BOTH, expand=True)#(padx=5, pady=5)
        
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

#        self.waitBar.focus_set()
        self.mix_scale.focus_set()
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
        mix = self.mix_var.get()
        w = ((1 - mix)/2, 1 - (1 - mix)/2)
        if self.w != (w):
            self.w=w
            self.data=wav_tools.wav_stereo_to_mono(self.e2s_sample.get_data().rawdata,*self.w)

    def play(self):
        self.update_data()
        audio.player.play_start(audio.LoopWaveSource(self.data,self.fmt,self.esli))

    def stop(self):
        audio.player.play_stop()

    #
    # standard button semantics

    def ok(self, event=None):
        self.withdraw()
        self.update_idletasks()

        self.apply()

        self.cancel()

    def cancel(self, event=None):
        self.stop()
        # put focus back to the parent window
        self.parent.focus_set()
        self.destroy()

    def apply(self):
        self.update_data()
        korg_chunk = self.e2s_sample.RIFF.chunkList.get_chunk(b'korg')
        esli_chunk = korg_chunk.data.chunkList.get_chunk(b'esli')
        esli_chunk.data.rawdata[:] = self.esli.rawdata[:]
        fmt__chunk = self.e2s_sample.RIFF.chunkList.get_chunk(b'fmt ')
        fmt__chunk.data = self.fmt
        data_chunk = self.e2s_sample.RIFF.chunkList.get_chunk(b'data')
        data_chunk.data.rawdata = self.data
        # Not requiered:
        #data_chunk.update_header()
        #self.e2s_sample.RIFF.update_header()
        #self.e2s_sample.update_header()
