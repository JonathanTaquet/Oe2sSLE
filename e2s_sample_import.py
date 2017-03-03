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

import math
import os

import RIFF
import e2s_sample_all as e2s
import wav_tools


class ImportOptions:
    """e2sSample import options"""

    # Sample import number to put in esli.OSC_importNum are starting at ~550
    # for user samples. The esli.OSC_importNum value will be overwritten
    # with e2s_sample_all.factory_importNums when e2sSample.all is saved
    # if the esli.OSC_0index corresponds to a factory sample number.
    import_num = 550

    def __init__(self):
        # default values
        self.osc_cat = 'User'
        self.loop_type = 0
        self.plus_12_db = 0
        # force to use the default values if already defined?
        self.force_osc_cat = 0
        self.force_loop_type = 0
        self.force_plus_12_db = 0
        # A free sample number will be searched from smp_num_from value
        # when a new sample will be imported
        self.smp_num_from = 19


class FromWavError(Exception):
    """Base class for from_wav exceptions."""
    pass


class NotWaveFormatPcm(FromWavError):
    """WAV format must be WAVE_FORMAT_PCM."""
    pass


class EmptyWav(FromWavError):
    """No data: empty WAV samples are not allowed by e2sSample format."""
    pass


class NotSupportedBitPerSample(FromWavError):
    """WAV bit per sample value is not supported"""
    pass


def from_wav(filename, import_opts=ImportOptions()):
    converted_from = None
    with open(filename, 'rb') as f:
        sample = e2s.e2s_sample(f)
    # check format
    fmt = sample.get_fmt()
    if fmt.formatTag != fmt.WAVE_FORMAT_PCM:
        raise NotWaveFormatPcm
    # electribe and Oe2sSLE do not allow empty samples
    if not len(sample.get_data()):
        raise EmptyWav
    if fmt.bitPerSample != 16:
        if fmt.bitPerSample == 8:
            wav_tools.wav_pcm_8b_to_16b(sample)
            converted_from = 8
        elif fmt.bitPerSample == 24:
            wav_tools.wav_pcm_24b_to_16b(sample)
            converted_from = 24
        else:
            raise NotSupportedBitPerSample
        fmt = sample.get_fmt()

    if not sample.RIFF.chunkList.get_chunk(b'korg'):
        korg_data = e2s.RIFF_korg()
        korg_chunk = RIFF.Chunk(header=RIFF.ChunkHeader(id=b'korg'), data=korg_data)
        sample.RIFF.chunkList.chunks.append(korg_chunk)
        sample.header.size += len(korg_chunk)

    korg_chunk = sample.RIFF.chunkList.get_chunk(b'korg')

    esli_chunk = korg_chunk.data.chunkList.get_chunk(b'esli')
    if not esli_chunk:
        esli = e2s.RIFF_korg_esli()
        esli_chunk = RIFF.Chunk(header=RIFF.ChunkHeader(id=b'esli'), data=esli)
        korg_chunk.data.chunkList.chunks.append(esli_chunk)
        esli.OSC_name = bytes(os.path.splitext(os.path.basename(filename))[0], 'ascii', 'ignore')
        # todo funtion for that:
        data = sample.get_data()
        esli.samplingFreq = fmt.samplesPerSec
        esli.OSC_EndPoint_offset = esli.OSC_LoopStartPoint_offset = len(data) - fmt.blockAlign
        esli.WAV_dataSize = len(data)
        if fmt.blockAlign == 4:
            # stereo
            esli.useChan1 = True
        # by default use maximum volume
        # unlike electribe which normalizes volume
        esli.playVolume = 65535

        # use options defaults
        esli.OSC_category = esli.OSC_category = e2s.esli_str_to_OSC_cat[import_opts.osc_cat]
        esli.playLevel12dB = import_opts.plus_12_db

        esli.OSC_importNum = ImportOptions.import_num
        ImportOptions.import_num += 1
        # by default play speed is same as indicated by Frequency
        esli.playLogPeriod = 65535 if fmt.samplesPerSec == 0 else max(0, int(round(63132-math.log2(fmt.samplesPerSec)*3072)))
        esli_chunk.header.size += len(esli_chunk)
        sample.header.size += len(esli_chunk)

        # check if smpl chunk is used
        smpl_chunk = sample.RIFF.chunkList.get_chunk(b'smpl')
        smpl_used = False
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
                        smpl_used = True
        if not smpl_used and import_opts.loop_type == 1:
            # loop all
            esli.OSC_LoopStartPoint_offset = 0
            esli.OSC_OneShot = 0
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

    apply_forced_options(sample, import_opts)
    return sample, converted_from


def apply_forced_options(e2s_sample, import_opts):
    esli = e2s_sample.get_esli()

    if import_opts.force_osc_cat:
        esli.OSC_category = e2s.esli_str_to_OSC_cat[import_opts.osc_cat]

    if import_opts.force_loop_type:
        if import_opts.loop_type == 0:
            # force one shot
            esli.OSC_LoopStartPoint_offset = esli.OSC_EndPoint_offset
            esli.OSC_OneShot = 1
        elif import_opts.loop_type == 1:
            # force loop all
            esli.OSC_LoopStartPoint_offset = 0
            esli.OSC_OneShot = 0

    if import_opts.force_plus_12_db:
        esli.playLevel12dB = import_opts.plus_12_db
