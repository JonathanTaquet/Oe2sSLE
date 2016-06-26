# -*- coding: utf-8 -*-
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

import RIFF
import e2s_sample_all

import struct

def wav_pcm_8b_to_16b(e2s_sample):
    # checks
    fmt = e2s_sample.get_fmt()
    if (   fmt.formatTag != fmt.WAVE_FORMAT_PCM
        or fmt.bitPerSample != 8):
        return None
    in_data = e2s_sample.get_data().rawdata
    n_samples = len(in_data)

    sample_values=struct.unpack(str(n_samples)+'B', in_data)
    w_sample_values=[(i - 128)*256 for i in sample_values]
    data=struct.pack('<'+str(n_samples)+'h',*w_sample_values)

    e2s_sample.get_chunk(b'data').data.rawdata = data
    e2s_sample.get_chunk(b'data').update_header()
    e2s_sample.update_header()
    fmt.bitPerSample = 16
    fmt.avgBytesPerSec *= 2
    fmt.blockAlign *= 2

    # TODO: update cue points chunkStart and blockStart if used later

    return e2s_sample

def wav_pcm_24b_to_16b(e2s_sample):
    # checks
    fmt = e2s_sample.get_fmt()
    if (   fmt.formatTag != fmt.WAVE_FORMAT_PCM
        or fmt.bitPerSample != 24):
        return None
    in_data=e2s_sample.get_data().rawdata
    n_samples = len(in_data)//3

    data=bytes([in_data[b] for i in range(n_samples) for b in (i*3+1, i*3+2)])

    e2s_sample.get_chunk(b'data').data.rawdata = data
    e2s_sample.get_chunk(b'data').update_header()
    e2s_sample.update_header()
    fmt.bitPerSample = 16
    fmt.avgBytesPerSec = fmt.avgBytesPerSec * 2 // 3
    fmt.blockAlign = fmt.blockAlign * 2 // 3

    # TODO: update cue points chunkStart and blockStart if used later

    return e2s_sample
        