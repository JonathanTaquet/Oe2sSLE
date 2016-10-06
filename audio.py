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

import wav_tools
import RIFF

import pyaudio as pa
import warnings


audio = pa.PyAudio()

class Player:
    def __init__(self):
        self.stream = None

    def __del__(self):
        self.pause()

    def pause(self):
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
            self.stream = None
        return self

    def play(self):
        if self.stream and self.stream.is_stopped():
            self.stream.start_stream()
        return self

class Sound(Player):
    def __init__(self, data, fmt):

        if fmt.formatTag != RIFF.WAVE_fmt_.WAVE_FORMAT_PCM:
            raise Exception()

        if fmt.samplesPerSec < 1000 or fmt.samplesPerSec > 192000:
            data, fmt = wav_tools.wav_resample_preview(data, fmt, 1000, 192000)
        self.data = data
        self.fmt = fmt
        self._offset = 0

        def callback(indata, frames, time, status):
            n_bytes=frames*fmt.blockAlign
            to_read=min(n_bytes, len(self.data) - self._offset)
            outdata = self.data[self._offset:self._offset+to_read]
            self._offset += to_read
            return (outdata,pa.paContinue)

        self.stream = audio.open(format=pa.paInt16, channels=fmt.channels, rate=fmt.samplesPerSec, output=True, stream_callback=callback)

class LoopWaveSource(Player):
    def __init__(self, data, fmt, esli):
        
        if fmt.formatTag != RIFF.WAVE_fmt_.WAVE_FORMAT_PCM:
            raise Exception()

        if fmt.samplesPerSec < 1000 or fmt.samplesPerSec > 192000:
            data, fmt = wav_tools.wav_resample_preview(data, fmt, 1000, 192000)
        self.data = data
        self.fmt = fmt
        self.esli = esli
        
        self._total_offset = 0
        self._offset = esli.OSC_StartPoint_address
        self._duration = 0

        """
        TODO: use esli.playVolume and esli.playLogScale
        """
        def callback(indata, frames, time, status):
            n_bytes=frames*fmt.blockAlign
            n_read=0
            data=bytearray(n_bytes)
            end=self.esli.OSC_StartPoint_address + self.esli.OSC_EndPoint_offset#+self.fmt.blockAlign
            while n_read < n_bytes:
                to_read =min(n_bytes-n_read, end - self._offset)
                data[n_read:n_read+to_read] = self.data[self._offset:self._offset+to_read]
                n_read += to_read
                self._offset += to_read
                if self._offset == end:
                    if self.esli.OSC_LoopStartPoint_offset < self.esli.OSC_EndPoint_offset:
                        self._offset = self.esli.OSC_StartPoint_address + self.esli.OSC_LoopStartPoint_offset
                    else:
                        break

            if not n_read:
                return (bytes(data),pa.paComplete)
         
            self._total_offset += n_read
            return (bytes(data),pa.paContinue)

        self.stream = audio.open(format=pa.paInt16, channels=fmt.channels, rate=fmt.samplesPerSec, output=True, stream_callback=callback)

class ApplicationPlayer:
    def __init__(self):
        self.player=None

    def play_start(self, sound):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            if self.player is not None:
                self.player.pause()
            self.player = sound.play()

    def play_stop(self):
        if self.player is not None:
            self.player.pause()
            self.player = None
        
def terminate():
    audio.terminate()

player=ApplicationPlayer()
