# -*- coding: utf-8 -*-
"""
Copyright (C) 2015-2016 Jonathan Taquet

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
import tkinter.filedialog
import tkinter.messagebox
import tkinter.ttk
#import re
import math
import platform
#import time
import sys

import RIFF
import e2s_sample_all as e2s
from VerticalScrolledFrame import VerticalScrolledFrame
import wav_tools

import os.path

import audio

import struct
import webbrowser

import GUI.res
from GUI.stereo_to_mono import StereoToMonoDialog
from GUI.wait_dialog import WaitDialog

Oe2sSLE_VERSION = (0,0,11)

class logger:
    def __init__(self):
        self.file = None
        self.stderr = sys.stderr
        self.stdout = sys.stdout
        sys.stderr=self
        sys.stdout=self

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self.file:
            self.file.write('-- Logger closed --\n')
            self.file.close()
        sys.stderr = self.stderr
        sys.stdout = self.stdout

    def write(self, data):
        if not self.file:
            self.file = open('Oe2sSLE.log', 'a')
        self.file.write(data)
        self.file.flush()

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

def linspace(start,stop,num):
    for i in range(num):
        yield start+((stop-start)*i)/(num-1)

class WaveDisplay(tk.Canvas):
    class LineSet:
        def __init__(self, first, last, loop_first=None, attack_last=None, amplitude=None):
            self.first=first
            self.last=last
            self.loop_first=loop_first
            self.attack_last=attack_last
            self.amplitude=amplitude
    
    def __init__(self, *arg, **kwarg):
        kwarg['highlightthickness']=0
        super().__init__(*arg, **kwarg)
        self.bind("<Configure>", self.on_resize)
        self.height = self.winfo_reqheight()
        self.width = self.winfo_reqwidth()
        
        self.toRefresh = False
        self.refreshLineSetOnly = False
        self.scrollBar = None

        self.wav = [[int(20000*math.sin(x*2.*math.pi/self.width)) for x in range(self.width)]]*2
        self.bitmap = bytearray()
        self.dispFrom = 0
        self.dispTo = self.width-1
        
        self.ampMax = 32767
        self.ampTot = 65536
        self.bgColor = (0,0,127)
        self.wavColor= (0,0,255)
        self.photo = tk.PhotoImage(width=self.width, height=self.height)
        self.photo_handle = self.create_image((0,0), anchor=tk.NW, image=self.photo, state="normal")

        self.refresh()

        self.lineSets = []
        self.activeLineSet = None

        self.bind("<Motion>", self.on_motion)
        self.bind("<ButtonPress-1>", self.on_b1_press)
        self.bind("<ButtonRelease-1>", self.on_b1_release)
        self.bind("<B1-Motion>", self.on_b1_motion)
        
    def set_activeLineSet(self, activeLineSet=None):
        if self.activeLineSet != activeLineSet:
            self.activeLineSet=activeLineSet
            self.refresh(True)
    
    def add_lineSet(self, lineSet):
        self.lineSets.append(lineSet)
        self.refresh(True)

    def set_scrollBar(self, scrollBar):
        self.scrollBar = scrollBar
        self.update_scrollBar()

    def set_wav(self, wave_fmt, wave_data):
        if wave_fmt.formatTag != RIFF.WAVE_fmt_.WAVE_FORMAT_PCM:
            raise Exception('format tag')
        if wave_fmt.bitPerSample != 16:
            raise Exception('bit per sample')
        num_chans = wave_fmt.channels
        num_samples = len(wave_data.rawdata)//2//num_chans
        tot_num_samples = num_samples*num_chans
        samples = struct.unpack('<'+str(tot_num_samples)+'h', wave_data.rawdata)
        self.wav = []
        for chan in range(num_chans):
            self.wav.append(samples[chan:tot_num_samples:num_chans])
        self.dispFrom = 0
        self.dispTo = num_samples
        self.activeLineSet = None
        self.refresh()
        
    def wav_length(self):
        return len(self.wav[0])
    
    def num_channels(self):
        return len(self.wav)

    def set_disp(self, dispFrom, dispTo):
        assert dispFrom < dispTo
        if dispFrom != self.dispFrom or dispTo != self.dispTo:
            self.dispFrom = dispFrom
            self.dispTo = dispTo
            self.refresh()
            
    def display_sample(self, index):
        if index < self.dispFrom:
            self.set_disp(index, self.dispTo - self.dispFrom + index)
        elif index > self.dispTo:
            self.set_disp(self.dispFrom - self.dispTo + index, index)
    
    """
    scroll by a step in samples
    """
    def scroll(self, step):
        self.set_disp(self.dispFrom+step, self.dispTo+step)
    
    def scroll_to(self, offset):
        self.scroll(offset - self.dispFrom)

    def scroll_stop(self, step):
        if step < 0:
            if self.dispFrom >= 0:
                step = max(step, -self.dispFrom)
            else:
                step = 0
        elif step > 0:
            if self.dispTo <= self.wav_length()-1:
                step = min(step, self.wav_length()-self.dispTo)
            else:
                step = 0
        self.scroll(step)
        
    """
    scroll by a step equvalent to pixels
    """
    def scroll_pix(self, step):
        self.scroll(step/self.get_zoom_x())

    def scroll_pix_stop(self, step):
        self.scroll_stop(step/self.get_zoom_x())

    def set_zoom_x(self, zoom):
        x_mid = self.dispFrom + (self.dispTo-self.dispFrom)/2
        dispFrom = int(round(x_mid-self.width/zoom/2))
        dispTo = int(round(x_mid+self.width/zoom/2))
        if dispFrom < -1:
            diff = -1-dispFrom
            dispFrom += diff
            dispTo += diff
        if dispTo > self.wav_length()-1:
            dispTo=self.wav_length()-1
        self.set_disp(dispFrom,dispTo)
        
    def get_zoom_x(self):
        return self.width/(self.dispTo-self.dispFrom)
        
    def wav_view_length(self):
        return self.dispTo-self.dispFrom
    
    """
    """
    def on_motion(self,event):
        lineset = self.activeLineSet
        if lineset is not None:
            amp_active = 1 #lineset.loop_first is None
        
            if (abs(event.x-lineset._last_x) < 5
                or abs(event.x-lineset._mid_x) < 5
                or abs(event.x-lineset._first_x) < 5):
                if self.cget('cursor') != 'sb_h_double_arrow':
                    self.configure(cursor='sb_h_double_arrow')
            elif (amp_active
                and (abs(event.y-lineset._amp_y0) < 5
                    or abs(event.y-lineset._amp_y1) < 5)
                and event.x >= lineset._amp_start_x
                and event.x <= lineset._amp_end_x):
                if self.cget('cursor') != 'sb_v_double_arrow':
                    self.configure(cursor='sb_v_double_arrow')
            else:
                if self.cget('cursor'):
                    self.configure(cursor='')

    def on_b1_press(self,event):
        self.drag=0
        lineset = self.activeLineSet
        if lineset is not None:
            amp_active = 1 #lineset.loop_first is None
        
            if abs(event.x-lineset._last_x) < 5:
                self.drag=3
            elif abs(event.x-lineset._mid_x) < 5:
                self.drag=2
            elif abs(event.x-lineset._first_x) < 5:
                self.drag=1
            elif amp_active:
                if abs(event.y-lineset._amp_y1) < 5:
                    self.drag=5
                elif abs(event.y-lineset._amp_y0) < 5:
                    self.drag=4

    def on_b1_release(self,event):
        self.drag=0

    def on_b1_motion(self,event):
        if self.drag:
            lineset = self.activeLineSet

            x = event.x
            y = event.y
            
            w = self.width
            h = self.height
            fr = self.dispFrom
            to = self.dispTo
            num_chans = self.num_channels()

            if self.drag < 4:
                new_x=int(fr+x*(to-fr)/w)
                if self.drag == 1:
                    lineset.first.set(new_x)
                elif self.drag == 2:
                    if lineset.loop_first is not None:
                        lineset.loop_first.set(new_x)
                    else:
                        lineset.attack_last.set(new_x)
                elif self.drag == 3:
                    lineset.last.set(new_x)
            else:
                if self.drag == 4:
                    new_y=int(self.ampTot-y*num_chans*self.ampTot*2/h)
                    lineset.amplitude.set(abs(new_y))
                elif self.drag == 5:
                    new_y=int(y*num_chans*self.ampTot*2/h-self.ampTot)
                    lineset.amplitude.set(abs(new_y))

    def on_resize(self,event):
        if self.width == event.width and self.height == event.height:
            return
        self.width = event.width
        self.height = event.height
        self.refresh()
        
    def refresh(self, line_set_only=False):
        if self.refreshLineSetOnly and not line_set_only:
            self.refreshLineSetOnly = False
        if not self.toRefresh:
            self.toRefresh=True
            self.after_idle(self.draw_wav)
        self.update_scrollBar()

    def update_scrollBar(self):
        if self.scrollBar:
            self.scrollBar.set(self.dispFrom/self.wav_length(), self.dispTo/self.wav_length())

    def draw_wav(self):
        # TODO:
        #  - put image into object
        #  - allow to update only parts : slice bar drawn, ...
        #while True:
        if self.toRefresh:
            self.toRefresh=False
            w = self.width
            h = self.height
            fr = self.dispFrom
            to = self.dispTo
    
            wstep = w*3
            
            # from python 3.5:
            #header = b"P6 %d %d 255 " % (w, h)
            header = bytes("P6 %d %d 255 " % (w, h), "utf8")
            head_l = len(header)

            if self.wav:
                num_chans = self.num_channels()

            if not self.refreshLineSetOnly:
                self.refreshLineSetOnly = True
                self.wav_ppm = bytearray(head_l+w*h*3)
                ppm = self.wav_ppm
                ppm[0:head_l] = header
                # init with bg color
                ppm[head_l:] = self.bgColor*(w*h)
                # draw zero line(s)
                if self.wav:
                    for chan in range(num_chans):
                        line=int((self.ampMax/self.ampTot+chan)*(h/num_chans))
                        ppm[head_l+line*wstep:head_l+(line+1)*wstep] = (127,127,127)*w
            
                # draw wav
                if self.wav:
                    for chan in range(num_chans):
                        _smin=0
                        _smax=0
                        for x in range(w):
                            start=max(0,int(fr+math.floor((to-fr)*(x)/w)))
                            stop=min(self.wav_length(),max(start+1,int(fr+math.floor((to-fr)*(x+1.)/w))))
                            if stop>start:
                                __smin=min(self.wav[chan][start:stop])
                                __smax=max(self.wav[chan][start:stop])
                                smin=min(_smax,__smin)
                                smax=max(_smin,__smax)
                                _smin=__smin
                                _smax=__smax
                            
                                pStart=int(((self.ampMax-smax)/self.ampTot+chan)*(h/num_chans))
                                pStop =int(((self.ampMax-smin)/self.ampTot+chan)*(h/num_chans))+1

                                #for i in range(pStop-pStart):
                                #    ppm[head_l+x*3+wstep*(i+pStart)+0:head_l+x*3+wstep*(i+pStart)+3] = self.wavColor
                                ppm[head_l+x*3+wstep*pStart+0:head_l+x*3+wstep*pStop+0:wstep] = (self.wavColor[0],)*(pStop-pStart)
                                ppm[head_l+x*3+wstep*pStart+1:head_l+x*3+wstep*pStop+1:wstep] = (self.wavColor[1],)*(pStop-pStart)
                                ppm[head_l+x*3+wstep*pStart+2:head_l+x*3+wstep*pStop+2:wstep] = (self.wavColor[2],)*(pStop-pStart)                    

            # draw line sets
            ppm = bytearray(head_l+w*h*3)
            ppm[:] = self.wav_ppm
            for active in (False, True):
                for lineSet in self.lineSets:
                    if active == (lineSet is self.activeLineSet):
                        first = lineSet.first.get()
                        last = lineSet.last.get()
                        if lineSet.loop_first is not None:
                            mid = lineSet.loop_first.get()
                        else:
                            mid = lineSet.attack_last.get()
                        amp = lineSet.amplitude.get()
                        if amp is not None:
                            start_x = max(0, math.floor((first+0.25 - fr)*w/(to - fr)))
                            end_x = min(w-1, math.ceil((last+0.75 - fr)*w/(to - fr)))

                            if active:
                                lineSet._amp_start_x = start_x
                                lineSet._amp_end_x = end_x
                                lineSet._amp_y0 = max(0,int((math.floor((self.ampTot-amp)/2)/self.ampTot)*(h/num_chans)))
                                lineSet._amp_y1 = min(h-1,int((math.floor((self.ampTot+amp)/2)/self.ampTot)*(h/num_chans)))
                            
                            
                            if end_x > start_x:
                                for chan in range(num_chans):
                                    y0 = max(0,int((math.floor((self.ampTot-amp)/2)/self.ampTot+chan)*(h/num_chans)))
                                    y1 = min(h-1,int((math.floor((self.ampTot+amp)/2)/self.ampTot+chan)*(h/num_chans)))
                                    if active:
                                        ppm[head_l+start_x*3+wstep*y0+0:head_l+(end_x+1)*3+wstep*y0+0:3] = (255,)*(end_x-start_x+1)
                                        ppm[head_l+start_x*3+wstep*y1+0:head_l+(end_x+1)*3+wstep*y1+0:3] = (255,)*(end_x-start_x+1)
                                    else:
                                        ppm[head_l+start_x*3+wstep*y0+0:head_l+(end_x+1)*3+wstep*y0+0:3] = (127,)*(end_x-start_x+1)
                                        ppm[head_l+start_x*3+wstep*y0+1:head_l+(end_x+1)*3+wstep*y0+1:3] = (127,)*(end_x-start_x+1)
                                        ppm[head_l+start_x*3+wstep*y1+0:head_l+(end_x+1)*3+wstep*y1+0:3] = (127,)*(end_x-start_x+1)
                                        ppm[head_l+start_x*3+wstep*y1+1:head_l+(end_x+1)*3+wstep*y1+1:3] = (127,)*(end_x-start_x+1)

                        if fr <= mid <= to:
                            x = round((mid+0.5 - fr)*w/(to - fr))
                            if x >= w:
                                x = w-1
                            # some green
                            if active:
                                ppm[head_l+x*3+1:head_l+x*3+wstep*h+1:wstep] = (255,)*h
                                lineSet._mid_x=x
                            else:
                                ppm[head_l+x*3+1:head_l+x*3+wstep*h+1:wstep] = (127,)*h
                        elif active:
                            lineSet._mid_x=round((mid+0.5 - fr)*w/(to - fr))
                                
                        if fr <= first <= to:
                            x = math.floor((first+0.25 - fr)*w/(to - fr))
                            # some green and red
                            if active:
                                ppm[head_l+x*3+0:head_l+x*3+wstep*h+0:wstep] = (255,)*h
                                ppm[head_l+x*3+1:head_l+x*3+wstep*h+1:wstep] = (255,)*h
                                lineSet._first_x=x
                            else:
                                ppm[head_l+x*3+0:head_l+x*3+wstep*h+0:wstep] = (127,)*h
                                ppm[head_l+x*3+1:head_l+x*3+wstep*h+1:wstep] = (127,)*h
                        elif active:
                            lineSet._first_x=math.floor((first+0.25 - fr)*w/(to - fr))
                        
                        if fr <= last <= to:
                            x = math.ceil((last+0.75 - fr)*w/(to - fr))
                            if x >= w:
                                x = w-1
                            # some red
                            if active:
                                ppm[head_l+x*3+0:head_l+x*3+wstep*h+0:wstep] = (255,)*h
                                lineSet._last_x=x
                            else:
                                ppm[head_l+x*3+0:head_l+x*3+wstep*h+0:wstep] = (127,)*h
                        elif active:
                            lineSet._last_x=math.ceil((last+0.75 - fr)*w/(to - fr))
                
            self.photo.configure(data=bytes(ppm), width=w, height=h)

class SampleNumSpinbox(ROSpinbox):
    def __init__(self, parent, *arg, **kwarg):
        super().__init__(parent, *arg, **kwarg)
        
        self.bind("<Shift-Up>",lambda event: self.big_increase(98))
        self.bind("<Shift-Down>",lambda event: self.big_increase(-98))
        self.bind("<Prior>",lambda event: self.big_increase(999))
        self.bind("<Next>",lambda event: self.big_increase(-999))
        self.bind("<Shift-Prior>",lambda event: self.big_increase(9999))
        self.bind("<Shift-Next>",lambda event: self.big_increase(-9999))

    def big_increase(self, increment):
        _curr=int(self.get())
        _max=int(self.cget('to'))
        _min=int(self.cget('from'))
        _next=min(_curr+increment,_max)
        _next=max(_next,_min)
        self.tk.globalsetvar(self.cget('textvariable'),_next)
        if increment:
            self.invoke('buttonup' if increment > 0 else 'buttondown')

class CVar:
    def __init__(self, var, min, max):
        self.var = var
        self.min = min
        self.max = max
        
    def set(self, value):
        if value < self.min:
            self.var.set(self.min)
        elif value > self.max:
            self.var.set(self.max)
        else:
            self.var.set(value)
            
    def get(self):
        return self.var.get()

class Slice:
    def __init__(self, master, editor, sliceNum):
        self.master = master
        self.editor = editor
        self.sliceNum = sliceNum
        
        self.labelSlice = tk.Label(self.master, text="Slice "+str(self.sliceNum)).grid(row=sliceNum+1)

        self.start  = tk.IntVar()
        self.stop = tk.IntVar()
        self.attack = tk.IntVar()
        self.amplitude = tk.IntVar()
        
        self.startTrace = None
        self.stopTrace = None
        self.attackTrace = None
        self.amplitudeTrace = None

        self.entryStart = SampleNumSpinbox(self.master, width=10, from_=0, textvariable=self.start, state='readonly')
        self.entryStop = SampleNumSpinbox(self.master, width=10, from_=-1, textvariable=self.stop, state='readonly')
        self.entryAttack = SampleNumSpinbox(self.master, width=10, from_=-1, textvariable=self.attack, state='readonly')
        self.entryAmplitude = SampleNumSpinbox(self.master, width=10, from_=0, textvariable=self.amplitude, state='readonly')
        self.buttonPlay = tk.Button(self.master, image=GUI.res.playIcon, command=self._play)
        
        self._selected=False
        self.entryStart.bind("<FocusIn>",self._focus_in,add="+")
        self.entryStart.bind("<FocusOut>",self._focus_out,add="+")
        self.entryStop.bind("<FocusIn>",self._focus_in,add="+")
        self.entryStop.bind("<FocusOut>",self._focus_out,add="+")
        self.entryAttack.bind("<FocusIn>",self._focus_in,add="+")
        self.entryAttack.bind("<FocusOut>",self._focus_out,add="+")
        self.entryAmplitude.bind("<FocusIn>",self._focus_in,add="+")
        self.entryAmplitude.bind("<FocusOut>",self._focus_out,add="+")

        self.entryStart.grid(row=sliceNum+1, column=1)
        self.entryStop.grid(row=sliceNum+1, column=2)
        self.entryAttack.grid(row=sliceNum+1, column=3)
        self.entryAmplitude.grid(row=sliceNum+1, column=4)
        self.buttonPlay.grid(row=sliceNum+1, column=5)
        
        self.lineSet = WaveDisplay.LineSet(self.start,self.stop,attack_last=self.attack,amplitude=self.amplitude)
        self.editor.wavDisplay.add_lineSet(self.lineSet)

    def set_sample(self, fmt, data, esli):
        if self.startTrace:
            self.start.trace_vdelete('w', self.startTrace)
        if self.stopTrace:
            self.stop.trace_vdelete('w', self.stopTrace)
        if self.attackTrace:
            self.attack.trace_vdelete('w', self.attackTrace)
        if self.amplitudeTrace:
            self.amplitude.trace_vdelete('w', self.amplitudeTrace)

        self.fmt = fmt
        self.data = data.rawdata
        self.esli = esli
        
        self.blockAlign = fmt.blockAlign
        self.sample_length = len(data) // self.blockAlign

        start=esli.slices[self.sliceNum].start
        stop=start+esli.slices[self.sliceNum].length-1
        attack=start+esli.slices[self.sliceNum].attack_length-1
        amplitude=esli.slices[self.sliceNum].amplitude
        
        self.entryStart.config(to=self.sample_length-1)
        self.entryStop.config(to=self.sample_length-1)
        self.entryAttack.config(to=self.sample_length-1)
        self.entryAmplitude.config(to=65536)
        
        self.start.set(start)
        self.stop.set(stop)
        self.attack.set(attack)
        self.amplitude.set(amplitude)
        
        self.lineSet.first = CVar(self.start,0,self.sample_length-1)
        self.lineSet.last = CVar(self.stop,-1,self.sample_length-1)
        self.lineSet.attack_last = CVar(self.attack,-1,self.sample_length-1)
        self.lineSet.amplitude = CVar(self.amplitude,0,65536)

        self.startTrace = self.start.trace('w', self._start_set)
        self.stopTrace = self.stop.trace('w', self._stop_set)
        self.attackTrace = self.attack.trace('w', self._attack_set)
        self.amplitudeTrace = self.amplitude.trace('w', self._amplitude_set)

        self._selected=False

    def _focus_in(self, event):
        if not self._selected:
            self.editor.wavDisplay.set_activeLineSet(self.lineSet)
            self.selected = True

    def _focus_out(self, event):
        if self._selected:
            self.editor.wavDisplay.set_activeLineSet()
            self.selected = False

    def _start_set(self, *args):
        start = self.start.get()
        if start > self.sample_length-1:
            self.start.set(self.sample_length-1)
            start = self.sample_length-1
        elif start < 0:
            self.start.set(0)
            start = 0
        if start > self.stop.get()+1:
            self.stop.set(start-1)
        if start > self.attack.get()+1:
            self.attack.set(start-1)

        self.esli.slices[self.sliceNum].start = start
        # update the offsets
        self.esli.slices[self.sliceNum].length = self.stop.get()-start+1
        self.esli.slices[self.sliceNum].attack_length = self.attack.get()-start+1
        self.editor.wavDisplay.refresh(True)

    def _stop_set(self, *args):
        stop = self.stop.get()
        if stop > self.sample_length-1:
            self.stop.set(self.sample_length-1)
            stop = self.sample_length-1
        elif stop < -1:
            self.stop.set(-1)
            stop= -1
        if stop < self.start.get()-1:
            self.start.set(stop+1)
        if stop < self.attack.get():
            self.attack.set(stop)
        self.esli.slices[self.sliceNum].length = stop-self.start.get()+1
        self.editor.wavDisplay.refresh(True)

    def _attack_set(self, *args):
        attack = self.attack.get()
        if attack > self.sample_length-1:
            self.attack.set(self.sample_length-1)
            attack = self.sample_length-1
        elif attack < -1:
            self.attack.set(-1)
            attack = -1
        if attack < self.start.get()-1:
            self.start.set(attack+1)
        if attack > self.stop.get():
            self.stop.set(attack)

        self.esli.slices[self.sliceNum].attack_length = attack-self.start.get()+1
        self.editor.wavDisplay.refresh(True)

    def _amplitude_set(self, *args):
        amp = self.amplitude.get()
        if amp > 65536:
            self.amplitude.set(65536)
            amp = 65536
        elif amp < 0:
            self.amplitude.set(0)
            amp = 0

        self.esli.slices[self.sliceNum].amplitude = amp
        self.editor.wavDisplay.refresh(True)


    def _play(self, *args):
        start=self.start.get()*self.fmt.blockAlign
        stop=self.stop.get()*self.fmt.blockAlign
        if stop > 0:
            audio.player.play_start(audio.Sound(self.data[start:stop],self.fmt))

class FrameSlices(tk.Frame):
    def __init__(self, master, editor, *arg, **kwarg):
        super().__init__(master, *arg, **kwarg)
        
        tk.Label(self, text="First").grid(row=0, column=1)        
        tk.Label(self, text="Last").grid(row=0, column=2)        
        tk.Label(self, text="?Attack?").grid(row=0, column=3)        
        tk.Label(self, text="?Amplitude?").grid(row=0, column=4)

        self.slices = [Slice(self,editor,i) for i in range(64)]

    def set_sample(self, fmt, data, esli):
        for s in self.slices:
            s.set_sample(fmt,data,esli)

class NormalSampleOptions(tk.LabelFrame):
    def __init__(self, parent, editor, *arg, **kwarg):
        super().__init__(parent, *arg, **kwarg)
        
        self.editor = editor

        self.sound = None
        self.fmt = None
        self.data = None
        self.esli = None
        
        self.sample_length = 0

        tk.Label(self, text="Start").grid(row=1, column=1)
        tk.Label(self, text="End").grid(row=1, column=2)
        tk.Label(self, text="Loop start").grid(row=1, column=3)
        tk.Label(self, text="Play volume").grid(row=1, column=4)

        self.start = tk.IntVar()
        self.stop = tk.IntVar()
        self.loopStart = tk.IntVar()
        self.playVolume = tk.IntVar()
        
        self.start_trace = None
        self.stop_trace = None
        self.loopStart_trace = None
        self.playVolume_trace = None
        self.rootSet = None        
        
        tk.Label(self, text="Sample").grid(row=2, column=0)
        self.startEntry = SampleNumSpinbox(self, width=10, from_=0, to=0, textvariable=self.start, state='readonly')
        self.startEntry.grid(row=2, column=1)
        self.stopEntry = SampleNumSpinbox(self, width=10, from_=0, to=0, textvariable=self.stop, state='readonly')
        self.stopEntry.grid(row=2, column=2)
        self.loopStartEntry = SampleNumSpinbox(self, width=10, from_=0, to=0, textvariable=self.loopStart, state='readonly')
        self.loopStartEntry.grid(row=2, column=3)
        self.playVolumeEntry = SampleNumSpinbox(self, width=10, from_=0, to=65535, textvariable=self.playVolume, state='readonly')
        self.playVolumeEntry.grid(row=2, column=4)        
        self.buttonPlay = tk.Button(self, image=GUI.res.playIcon, command=self.play_start)
        self.buttonPlay.grid(row=2,column=5)
        self.buttonStop = tk.Button(self, image=GUI.res.stopIcon, command=self.play_stop)
        self.buttonStop.grid(row=2,column=6)
        
        self._selected=False
        self.startEntry.bind("<FocusIn>",self._focus_in,add="+")
        self.startEntry.bind("<FocusOut>",self._focus_out,add="+")
        self.stopEntry.bind("<FocusIn>",self._focus_in,add="+")
        self.stopEntry.bind("<FocusOut>",self._focus_out,add="+")
        self.loopStartEntry.bind("<FocusIn>",self._focus_in,add="+")
        self.loopStartEntry.bind("<FocusOut>",self._focus_out,add="+")
        self.playVolumeEntry.bind("<FocusIn>",self._focus_in,add="+")
        self.playVolumeEntry.bind("<FocusOut>",self._focus_out,add="+")

        self.lineSet = WaveDisplay.LineSet(self.start,self.stop,loop_first=self.loopStart)
        self.editor.wavDisplay.add_lineSet(self.lineSet)

    def play_start(self):
        # TODO: icon pause
        # TODO: see how to reduce delay (i.e. buffer size)
        #if self.sound is not None:
        #    self.sound.pause()
    
        # TODO: verrify meaning of each offset in esli (+ or - 1 or not )
        audio.player.play_start(audio.LoopWaveSource(self.data,self.fmt,self.esli))

    def play_stop(self):
        audio.player.play_stop()

    def set_sample(self, smpl):
        self.smpl = smpl

        fmt = smpl.e2s_sample.get_fmt()
        data = smpl.e2s_sample.get_data()
        esli = smpl.e2s_sample.get_esli()        

        self.fmt = fmt
        self.data = data.rawdata
        self.esli = esli
        self.blockAlign = fmt.blockAlign
        self.sample_length = len(data) // self.blockAlign
        
        self.oneshot = self.smpl.oneShot.get()
        
        if self.start_trace:
            self.start.trace_vdelete('w', self.start_trace)
        if self.stop_trace:
            self.stop.trace_vdelete('w', self.stop_trace)
        if self.loopStart_trace:
            self.loopStart.trace_vdelete('w', self.loopStart_trace)
        if self.playVolume_trace:
            self.playVolume.trace_vdelete('w', self.playVolume_trace)

        start=esli.OSC_StartPoint_address//self.blockAlign
        stop=start+esli.OSC_EndPoint_offset//self.blockAlign
        loopStart=start+esli.OSC_LoopStartPoint_offset//self.blockAlign
        playVolume=esli.playVolume
        
        self.startEntry.config(to=self.sample_length-1)
        self.stopEntry.config(to=self.sample_length-1)
        self.loopStartEntry.config(to=self.sample_length-1)
        
        self.start.set(start)
        self.stop.set(stop)
        self.loopStart.set(loopStart)
        self.playVolume.set(playVolume)
        
        self.start_trace = self.start.trace('w', self._start_set)
        self.stop_trace = self.stop.trace('w', self._stop_set)
        self.loopStart_trace = self.loopStart.trace('w', self._loopStart_set)
        self.playVolume_trace = self.playVolume.trace('w', self._playVolume_set)
        
        self.lineSet.first = CVar(self.start,0,self.sample_length-1)
        self.lineSet.last = CVar(self.stop,0,self.sample_length-1)
        self.lineSet.loop_first = CVar(self.loopStart,0,self.sample_length-1)
        self.lineSet.amplitude = CVar(self.playVolume,0,65535)

        self._selected=False

    def _focus_in(self, event):
        if not self._selected:
            self.editor.wavDisplay.set_activeLineSet(self.lineSet)
            self.selected = True

    def _focus_out(self, event):
        if self._selected:
            self.editor.wavDisplay.set_activeLineSet()
            self.selected = False

    def _start_set(self, *args):
        if self.rootSet is None:
            self.rootSet = self._start_set

            if self.loopStart.get() < self.start.get():
                self.loopStart.set(self.start.get())
            if self.stop.get() < self.start.get():
                self.stop.set(self.start.get())
            
            self.editor.wavDisplay.display_sample(self.start.get())
            self.rootSet = None

        start = self.start.get()
        self.esli.OSC_StartPoint_address = start*self.blockAlign
        # update the offsets
        self.esli.OSC_LoopStartPoint_offset = (self.loopStart.get()-start)*self.blockAlign
        self.esli.OSC_EndPoint_offset = (self.stop.get()-start)*self.blockAlign
        
        self.editor.wavDisplay.set_activeLineSet(self.lineSet)
        self.editor.wavDisplay.refresh(True)

    def _stop_set(self, *args):
        if self.rootSet is None:
            self.rootSet = self._stop_set
            
            if self.start.get() > self.stop.get():
                self.start.set(self.stop.get())
            if self.loopStart.get() > self.stop.get():
                self.loopStart.set(self.stop.get())

            self.editor.wavDisplay.display_sample(self.stop.get())
            self.rootSet = None

        start = self.start.get()
        stop = self.stop.get()
        loopStart = self.loopStart.get()
        self.esli.OSC_EndPoint_offset = (stop-start)*self.blockAlign
        if self.rootSet is None and self.oneshot:
            # can't be oneShot and have loopStart != stop
            if loopStart != stop:
                self.smpl.oneShot.set(False)
            else:
                self.smpl.oneShot.set(True)
        self.editor.wavDisplay.set_activeLineSet(self.lineSet)
        self.editor.wavDisplay.refresh(True)

    def _loopStart_set(self, *args):
        if self.rootSet is None:
            self.rootSet = self._loopStart_set
            
            if self.start.get() > self.loopStart.get():
                self.start.set(self.loopStart.get())
            if self.stop.get() < self.loopStart.get():
                self.stop.set(self.loopStart.get())

            self.editor.wavDisplay.display_sample(self.loopStart.get())
            self.rootSet = None

        start = self.start.get()
        stop = self.stop.get()
        loopStart = self.loopStart.get()
        self.esli.OSC_LoopStartPoint_offset = (loopStart-start)*self.blockAlign
        if self.rootSet is None and self.oneshot:
            # can't be oneShot and have loopStart != stop
            if loopStart != stop:
                self.smpl.oneShot.set(False)
            else:
                self.smpl.oneShot.set(True)
        self.editor.wavDisplay.set_activeLineSet(self.lineSet)
        self.editor.wavDisplay.refresh(True)
    
    def _playVolume_set(self, *args):
        playVolume = self.playVolume.get()

        if playVolume > 65535:
            self.playVolume.set(65535)
            playVolume = 65535
        elif playVolume < 0:
            self.playVolume.set(0)
            playVolume = 0

        self.esli.playVolume = playVolume
        self.editor.wavDisplay.refresh(True)
class SlicedSampleOptions(tk.LabelFrame):
    def __init__(self, parent, editor, *arg, **kwarg):
        super().__init__(parent, *arg, **kwarg)

        self.frameSlices = FrameSlices(self, editor)
        self.frameSlices.pack(fill=tk.BOTH, expand=tk.YES)

    def set_sample(self, fmt, data, esli):
        self.frameSlices.set_sample(fmt,data,esli)

class SliceEditor(tk.Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.esli=None

        # Some config width height settings
        canvas_width = 640
        canvas_height = 240

        self.wavDisplay = WaveDisplay(self, width=canvas_width, height=canvas_height)
        self.wavDisplay.pack(fill=tk.BOTH, expand=tk.YES, padx=2)
        self.h_scroll = tk.Scrollbar(self, orient=tk.HORIZONTAL, command=self.scroll_wav)
        self.h_scroll.pack(fill=tk.X, expand=tk.NO, padx=2)
        self.wavDisplay.set_scrollBar(self.h_scroll)

        framezoom = tk.Frame(self)
        framezoom.pack(fill=tk.X, expand=tk.NO)
        tk.Label(framezoom,text="Zoom:").pack(side=tk.LEFT)
        self.zoomVar=tk.StringVar()
        self.zoomVar.trace("w",self._zoom_edit)
        self.zoomEdit = ROSpinbox(framezoom, values=('all',), textvariable=self.zoomVar)
        self.zoomEdit.pack(side=tk.LEFT)
        
        self.frame = VerticalScrolledFrame(self)
        self.frame.pack(fill=tk.BOTH, expand=tk.YES)

        self.normalSampleOptions = NormalSampleOptions(self.frame.interior, self, text="Normal sample options")
        self.normalSampleOptions.pack(side=tk.TOP, fill=tk.BOTH, expand=tk.NO)

        self.slicedSampleOptions = SlicedSampleOptions(self.frame.interior, self, text="Sliced sample options")
        self.slicedSampleOptions.pack(side=tk.TOP, fill=tk.BOTH, expand=tk.NO)

        frame = tk.Frame(self.frame.interior)
        frame.pack()
        
        self.slicedRadioV = tk.BooleanVar()
        self.radioUseNormal = tk.Radiobutton(frame, text="Normal sample", variable=self.slicedRadioV, value=False, state=tk.DISABLED)
        self.radioUseNormal.grid(row=0,column=0,sticky=tk.W)        

        self.radioUseSliced = tk.Radiobutton(frame, text="Sliced sample", variable=self.slicedRadioV, value=True, state=tk.DISABLED)
        self.radioUseSliced.grid(row=1,column=0,sticky=tk.W)

        tk.Label(frame,text="Steps").grid(row=0,column=1,sticky=tk.E)
        tk.Label(frame,text="/").grid(row=0,column=2)
        tk.Label(frame,text="Beat").grid(row=0,column=3,sticky=tk.W)
        tk.Label(frame,text="Active Steps").grid(row=0,column=4)
        
        self.numSteps = tk.IntVar()
        self.numStepsTrace = None
        self.numActiveSteps = tk.IntVar()
        self.numActiveStepsTrace = None
        self.numStepsEdit = ROSpinbox(frame, from_=0, to=64, width=2, textvariable=self.numSteps)
        self.numStepsEdit.grid(row=1,column=1,sticky=tk.E)
        tk.Label(frame,text="/").grid(row=1,column=2)
        self.beat = tk.StringVar()
        self.beatTrace = None
        self.beatEdit = ROSpinbox(frame, values=tuple(sorted(e2s.esli_beat, key=e2s.esli_beat.get)), width=6, textvariable=self.beat)
        self.beatEdit.grid(row=1,column=3,sticky=tk.W)
        self.numActiveStepsEntry = tk.Entry(frame, width=2, textvariable=self.numActiveSteps, state=tk.DISABLED)
        self.numActiveStepsEntry.grid(row=1,column=4)

        frame = tk.Frame(self.frame.interior)
        frame.pack()

        self.activeSteps= []
        self.activeStepsTrace = []
        for j in range(64):
            self.activeSteps.append(tk.StringVar())
            self.activeStepsTrace.append(None)
        
        self.activeStepsEntry = []
        for j in range(4):
            tk.Label(frame, text="Step : ").grid(row=j*2+0, column=0)
            tk.Label(frame, text="Slice : ").grid(row=j*2+1, column=0)
            for i in range(16):
                tk.Label(frame, text=j*16+i+1).grid(row=j*2+0,column=i+1)
                self.activeStepsEntry.append(ROSpinbox(frame, values=("Off",)+tuple(range(64)), width=3, textvariable=self.activeSteps[j*16+i]))
                # bug? 'textvariable' must be configured later than 'values' to be used
                #self.activeStepsEntry[j*16+i].config(textvariable=self.activeSteps[j*16+i])
                self.activeStepsEntry[j*16+i].grid(row=j*2+1,column=i+1)
        
        tk.Button(frame, text="Off them all", command=self.allActiveStepsOff).grid(row=8, column=0, columnspan=17, padx=5, pady=5)

    def allActiveStepsOff(self):
        for j in range(64):
            self.activeSteps[j].set("Off")

    def _zoom_edit(self, *args):
        zoomStr = self.zoomVar.get()
        
        if zoomStr == 'all':
            self.wavDisplay.set_disp(0,self.wavDisplay.wav_length())
        else:
            zoom = float(zoomStr)
            self.wavDisplay.set_zoom_x(zoom)
        
    
    def scroll_wav(self, command, *args):
        if command == tk.MOVETO:
            offset = float(args[0])
            scroll_tot = self.wavDisplay.wav_length()
            self.wavDisplay.scroll_to(scroll_tot * offset)
        elif command == tk.SCROLL:
            step = float(args[0])
            what = args[1]
            
            if what == "units":
                self.wavDisplay.scroll_pix_stop(step*16)
            elif what == "pages":
                self.wavDisplay.scroll_pix_stop(step*self.wavDisplay.width/2)
            else:
                raise Exception("Unknown scroll unit: " + what)

    def set_sample(self, smpl):
        self.smpl = smpl

        fmt = smpl.e2s_sample.get_fmt()
        data = smpl.e2s_sample.get_data()
        esli = smpl.e2s_sample.get_esli()        

        self.esli = esli
        self.zoomVar.set('all')
        #compute zoom 'all' factor:
        zoom_all = self.wavDisplay.width/(len(data)//fmt.blockAlign)
        zooms = [16., 8., 4., 2., 1.]
        curr_zoom=0.5
        while curr_zoom > zoom_all:
            zooms.append(curr_zoom)
            curr_zoom /= 2
        zooms.append('all')
        zooms.reverse()
        self.zoomEdit.config(values=tuple(zooms))
        #self.zoomEdit.config(values=('all', 0.0625, 0.125, 0.25, 0.5, 1. ,2. ,4., 8., 16.))
        self.wavDisplay.set_wav(fmt, data)
        self.normalSampleOptions.set_sample(smpl)
        self.slicedSampleOptions.set_sample(fmt, data, esli)
        
        if self.numActiveStepsTrace:
            self.numActiveSteps.trace_vdelete('w', self.numActiveStepsTrace)

        for j in range(64):
            if self.activeStepsTrace[j]:
                self.activeSteps[j].trace_vdelete('w', self.activeStepsTrace[j])
            self.activeSteps[j].set(str(esli.sliceSteps[j]) if esli.sliceSteps[j] >= 0 else "Off")
            self.activeStepsTrace[j] =  self.activeSteps[j].trace('w', lambda *args, j=j: self._activeStepEdit(j))

        if self.numStepsTrace:
            self.numSteps.trace_vdelete('w', self.numStepsTrace)
        self.numSteps.set(esli.slicingNumSteps)
        self.numStepsTrace = self.numSteps.trace('w', self._numStepsEdit)
                
        if self.beatTrace:
            self.beat.trace_vdelete('w', self.beatTrace)
        self.beat.set(e2s.esli_beat_to_str.get(esli.slicingBeat))
        self.beatTrace = self.beat.trace('w', self._beatEdit)

        self.numActiveSteps.set(esli.slicesNumActiveSteps)
        self.numActiveStepsTrace = self.numActiveSteps.trace('w', self._numActiveStepsChanged)
        
        self.slicedRadioV.set(self.numActiveSteps.get()>0)

        #reset view point of vertical scroll
        self.frame.canvas.xview_moveto(0)
        self.frame.canvas.yview_moveto(0)

    def _activeStepEdit(self, index):
        value = self.activeSteps[index].get()
        self.esli.sliceSteps[index] = int(value) if value != "Off" else -1
        self._updateSlicesNumActiveSteps()
        
    def _numStepsEdit(self, *args):
        numSteps = self.numSteps.get()
        self.esli.slicingNumSteps = numSteps
        self._updateSlicesNumActiveSteps()
        #self.slicedRadioV.set(numSteps>0)
        
    def _beatEdit(self, *args):
        self.esli.slicingBeat = e2s.esli_beat.get(self.beat.get())
        self._limitNumSteps()
        self._updateSlicesNumActiveSteps()
    
    def _limitNumSteps(self):
        if self.beat.get() in ('8 Tri','16 Tri'):
            self.numStepsEdit.config(to=48)
            if self.numSteps.get() > 48:
                self.numSteps.set(48)
        else:
            self.numStepsEdit.config(to=64)
        
        
    def _updateSlicesNumActiveSteps(self):
        numActiveSteps=0
        for i in range(self.numSteps.get()):
            numActiveSteps += 1 if self.activeSteps[i].get() != "Off" else 0
        self.numActiveSteps.set(numActiveSteps)
    
    def _numActiveStepsChanged(self, *args):
        self.esli.slicesNumActiveSteps = self.numActiveSteps.get()
        self.slicedRadioV.set(self.numActiveSteps.get()>0)

class SliceEditorDialog(tk.Toplevel):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.withdraw()
        self.transient(parent)
        self.protocol("WM_DELETE_WINDOW", self.on_delete)
        
        self.sliceEditor = SliceEditor(self)
        self.sliceEditor.pack(fill=tk.BOTH, expand=tk.YES)
        
    def run(self):
        self.deiconify()
        
        self.grab_set()        
        
        self.focus_set()
        
    def on_delete(self):
        audio.player.play_stop()
        self.withdraw()
        
        parent=self.master
        parent.grab_set()
        parent.focus_set()
        parent.restore_binding()
        

class Sample(object):
    OSC_caths = ('Analog',
                 'Audio In',
                 'Kick',
                 'Snare',
                 'Clap',
                 'HiHat',
                 'Cymbal',
                 'Hits',
                 'Shots',
                 'Voice',
                 'SE',
                 'FX',
                 'Tom',
                 'Perc.',
                 'Phrase',
                 'Loop',
                 'PCM',
                 'User')
    
    def __init__(self, master, lineNum, e2s_sample):
        self.master = master
       
        self.e2s_sample = e2s_sample
        
        self.name = tk.StringVar()
        self.oscNum = tk.IntVar()
        self.oscCat = tk.StringVar()
        self.oneShot = tk.BooleanVar()
        self.plus12dB = tk.BooleanVar()
        self.tuneVal = tk.IntVar()
        self.samplingFreq= tk.IntVar()
        self.duration=tk.StringVar()
        self.stereo=tk.BooleanVar()
        self.smpSize=tk.IntVar()
        
        self.name_trace = None
        self.oscNum_trace = None
        self.oscCat_trace = None
        self.oneShot_trace = None
        self.plus12dB_trace = None
        self.tuneVal_trace = None

        self.reset_vars()
        
        self.radioButton = tk.Radiobutton(self.master, variable=self.master.selectV)
        self.entryOscNum = SampleNumSpinbox(self.master, width=3, textvariable=self.oscNum, command=self._oscNum_command)
        self.entryOscNum._prev = self.oscNum.get()
        self.entryName = tk.Entry(self.master, width=16, textvariable=self.name)
        self.entryOscCat  = ROSpinbox(self.master, values=Sample.OSC_caths, width=8)
        # bug? 'textvariable' must be configured later than 'values' to be used
        self.entryOscCat.config(textvariable=self.oscCat)
        self.checkOneShot = tk.Checkbutton(self.master, variable=self.oneShot)
        self.check12dB = tk.Checkbutton(self.master, variable=self.plus12dB)
        self.entryTune = ROSpinbox(self.master, from_=-63, to=63, width=3, format='%2.0f', textvariable=self.tuneVal)
        self.buttonPlay = tk.Button(self.master, image=GUI.res.playIcon, command=self.play)
        self.samplingFreqEntry = SampleNumSpinbox(self.master, width=8, textvariable=self.samplingFreq, justify=tk.RIGHT, command=self._samplingFreq_command)
        self.durationEntry = tk.Entry(self.master, width=8, textvariable=self.duration, state=tk.DISABLED, justify=tk.RIGHT)
        self.checkStereo = tk.Checkbutton(self.master, variable=self.stereo, command=self._stereo_command)
        self.sizeEntry = tk.Entry(self.master, width=8, textvariable=self.smpSize, state=tk.DISABLED, justify=tk.RIGHT)

        self.set_lineNum(lineNum)

    def destroy(self):
        self.radioButton.destroy()
        self.entryOscNum.destroy()
        self.entryName.destroy()
        self.entryOscCat.destroy()
        self.checkOneShot.destroy()
        self.check12dB.destroy()
        self.entryTune.destroy()
        self.buttonPlay.destroy()
        self.samplingFreqEntry.destroy()
        self.durationEntry.destroy()
        self.checkStereo.destroy()
        self.sizeEntry.destroy()

    def set_lineNum(self, lineNum):
        self.lineNum = lineNum

        row = lineNum+1

        self.radioButton.config(value=lineNum)
        self.radioButton.grid(row=row, column=0)        
        self.entryOscNum.grid(row=row, column=1)
        self.entryName.grid(row=row, column=2)
        self.entryOscCat.grid(row=row, column=3)
        self.checkOneShot.grid(row=row,column=4)
        self.check12dB.grid(row=row,column=5)
        self.entryTune.grid(row=row,column=6)
        self.buttonPlay.grid(row=row, column=7)
        self.samplingFreqEntry.grid(row=row, column=8)
        self.durationEntry.grid(row=row, column=9)
        self.checkStereo.grid(row=row, column=10)
        self.sizeEntry.grid(row=row, column=11)
        
        
        self.entryOscNum.config(from_=lineNum+19 if lineNum+19<422 else lineNum+19+79, to=999)
        # RIFF_korg_esli.playLogPeriod has a 0.5814686990855805 to 1536036.6940220615 frequency range
        self.samplingFreqEntry.config(from_=1, to=1536036)

    def move_to_lineNum(self, lineNum):
        self.set_lineNum(lineNum)
        
    def reset_vars(self):
        if self.name_trace:
            self.name.trace_vdelete('w', self.name_trace)
        if self.oscNum_trace:
            self.oscNum.trace_vdelete('w', self.oscNum_trace)
        if self.oscCat_trace:
            self.oscCat.trace_vdelete('w', self.oscCat_trace)        
        if self.oneShot_trace:
            self.oneShot.trace_vdelete('w', self.oneShot_trace)
        if self.plus12dB_trace:
            self.plus12dB.trace_vdelete('w', self.plus12dB_trace)
        if self.tuneVal_trace:
            self.tuneVal.trace_vdelete('w', self.tuneVal_trace)
        
        esli = self.e2s_sample.get_esli()
        fmt = self.e2s_sample.get_fmt()
        data = self.e2s_sample.get_data()
        self.name.set(esli.OSC_name.decode("utf-8").rstrip('\x00'))
        self.oscNum.set(esli.OSC_0index+1)
        self.oscCat.set(Sample.OSC_caths[esli.OSC_category])
        self.oneShot.set(esli.OSC_OneShot)
        self.plus12dB.set(esli.playLevel12dB)
        self.tuneVal.set(esli.sampleTune)
        self.samplingFreq.set(esli.samplingFreq)
        if fmt.samplesPerSec != esli.samplingFreq:
            print("Warning: sampling frequency differs between esli and fmt")
        self.duration.set("{:.4f}".format(len(data)/fmt.avgBytesPerSec if fmt.avgBytesPerSec else 0))
        self.stereo.set(fmt.channels > 1)
        self.smpSize.set(len(data))

        self.name_trace = self.name.trace('w', self._name_set)        
        self.oscNum_trace = self.oscNum.trace('w', self._oscNum_set)        
        self.oscCat_trace = self.oscCat.trace('w', self._oscCat_set)        
        self.oneShot_trace = self.oneShot.trace('w', self._oneShot_set)        
        self.plus12dB_trace = self.plus12dB.trace('w', self._plus12dB_set)        
        self.tuneVal_trace = self.tuneVal.trace('w', self._tuneVal_set)        
    
    def _name_set(self, *args):
        # TODO verify which encoding is used by electribe sampler
        esli = self.e2s_sample.get_esli()
        esli.OSC_name = bytes(self.name.get().encode('utf-8'))
        self.name.set(esli.OSC_name.decode("utf-8").rstrip('\x00'))
    
    def _oscNum_set(self, *args):
        oscNum = self.oscNum.get()
        if 422 <= oscNum <= 500:
            if self.entryOscNum._prev < oscNum:
                self.oscNum.set(501)
            else:
                self.oscNum.set(421)
            oscNum = self.oscNum.get()
        self.e2s_sample.get_esli().OSC_0index = oscNum-1
        self.e2s_sample.get_esli().OSC_0index1 = oscNum-1
        self.entryOscNum._prev = oscNum
    
    def _oscNum_command(self):
        oscNum = self.oscNum.get()
        lN = self.lineNum
        samples = self.master.samples

        maxval = 1000-len(samples)+lN
        if maxval <= 500:
            maxval -= 79
        
        if oscNum > maxval:
            self.oscNum.set(maxval)
            oscNum = self.oscNum.get()
        
        if lN and samples[lN-1].oscNum.get() >= oscNum:
            # was decreased
            # check that we will not go under 19 is not necessary while 
            # is setself.entryOscNum.config(from_=lineNum+19, to=999)
            while lN and samples[lN-1].oscNum.get() >= samples[lN].oscNum.get():
                samples[lN-1].oscNum.set(samples[lN].oscNum.get()-1 if samples[lN].oscNum.get() != 501 else 421)
                lN -= 1
        elif lN < len(samples)-1 and samples[lN+1].oscNum.get() <= oscNum:
            # was increased, look if possible
            #if len(samples)-1 - lN <= 999 - oscNum:
            while lN < len(samples)-1 and samples[lN+1].oscNum.get() <= samples[lN].oscNum.get():
                samples[lN+1].oscNum.set(samples[lN].oscNum.get()+1 if samples[lN].oscNum.get() != 421 else 501)
                lN += 1
            #else:
            #    self.oscNum.set(oscNum-1)

    def _oscCat_set(self, *args):
        self.e2s_sample.get_esli().OSC_category = e2s.esli_str_to_OSC_cat[self.oscCat.get()]
    
    def _oneShot_set(self, *args):
        oneShot = self.oneShot.get()
        if oneShot and self.e2s_sample.get_esli().OSC_LoopStartPoint_offset != self.e2s_sample.get_esli().OSC_EndPoint_offset:
            if tk.messagebox.askyesno("Loop Start is set", "Loop start shall be reset to allow one shot.\nContinue?"):
                self.e2s_sample.get_esli().OSC_LoopStartPoint_offset = self.e2s_sample.get_esli().OSC_EndPoint_offset
                self.e2s_sample.get_esli().OSC_OneShot = oneShot
            else:
                self.oneShot.set(False)
                # update checkbutton
                self.checkOneShot.config(state=tk.NORMAL)
        else:
            self.e2s_sample.get_esli().OSC_OneShot = oneShot
        
    def _plus12dB_set(self, *args):
        self.e2s_sample.get_esli().playLevel12dB = self.plus12dB.get()
    
    def _tuneVal_set(self, *args):
        self.e2s_sample.get_esli().sampleTune = self.tuneVal.get()
    
    def _samplingFreq_command(self, *ars):
        sFreq = self.samplingFreq.get()
        esli = self.e2s_sample.get_esli()
        fmt = self.e2s_sample.get_fmt()
        data = self.e2s_sample.get_data()
        esli.samplingFreq = sFreq
        # by default play speed is same as indicated by Frequency
        esli.playLogPeriod = 65535 if sFreq == 0 else max(0, int(round(63132-math.log2(sFreq)*3072)))
        fmt.samplesPerSec = sFreq
        fmt.avgBytesPerSec = sFreq*fmt.blockAlign
        self.duration.set("{:.4f}".format(len(data)/fmt.avgBytesPerSec if fmt.avgBytesPerSec else 0))

    def _stereo_command(self,*args):
        # don't switch immediately
        self.stereo.set(not self.stereo.get())
        if not self.stereo.get():
            # mono can't be set to stereo
            return
        dialog = StereoToMonoDialog(self.checkStereo, self.e2s_sample)
        self.master.wait_window(dialog)
        fmt = self.e2s_sample.get_fmt()
        self.stereo.set(fmt.channels > 1)
        data = self.e2s_sample.get_data()
        self.smpSize.set(len(data))
        self.master.update_WAVDataSize()

    def exchange_with(self, other):
        # swap samples
        self.e2s_sample, other.e2s_sample = other.e2s_sample, self.e2s_sample
        # swap osc indexes
        self_esli = self.e2s_sample.get_esli()
        othe_esli = other.e2s_sample.get_esli()
        osc_index = self_esli.OSC_0index
        self_esli.OSC_0index=self_esli.OSC_0index1=othe_esli.OSC_0index
        othe_esli.OSC_0index=othe_esli.OSC_0index1=osc_index
        
        self.reset_vars()
        other.reset_vars()
        self.entryOscNum._prev = self_esli.OSC_0index+1
        other.entryOscNum._prev = othe_esli.OSC_0index+1


    def play(self):
        # TODO: have a single wav player for the whole application
        self.master.play(self.e2s_sample)
        
class SampleList(tk.Frame):
    def __init__(self, *arg, **kwarg):
        super().__init__(*arg, **kwarg)
        tk.Label(self, text="#Num").grid(row=0, column=1)
        tk.Label(self, text="Name").grid(row=0, column=2)
        tk.Label(self, text="Cat.").grid(row=0, column=3)
        tk.Label(self, text="1-shot").grid(row=0, column=4)
        tk.Label(self, text="+12dB").grid(row=0, column=5)
        tk.Label(self, text="Tune").grid(row=0, column=6)
        tk.Label(self, text="Freq (Hz)").grid(row=0, column=8)
        tk.Label(self, text="Time (s)").grid(row=0, column=9)
        tk.Label(self, text="Stereo").grid(row=0,column=10)
        tk.Label(self, text="Data Size").grid(row=0, column=11)
        
        self.selectV = tk.IntVar()

        self.WAVDataSize = tk.IntVar()

        self.samples = []
        
        self.canvas_name = arg[0].winfo_parent()

    def get_next_free_sample_index(self):
        max=17
        for sample in self.samples:
            if sample.e2s_sample.get_esli().OSC_0index > max:
                max = sample.e2s_sample.get_esli().OSC_0index
        if 421 <= max <= 499:
            max = 500
        if max<998:
            return max+1
        else:
            # find first free
            for i in range(18,999):
                if 421 <= i <= 499:
                    continue
                found = False
                for sample in self.samples:
                    if sample.e2s_sample.get_esli().OSC_0index == i:
                        found = True
                        break
                if not found:
                    return i
            return None
    
    def get_canvas(self):
        return self._nametowidget(self.canvas_name)

    def get_view_bbox(self):
        canvas = self.get_canvas() 
        x=canvas.canvasx(0)
        y=canvas.canvasy(0)
        w=canvas.winfo_width()
        h=canvas.winfo_height()
        return (x, y, w, h)

    def get_selected(self):
        if 0 <= self.selectV.get() < len(self.samples):
            return self.samples[self.selectV.get()]
        else:
            return None

    def update_WAVDataSize(self):
        self.WAVDataSize.set(sum( (s.smpSize.get() for s in self.samples) ))
    
    def add_new(self, e2s_sample):
        self.samples.append(Sample(self,len(self.samples),e2s_sample))
        self.WAVDataSize.set(self.WAVDataSize.get()+self.samples[-1].smpSize.get())
        lineNum=len(self.samples)-1
        #sort
        while lineNum > 1:
            cr_index = self.samples[lineNum].oscNum.get()
            pr_index = self.samples[lineNum-1].oscNum.get()
            if cr_index > pr_index:
                break
            self.move_up(lineNum)
            if self.selectV.get() == lineNum-1:
                self.selectV.set(lineNum)
            lineNum -= 1
                
    
    def remove(self, line_num):
        if 0 <= line_num < len(self.samples):
            self.WAVDataSize.set(self.WAVDataSize.get()-self.samples[line_num].smpSize.get())
            self.samples[line_num].destroy()
            if line_num < len(self.samples)-1:
                for i in range(line_num, len(self.samples)-1):
                    self.samples[i+1].move_to_lineNum(i)
            else:
                if len(self.samples) > 1:
                    self.selectV.set(self.selectV.get()-1) 
            del self.samples[line_num]

    def clear(self):
        for sample in reversed(self.samples):
            sample.destroy()
        self.samples.clear()
        self.WAVDataSize.set(0)
        self.selectV.set(0)
        canvas = self.get_canvas()
        canvas.yview('moveto', 0.)
        
    def move_up(self, line_num):
        if 0 < line_num < len(self.samples):
            self.samples[line_num].exchange_with(self.samples[line_num-1])
            return True
        return False

    def move_down(self, line_num):
        if 0 <= line_num < len(self.samples)-1:
            self.samples[line_num].exchange_with(self.samples[line_num+1])
            return True
        return False

    def show_selected(self):
        vbb = self.get_view_bbox()
        canvas = self.get_canvas()
        y_selected = self.samples[self.selectV.get()].entryName.winfo_y()
        h_selected = self.samples[self.selectV.get()].entryName.winfo_height()
        if y_selected < vbb[1]:
            canvas.yview('moveto', y_selected/self.winfo_height())
        elif y_selected + h_selected > vbb[1] + vbb[3]:
            canvas.yview('moveto', (y_selected+h_selected-canvas.winfo_height())/self.winfo_height())
            
    def move_up_selected(self):
        if self.move_up(self.selectV.get()):
            self.selectV.set(self.selectV.get()-1)
            self.show_selected()
                
        
    def move_down_selected(self):
        if self.move_down(self.selectV.get()):
            self.selectV.set(self.selectV.get()+1)
            self.show_selected()
            
    def remove_selected(self):
        self.remove(self.selectV.get())

    def play(self, e2s_sample):
        riff_fmt = e2s_sample.get_fmt()
        audio.player.play_start(audio.Sound(e2s_sample.get_data().rawdata,riff_fmt))
        
class About(tk.Toplevel):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.transient(parent)
        self.title('About Open e2sSample.all Library Editor')
        self.resizable(width=tk.FALSE, height=tk.FALSE)

        self.parent=parent

        body = tk.Frame(self)
        self.text = tk.Text(body,state=tk.NORMAL,width=80)
        self.text.pack()
        body.pack(padx=5, pady=5)
        
        text = self.text
        text.config(cursor="arrow")
        text.insert(tk.INSERT,"Oe2sSLE "+str(Oe2sSLE_VERSION[0])+"."+str(Oe2sSLE_VERSION[1])+"."+str(Oe2sSLE_VERSION[2])+"\n")
        text.insert(tk.END,
"""
Home Page : """)
        text.tag_config("link-home", foreground="blue", underline=1)
        text.tag_bind("link-home", "<Button-1>", lambda event: webbrowser.open('http://mayflyshare.com/Oe2sSLE'))
        text.insert(tk.END, "<http://mayflyshare.com/Oe2sSLE>", "link-home")
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

        text.insert(tk.END, """

To contribute or support, visit """)
        text.tag_config("link-github", foreground="blue", underline=1)
        text.tag_bind("link-github", "<Button-1>", lambda event: webbrowser.open('https://github.com/JonathanTaquet/Oe2sSLE/'))
        text.insert(tk.END, "<https://github.com/JonathanTaquet/Oe2sSLE/>", "link-github")
        
        text.config(state=tk.DISABLED)        
        
        self.focus_set()

class SampleAllEditor(tk.Tk):
    """
    TODO:
    - check box: import sample and keep original number
    - sort imported samples
    - check box: remove unhandled chunks
    - button: edit sample
    """    
    
    factory_importNums = [
        i for i in range( 50, 86)] + [
        i for i in range( 87,113)] + [
        i for i in range(114,126)] + [
        i for i in range(127,136)] + [
        i for i in range(137,182)] + [
        i for i in range(183,184)] + [
        i for i in range(185,186)] + [
        i for i in range(187,189)] + [
        i for i in range(190,461)]

    def __init__(self, *args, **kw):
        self.root = tk.Tk.__init__(self, *args, **kw)
        GUI.res.init()

        root = self.root

        # Set the window title
        self.wm_title("Open e2sSample.all Library Editor")
        self.minsize(width=600,height=500)
        
        # user samples are starting at ~550 but sample number must start at 501 ?
        self.import_num=550

        self.sliceEditDialog = None

        self.mainFrame = tk.Frame(root)
        self.mainFrame.pack(fill=tk.BOTH, expand=tk.YES, side=tk.LEFT)
        
        self.frame = VerticalScrolledFrame(self.mainFrame)
        self.frame.pack(fill=tk.BOTH, expand=tk.YES)
        
        self.sampleList = SampleList(self.frame.interior)
        self.sampleList.pack(fill=tk.BOTH, expand=tk.YES)
        
        fr = tk.Frame(self.mainFrame)
        self.moveUp100Button = tk.Button(fr, text='<<<', command=lambda: [self.sampleList.move_up_selected() for i in range(100) ])
        self.moveUp100Button.pack(side=tk.LEFT)

        self.moveUp10Button = tk.Button(fr, text='<<', command=lambda: [self.sampleList.move_up_selected() for i in range(10) ])
        self.moveUp10Button.pack(side=tk.LEFT)

        self.moveUpButton = tk.Button(fr, text='<', command=self.sampleList.move_up_selected)
        self.moveUpButton.pack(side=tk.LEFT)

        self.moveDownButton = tk.Button(fr, text='>', command=self.sampleList.move_down_selected)
        self.moveDownButton.pack(side=tk.LEFT)

        self.moveDown10Button = tk.Button(fr, text='>>', command=lambda: [self.sampleList.move_down_selected() for i in range(10) ])
        self.moveDown10Button.pack(side=tk.LEFT)

        self.moveDown100Button = tk.Button(fr, text='>>>', command=lambda: [self.sampleList.move_down_selected() for i in range(100) ])
        self.moveDown100Button.pack(side=tk.LEFT)
        fr.pack()


        fr = tk.Frame(self.mainFrame)
        self.buttonEdit = tk.Button(fr, text="Edit Selected", command=self.edit_selected)
        self.buttonEdit.pack(side=tk.TOP, fill=tk.BOTH)

        self.buttonRem = tk.Button(fr, text="Remove Selected", command=self.sampleList.remove_selected)
        self.buttonRem.pack(side=tk.TOP, fill=tk.BOTH)        

        self.buttonAdd = tk.Button(fr, text="Import wav Sample(s)", command=self.import_sample)
        self.buttonAdd.pack(side=tk.TOP, fill=tk.BOTH)
        
        self.buttonAdd = tk.Button(fr, text="Import e2sSample.all", command=self.import_all_sample)
        self.buttonAdd.pack(side=tk.TOP, fill=tk.BOTH)

        self.buttonExp = tk.Button(fr, text="Export Selected as wav", command=self.export_sample)
        self.buttonExp.pack(side=tk.TOP, fill=tk.BOTH)
        
        self.buttonExp = tk.Button(fr, text="Export all as wav", command=self.export_all_sample)
        self.buttonExp.pack(side=tk.TOP, fill=tk.BOTH)

        self.buttonLoad = tk.Button(fr, text="Open", command=self.load)
        self.buttonLoad.pack(side=tk.LEFT,fill=tk.Y)

        self.buttonClear = tk.Button(fr, text="Clear all", command=self.clear)
        self.buttonClear.pack(side=tk.RIGHT)

        self.buttonSaveAs = tk.Button(fr, text="Save As", command=self.save_as)
        self.buttonSaveAs.pack(side=tk.TOP,fill=tk.Y)
        fr.pack(fill=tk.X)

        self.restore_binding()

        fr = tk.Frame(self.mainFrame,borderwidth=2, relief='sunken')
        tk.Label(fr,text='/ '+str(e2s.WAVDataMaxSize)).pack(side=tk.RIGHT)
        self.sizeEntry = tk.Entry(fr, width=8, textvariable=self.sampleList.WAVDataSize, state=tk.DISABLED, justify=tk.RIGHT)
        self.sizeEntry.pack(side=tk.RIGHT)
        tk.Label(fr,text='Total Data Size : ').pack(side=tk.RIGHT)

        self.buttonDonate = tk.Button(fr, command=self.donate, image=GUI.res.pledgieIcon)
        self.buttonDonate.pack(side=tk.LEFT)
        
        self.buttonAbout=tk.Button(fr, text="About", command=self.about)
        self.buttonAbout.pack(side=tk.TOP)        
        fr.pack(side=tk.TOP,fill=tk.X)

    def donate(self):
        webbrowser.open('https://pledgie.com/campaigns/30817')
    
    def about(self):
        about = About(self.root)
        
    def clear(self):    
        wd = WaitDialog(self.root)
        wd.run(self.sampleList.clear)
            
    def load(self):
        filename = tk.filedialog.askopenfilename(parent=self.root,title="Select e2s Sample.all file to open",filetypes=(('.all Files','*.all'),('All Files','*.*')))
        if filename:
            def fct():
                try:
                    samplesAll = e2s.e2s_sample_all(filename=filename)
                except Exception as e:
                    tk.messagebox.showwarning(
                    "Open",
                    "Cannot use this file:\n{}\nError message:\n{}".format(filename, e)
                    )
                    return

                if samplesAll._loadErrors:
                    tk.messagebox.showwarning(
                    "Open",
                    ("Recovered from {} error(s) in this file:\n{}\n"
                     "The file is probably corrupted or you found a bug.\n"
                     "See log file for details."
                    )
                    .format(samplesAll._loadErrors, filename)
                    )
                
                self.sampleList.clear()
                for sample in samplesAll.samples:
                    self.sampleList.add_new(sample)
            wd = WaitDialog(self.root)
            wd.run(fct)
                
    def save_as(self):
        if not self.sampleList.WAVDataSize.get() > e2s.WAVDataMaxSize or tk.messagebox.askyesno("Memory overflow", "Are you sure to save with memory overflow?"):
            filename = tk.filedialog.asksaveasfilename(parent=self.root,title="Save as e2s Sample.all file",defaultextension='.all',filetypes=(('.all Files','*.all'),('All Files','*.*')),initialfile='e2sSample.all')
            if filename:
                def fct():
                    # first assign correct OSC_importNum (maybe a bug of the electribe?)
                    # samples are ordered by esli.OSC_0index
                    for sample in self.sampleList.samples:
                        esli = sample.e2s_sample.get_esli()
                        if esli.OSC_0index < 500:
                            esli.OSC_importNum = self.factory_importNums[esli.OSC_0index-18]
                        else:
                            esli.OSC_importNum = 550+esli.OSC_0index-500
                            
                    sampleAll = e2s.e2s_sample_all()
                    for sample in self.sampleList.samples:
                        # make clean local copy (no external metadata)
                        e2s_sample = sample.e2s_sample.get_clean_copy()
                        sampleAll.samples.append(e2s_sample)
                    try:
                        sampleAll.save(filename)
                    except Exception as e:
                        tk.messagebox.showwarning(
                        "Save as",
                        "Cannot save to this file:\n{}\nError message:\n{}".format(filename, e)
                        )
                wd = WaitDialog(self.root)
                wd.run(fct)
        
    
    def import_sample(self):
        filenames = tk.filedialog.askopenfilenames(parent=self.root,title="Select WAV file(s) to import",filetypes=(('Wav Files','*.wav'), ('All Files','*.*')))
        def fct():
            converted = [[],[]] # (8 bits, 24 bits)
            for filename in filenames:
                try:
                    with open(filename, 'rb') as f:
                        sample = e2s.e2s_sample(f)
                except Exception as e:
                    tk.messagebox.showwarning(
                    "Import WAV",
                    "Cannot open this file:\n{}\nError message:\n{}".format(filename, e)
                    )
                    continue
                
                #check format
                fmt = sample.get_fmt()
                if fmt.formatTag != fmt.WAVE_FORMAT_PCM:
                    tk.messagebox.showwarning(
                    "Import WAV",
                    "Cannot use this file:\n{}\nWAV format must be WAVE_FORMAT_PCM".format(filename)
                    )
                    continue
                    
                if fmt.bitPerSample != 16:
                    if fmt.bitPerSample == 8:
                        wav_tools.wav_pcm_8b_to_16b(sample)
                        converted[0] += [filename]
                    elif fmt.bitPerSample == 24:
                        wav_tools.wav_pcm_24b_to_16b(sample)
                        converted[1] += [filename]
                    else:
                        tk.messagebox.showwarning(
                        "Import WAV",
                        "Cannot use this file:\n{}\nWAV format must preferably use 16 bits per sample.\n" +
                        "8 bits and old 24 bits per sample are also supported but will be converted to 16 bits.\n"
                        "Convert your file before importing it.".format(filename)
                        )
                        continue
                    fmt = sample.get_fmt()
                
                if not sample.RIFF.chunkList.get_chunk(b'korg'):
                    korg_data=e2s.RIFF_korg()
                    korg_chunk = RIFF.Chunk(header=RIFF.ChunkHeader(id=b'korg'),data=korg_data)
                    sample.RIFF.chunkList.chunks.append(korg_chunk)
                    sample.header.size += len(korg_chunk)
                
                korg_chunk = sample.RIFF.chunkList.get_chunk(b'korg')
                
                esli_chunk = korg_chunk.data.chunkList.get_chunk(b'esli')
                if not esli_chunk:
                    esli = e2s.RIFF_korg_esli()
                    esli_chunk = RIFF.Chunk(header=RIFF.ChunkHeader(id=b'esli'),data=esli)
                    korg_chunk.data.chunkList.chunks.append(esli_chunk)
                    esli.OSC_name = bytes(os.path.splitext(os.path.basename(filename))[0],"utf8")
                    #todo funtion for that:
                    data = sample.get_data()
                    esli.samplingFreq = fmt.samplesPerSec
                    esli.OSC_EndPoint_offset = esli.OSC_LoopStartPoint_offset = len(data) - fmt.blockAlign
                    esli.WAV_dataSize = len(data)
                    if fmt.blockAlign == 4:
                        # stereo
                        esli.useChan1 = True
                    # by default use maximum volume (not like electribe that computes a good value)
                    esli.playVolume = 65535
                    
                    esli.OSC_importNum = self.import_num
                    self.import_num += 1
                    # by default play speed is same as indicated by Frequency
                    esli.playLogPeriod = 65535 if fmt.samplesPerSec == 0 else max(0, int(round(63132-math.log2(fmt.samplesPerSec)*3072)))
                    esli_chunk.header.size += len(esli_chunk)
                    sample.header.size += len(esli_chunk)

                    # check if smpl chunk is used
                    smpl_chunk = sample.RIFF.chunkList.get_chunk(b'smpl')
                    if smpl_chunk:
                        # use it to initialize loop point
                        if smpl_chunk.data.numSampleLoops > 0:
                            # todo: if several LoopData, propose to generate several wavs ?
                            smpl_loop = smpl_chunk.data.loops[0]
                            if smpl_loop.playCount != 1:
                                # looping sample
                                start = smpl_loop.start*fmt.blockAlign
                                end = smpl_loop.end*fmt.blockAlign
                                if start < end and end <= len(data) - fmt.blockAlign:
                                    esli.OSC_LoopStartPoint_offset = start - esli.OSC_StartPoint_address
                                    esli.OSC_OneShot = 0
                                    esli.OSC_EndPoint_offset = end - esli.OSC_StartPoint_address
                    # check if cue chunk is used
                    cue_chunk = sample.RIFF.chunkList.get_chunk(b'cue ')
                    if cue_chunk:
                        num_cue_points = cue_chunk.data.numCuePoints
                        num_slices = 0
                        num_samples = len(data) // fmt.blockAlign
                        for cue_point_num in range(num_cue_points):
                            cue_point = cue_chunk.data.cuePoints[cue_point_num]
                            if cue_point.fccChunk != b'data' or cue_point.sampleOffset >= num_samples:
                                # unhandled cue_point
                                continue
                            else:
                                esli.slices[num_slices].start = cue_point.sampleOffset
                                esli.slices[num_slices].length = num_samples - cue_point.sampleOffset
                                if num_slices > 0:
                                    esli.slices[num_slices-1].length = esli.slices[num_slices].start - esli.slices[num_slices-1].start
                                num_slices += 1
                                if num_slices >= 64:
                                    break
                else:
                    esli = esli_chunk.data

                nextsampleIndex = self.sampleList.get_next_free_sample_index()
                if nextsampleIndex is not None:
                    esli.OSC_0index = esli.OSC_0index1 = nextsampleIndex
                    
                    self.sampleList.add_new(sample)
                else:
                    tk.messagebox.showwarning(
                    "Import WAV",
                    "Cannot use this file:\n{}\nToo many samples.".format(filename)
                    )
                    break
            if not all(n_conv == [] for n_conv in converted):
                tk.messagebox.showinfo(
                    "Import WAV",
                    ("{} file(s) converted from 8 bits to 16 bits.\n".format(len(converted[0])) if len(converted[0]) else "") +
                    ("{} file(s) converted from 24 bits to 16 bits.\n".format(len(converted[1])) if len(converted[1]) else "")
                    )

        wd = WaitDialog(self.root)
        wd.run(fct)
                
    def import_all_sample(self):
        filename = tk.filedialog.askopenfilename(parent=self.root,title="Select e2sSample.all file to import",filetypes=(('.all Files','*.all'),('All Files','*.*')))
        if filename:        
            def fct():
                try:
                    samplesAll = e2s.e2s_sample_all(filename=filename)
                except Exception as e:
                    tk.messagebox.showwarning(
                    "Import e2sSample.all",
                    "Cannot use this file:\n{}\nError message:\n{}".format(filename, e)
                    )
                    return
                if samplesAll._loadErrors:
                    tk.messagebox.showwarning(
                    "Import e2sSample.all",
                    ("Recovered from {} error(s) in this file:\n{}\n"
                     "The file is probably corrupted or you found a bug.\n"
                     "See log file for details."
                    )
                    .format(samplesAll._loadErrors, filename)
                    )
                
                for sample in samplesAll.samples:
                    esli = sample.get_esli()
    
                    nextsampleIndex = self.sampleList.get_next_free_sample_index()
                    if nextsampleIndex is not None:
                        esli.OSC_0index = esli.OSC_0index1 = nextsampleIndex
                        
                        self.sampleList.add_new(sample)
                    else:
                        tk.messagebox.showwarning(
                        "Import e2sSample.all",
                        "Too many samples."
                        )
                        break

            wd = WaitDialog(self.root)
            wd.run(fct)

    def export_sample(self):
        if self.sampleList.samples:
            filename = tk.filedialog.asksaveasfilename(parent=self.root,title="Export sample as",defaultextension='.wav',filetypes=(('Wav Files','*.wav'), ('All Files','*.*'))
                                                      ,initialfile="{:0>3}_{}.wav".format(self.sampleList.get_selected().oscNum.get(),self.sampleList.get_selected().name.get()))
            if filename:
                try:
                    with open(filename, 'wb') as f:
                        self.sampleList.get_selected().e2s_sample.write(f)
                except Exception as e:
                    tk.messagebox.showwarning(
                    "Export sample as",
                    "Cannot save sample as:\n{}\nError message:\n{}".format(filename, e)
                    )

    def export_all_sample(self):
        if self.sampleList.samples:
            directory = tk.filedialog.askdirectory(parent=self.root,title="Export all samples to directory",mustexist=True)
            def fct():
                if directory:
                    # check files do not exist
                    for sample in self.sampleList.samples:
                        filename = "{:0>3}_{}.wav".format(sample.oscNum.get(),sample.name.get())
                        filename = filename.replace('/','-').replace('\\','-')
                        filename = directory+"/"+filename
                        # TODO: dialog to ask if replace/replace-all or select new rename
                        if os.path.exists(filename):
                            filename = tk.filedialog.asksaveasfilename(parent=self.root,title="File exists, export sample as [cancel to abort]",defaultextension='.wav',filetypes=(('Wav Files','*.wav'), ('All Files','*.*'))
                                                                      ,initialdir=directory,initialfile="{:0>3}_{}.wav".format(sample.oscNum.get(),sample.name.get()))
                            if not filename:
                                break
                        ok = False
                        while not ok:
                            try:
                                with open(filename, 'wb') as f:
                                    sample.e2s_sample.write(f)
                            except Exception as e:
                                tk.messagebox.showwarning(
                                "Export sample as",
                                "Cannot save sample as:\n{}\nError message:\n{}".format(filename, e)
                                )
                                filename = tk.filedialog.asksaveasfilename(parent=self.root,title="Export sample as [cancel to abort]",defaultextension='.wav',filetypes=(('Wav Files','*.wav'), ('All Files','*.*'))
                                                                          ,initialdir=directory,initialfile="{:0>3}_{}.wav".format(sample.oscNum.get(),sample.name.get()))
                                if not filename:
                                    break
                            ok = True
                        if not ok:
                            break
                                
            wd = WaitDialog(self.root)
            wd.run(fct)

    system = platform.system()
    def edit_selected(self):
        if not self.sliceEditDialog:
            self.sliceEditDialog = SliceEditorDialog(self)
        smpl = self.sampleList.get_selected()
        self.sliceEditDialog.sliceEditor.set_sample(smpl)
        if self.system == 'Windows':
            def _on_mousewheel(event):
                self.sliceEditDialog.sliceEditor.frame.canvas.yview_scroll(-1*(event.delta//120), "units")
            self.bind_all('<MouseWheel>', _on_mousewheel)
        elif self.system == 'Darwin':
            #def _on_mousewheel(event):
            #    self.sliceEditDialog.sliceEditor.frame.canvas.yview_scroll(-1*(event.delta), "units")
            #self.bind_all('<MouseWheel>', _on_mousewheel)
            pass
        else:
            def _on_up(event):
                self.sliceEditDialog.sliceEditor.frame.canvas.yview_scroll(-1*(event.delta//120), "units")
            def _on_down(event):
                self.sliceEditDialog.sliceEditor.frame.canvas.yview_scroll(event.delta//120, "units")
            self.bind_all('<Button-4>', _on_up)
            self.bind_all('<Button-5>', _on_down, add="+")
        self.sliceEditDialog.run()

    def restore_binding(self):
        if self.system == 'Windows':
            def _on_mousewheel(event):
                self.frame.canvas.yview_scroll(-1*(event.delta//120), "units")
            self.bind_all('<MouseWheel>', _on_mousewheel)
        elif self.system == 'Darwin':
            #def _on_mousewheel(event):
            #    self.frame.canvas.yview_scroll(-1*(event.delta), "units")
            #self.bind_all('<MouseWheel>', _on_mousewheel)
            pass
        else:
            def _on_up(event):
                self.frame.canvas.yview_scroll(-1*(event.delta//120), "units")
            def _on_down(event):
                self.frame.canvas.yview_scroll(event.delta//120, "units")
            self.bind_all('<Button-4>', _on_up)
            self.bind_all('<Button-5>', _on_down, add="+")


if __name__ == '__main__':
    # redirect outputs to a logger
    with logger() as log:
        # Create a window
        app = SampleAllEditor()
        app.mainloop()
        audio.terminate()
