"""
Copyright (C) 2018 Jonathan Taquet

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

def trim(e2s_sample, start, stop):
    fmt = e2s_sample.get_fmt()
    esli = e2s_sample.get_esli()

    data_size = len(e2s_sample.get_data().rawdata)
    smpl_size = fmt.blockAlign

    start = min(max(0, start), data_size // smpl_size - 1)
    stop =  min(max(0, stop), data_size // smpl_size - 1)
    start, stop = min(start, stop), max(start, stop)

    smpl_offset = start
    byte_offset = start * smpl_size

    # remove offset from all points
    esli.OSC_StartPoint_address = max(0, esli.OSC_StartPoint_address - byte_offset)
    for sli in esli.slices:
        sli.length = max(0, min(sli.length, sli.length+sli.start))
        sli.start = max(0, sli.start)

    smpl_len = max(0, stop - start + 1)
    byte_len = smpl_len * smpl_size

    esli.OSC_LoopStartPoint_offset = min(esli.OSC_LoopStartPoint_offset, byte_len - smpl_size)
    esli.OSC_EndPoint_offset = min(esli.OSC_EndPoint_offset, byte_len - smpl_size)
    for sli in esli.slices:
        if sli.start > smpl_len - 1:
            sli.start = 0
            sli.length = 0
        else:
            sli.length = min(sli.length, smpl_len - sli.start)
    e2s_sample.get_data().rawdata = e2s_sample.get_data().rawdata[byte_offset:byte_offset+byte_len]
    esli.WAV_dataSize = len(e2s_sample.get_data().rawdata)