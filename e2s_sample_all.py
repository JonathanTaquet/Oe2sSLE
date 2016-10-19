# -*- coding: utf-8 -*-
"""
Copyright (C) 2015 Jonathan Taquet

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

import struct
import RIFF
import warnings
import traceback

from RIFF.smpl import RIFF_smpl
from RIFF.cue  import RIFF_cue

class OSC:
    ANALOG   = 0
    AUDIO_IN = 1
    KICK     = 2
    SNARE    = 3
    CLAP     = 4
    HIHAT    = 5
    CYMBAL   = 6
    HITS     = 7
    SHOTS    = 8
    VOICE    = 9
    SE       = 10
    FX       = 11
    TOM      = 12
    PERC     = 13
    PHRASE   = 14
    LOOP     = 15
    PCM      = 16
    USER     = 17

esli_OSC_cat_to_str = {
    0   : 'Analog',
    1   : 'Audio In',
    2   : 'Kick',
    3   : 'Snare',
    4   : 'Clap',
    5   : 'HiHat',
    6   : 'Cymbal',
    7   : 'Hits',
    8   : 'Shots',
    9   : 'Voice',
    10  : 'SE',
    11  : 'FX',
    12  : 'Tom',
    13  : 'Perc.',
    14  : 'Phrase',
    15  : 'Loop',
    16  : 'PCM',
    17  : 'User'
}

esli_str_to_OSC_cat = {
    'Analog'   :  0,
    'Audio In' :  1,
    'Kick'     :  2,
    'Snare'    :  3,
    'Clap'     :  4,
    'HiHat'    :  5,
    'Cymbal'   :  6,
    'Hits'     :  7,
    'Shots'    :  8,
    'Voice'    :  9,
    'SE'       : 10,
    'FX'       : 11,
    'Tom'      : 12,
    'Perc.'    : 13,
    'Phrase'   : 14,
    'Loop'     : 15,
    'PCM'      : 16,
    'User'     : 17
}

esli_beat = {
    '16'     : 0,
    '32'     : 1,
    '8 Tri'  : 2,
    '16 Tri' : 3
}

esli_beat_to_str = {
    0 : '16',
    1 : '32',
    2 : '8 Tri',
    3 : '16 Tri'
}

WAVDataMaxSize = 26214396

class RIFF_korg_esli(RIFF.ChunkData):
    _dataSize = 1172
    _chunkHeader = RIFF.ChunkHeader(id=b'esli', size=_dataSize)

    class SliceData:
        def __init__(self, esli_master, slice_num):
            self.__dict__['fields']=dict()
            self.__dict__['esli']=esli_master
            offset=self.esli.fields['slicesData'][0]+slice_num*struct.calcsize('4I')
            self.fields['start']=(offset, '<I')
            offset+=struct.calcsize('I')
            self.fields['length']=(offset, '<I')
            offset+=struct.calcsize('I')
            self.fields['attack_length']=(offset, '<I')
            offset+=struct.calcsize('I')
            self.fields['amplitude']=(offset, '<I')
            offset+=struct.calcsize('I')
            
    
        def __getattr__(self, name):
            try:
                loc, fmt = self.fields[name]
            except:
                raise AttributeError
            else:
                size = struct.calcsize(fmt)
                unpacked = struct.unpack(fmt, self.esli.rawdata[loc:loc+size])
                if len(unpacked) == 1:
                    return unpacked[0]
                else:
                    return unpacked

        def __setattr__(self, name, value):
            try:
                loc, fmt = self.fields[name]
            except:
                self.__dict__[name] = value
            else:
                size = struct.calcsize(fmt)
                self.__dict__['esli'].rawdata[loc:loc+size] = struct.pack(fmt, value)

    class SliceSteps:
        def __init__(self, esli_master):
            self.esli = esli_master
            self.baseOffset=self.esli.fields['slicesActiveSteps'][0]
        
        def __getitem__(self, index):
            assert index >= 0 and index < 64
            return struct.unpack('b', self.esli.rawdata[self.baseOffset+index:self.baseOffset+index+1])[0]
        
        def __setitem__(self, index, value):
            assert index >= 0 and index < 64
            self.esli.rawdata[self.baseOffset+index:self.baseOffset+index+1] =  struct.pack('b', value)
            
    
    def __init__(self, file=None, chunkHeader=None):
        self.__dict__['fields'] = dict()
        self.__dict__['rawdata'] = bytearray(RIFF_korg_esli._dataSize)
        offset = 0
        self.fields['OSC_0index']=(offset, '<H')
        offset += struct.calcsize('H')
        self.fields['OSC_name']=(offset, '16s')
        offset += struct.calcsize('16s')
        self.fields['OSC_category']=(offset, '<H')
        offset += struct.calcsize('H')
        self.fields['OSC_importNum']=(offset, '<H')
        offset += struct.calcsize('H')
        self.fields['_16_22_UFix']=(offset, '12s')
        offset += struct.calcsize('12s')
        self.fields['playLogPeriod']=(offset, '<H')
        offset += struct.calcsize('<H')
        self.fields['playVolume']=(offset, '<H')
        offset += struct.calcsize('<H')
        self.fields['_26_UVar']=(offset, '1s')
        offset += struct.calcsize('1s')
        self.fields['_27_UFix']=(offset, '1s')
        offset += struct.calcsize('1s')
        self.fields['OSC_StartPoint_address']=(offset, '<I')
        offset += struct.calcsize('I')
        self.fields['OSC_LoopStartPoint_offset']=(offset, '<I')
        offset += struct.calcsize('I')
        self.fields['OSC_EndPoint_offset']=(offset, '<I')
        offset += struct.calcsize('I')
        self.fields['OSC_OneShot']=(offset, '?')
        offset += struct.calcsize('?')
        self.fields['_35_3C_UFix']=(offset, '7s')
        offset += struct.calcsize('7s')
        self.fields['WAV_dataSize']=(offset, '<I')
        offset += struct.calcsize('I')
        self.fields['useChan0_UFix']=(offset, 'B')
        offset += struct.calcsize('B')
        self.fields['useChan1']=(offset, '?')
        offset += struct.calcsize('?')
        self.fields['playLevel12dB']=(offset, '?')
        offset += struct.calcsize('?')
        self.fields['_43_48_UFix']=(offset, '5s')
        offset += struct.calcsize('5s')
        self.fields['samplingFreq']=(offset, '<I')
        offset += struct.calcsize('I')
        self.fields['_4C_UFix']=(offset, '1s')
        offset += struct.calcsize('1s')
        self.fields['sampleTune']=(offset, '<b')
        offset += struct.calcsize('b')
        self.fields['OSC_0index1']=(offset, '<H')
        offset += struct.calcsize('H')
        self.fields['slicesData']=(offset, '<256I')
        offset += struct.calcsize('256I')
        self.fields['slicesActiveSteps']=(offset, '64s')
        offset += struct.calcsize('64s')
        self.fields['slicingNumSteps']=(offset, 'B')
        offset += struct.calcsize('B')
        self.fields['slicingBeat']=(offset, 'B')
        offset += struct.calcsize('B')
        self.fields['slicesNumActiveSteps']=(offset, 'B')
        offset += struct.calcsize('B')
        self.fields['_493_UVar']=(offset, '1s')
        offset += struct.calcsize('1s')

        self.__dict__['slices'] = []
        for i in range(64):
            self.slices.append(self.SliceData(self,i))
        
        self.sliceSteps = self.SliceSteps(self)

        if file:
            self.read(file,chunkHeader)
        else:
            self.reset()
        
    def __len__(self):
        return RIFF_korg_esli._dataSize
    
    def __getattr__(self, name):
        try:
            loc, fmt = self.fields[name]
        except:
            raise AttributeError
        else:
            size = struct.calcsize(fmt)
            unpacked = struct.unpack(fmt, self.rawdata[loc:loc+size])
            if len(unpacked) == 1:
                return unpacked[0]
            else:
                return unpacked

    def __setattr__(self, name, value):
        try:
            loc, fmt = self.fields[name]
        except:
            self.__dict__[name] = value
        else:
            size = struct.calcsize(fmt)
            self.__dict__['rawdata'][loc:loc+size] = struct.pack(fmt, value)

    def read(self, file, chunkHeader):
        if chunkHeader.id != b'esli':
            raise TypeError("'elsi' chunk expected")
        if chunkHeader.size < RIFF_korg_esli._dataSize:
            raise ValueError('Unknown esli chunck size')
        if chunkHeader.size > RIFF_korg_esli._dataSize:
            print ('Unusual esli chunck size')
        self.rawdata[:] = file.read(chunkHeader.size)
        if len(self.rawdata) != chunkHeader.size:
            raise EOFError('Unexpected End Of File')

        if self._16_22_UFix != b'\x00\x00\x00\x7F\x00\x01\x00\x00\x00\x00\x00\x00':
            print('Unusual values in _16_22_UFix: ', self._16_22_UFix)
        if self._27_UFix != b'\x00':
            print('Unusual values in _27_UFix: ', self._27_UFix)
        if self._35_3C_UFix != b'\x00\x00\x00\x00\x00\x00\x00':
            print('Unusual values in _35_3C_UFix: ', self._35_3C_UFix)
        if self._43_48_UFix != b'\x01\xB0\x04\x00\x00':
            print('Unusual values in _43_48_UFix: ', self._43_48_UFix)
        if self._4C_UFix != b'\x00':
            print('Unusual values in _4C_UFix: ', self._4C_UFix)
        if self.useChan0_UFix != 1:
            print('Unusual value in useChan0_UFix: ', self.useChan0_UFix)

    def reset(self):
        self._16_22_UFix = b'\x00\x00\x00\x7F\x00\x01\x00\x00\x00\x00\x00\x00'
        self._27_UFix = b'\x00'
        self._35_3C_UFix = b'\x00\x00\x00\x00\x00\x00\x00'
        self._43_48_UFix = b'\x01\xB0\x04\x00\x00'
        self._4C_UFix = b'\x00'
        self.useChan0_UFix = 1
        
        self.OSC_category = OSC.USER
        self.OSC_OneShot = True
        

    def get_chunk_header(self):
        return RIFF_korg_esli._chunkHeader
        
    def write(self, file):
        file.write(self.rawdata)

    def set_OSCNum(self, num):
        self.OSC_0index = self.OSC_0index1 = num-1

    def get_OSCNum(self):
        return self.OSC_0index+1

class RIFF_korg(RIFF.ChunkData):
    registeredChunks = {
        b'esli' : RIFF_korg_esli
    }

    def __init__(self, file=None, chunkHeader=None):
        self.chunkList = RIFF.ChunkList(RIFF_korg.registeredChunks)
        if file:
            self.read(file,chunkHeader)
        
    def __len__(self):
        return len(self.chunkList)
    
    def read(self, file, chunkHeader):
        if chunkHeader.id != b'korg':
            raise TypeError("'korg' chunk expected")
        self.chunkList.read(file, chunkHeader.size)
        
    def write(self, file):
        self.chunkList.write(file)

class RIFF_korgWAVEChunkList(RIFF.WAVEChunkList):

    registeredChunks = {
        b'korg' : RIFF_korg,
        b'smpl' : RIFF_smpl,
        b'cue ' : RIFF_cue,
    }
    
    def __init__(self, registeredChunks=dict()):
        rc = dict(RIFF_korgWAVEChunkList.registeredChunks)
        for key, val in registeredChunks.items():
            rc[key]=val
        super(RIFF_korgWAVEChunkList, self).__init__(rc)

#TODO: should  be changed as a RIFF.Chunk
# => 'RIFF' chunk must be handled in RIFF module
class e2s_sample:
    def __init__(self, file=None, **kw):
        if file:
            self.read(file)
        else:
            self.RIFF = RIFF.Form(type=b'WAVE', chunkList=RIFF_korgWAVEChunkList())

    def __len__(self):
        return len(self.header)+len(self.RIFF)
    
    def read(self, file):
        self.header = RIFF.ChunkHeader(file)
        # now, parse
        if self.header.id != b"RIFF":
            raise ValueError(
                "Expected {} chunk, got {}; ignored.".format(b"RIFF", self.header.id))
        self.RIFF = RIFF.Form(file,self.header,registeredForms={b'WAVE':RIFF_korgWAVEChunkList})
    
    def write(self, file):
        self.update_header()
        self.header.write(file)
        self.RIFF.write(file)
        
    def get_esli(self):
        try:
            return self._esli
        except:
            self._esli = self.RIFF.chunkList.get_chunk(b'korg').data.chunkList.get_chunk(b'esli').data
        return self._esli

    def get_data(self):
        return self.RIFF.chunkList.get_chunk(b'data').data
    
    def get_fmt(self):
        return self.RIFF.chunkList.get_chunk(b'fmt ').data

    def get_chunk(self, id):
        return self.RIFF.chunkList.get_chunk(id)


    def update_header(self):
        self.header.size = len(self.RIFF)


    def get_clean_copy(self):
        copy = e2s_sample()
        copy.header = RIFF.ChunkHeader(id=self.header.id)
        copy.RIFF.chunkList.chunks.append(self.RIFF.chunkList.get_chunk(b'fmt '))
        copy.RIFF.chunkList.chunks.append(self.RIFF.chunkList.get_chunk(b'data'))
        copy.RIFF.chunkList.chunks.append(self.RIFF.chunkList.get_chunk(b'korg'))
        copy.header.size = len(copy.RIFF)
        return copy
        
# TODO: check if e2s supports RIFX files (big endian)

class e2s_sample_all:
    def __init__(self, **kw):
        self.samples = []
        if 'filename' in kw:
            self.load(kw['filename'])
    
    def load(self, filename):
        self._loadErrors = 0
        with open(filename,'rb') as f:
            # header
            if f.read(16) != b"e2s sample all\x1A\x00":
                raise ValueError("unhandled file format")
            # RIFF addresses up to 0x1000 in the file
            riffAddrs = struct.unpack("<"+"I"*1020,f.read(4080))
            for riffAddr in riffAddrs:
                # skip null pointers
                # TODO: check if addr can be Odd (for electribe)
                if riffAddr:
                    try:
                        f.seek(riffAddr)
                        sample = e2s_sample(f)
                        self.samples.append(sample)
                    except:
                        self._loadErrors += 1
                        warnings.warn('Recovering from an error while reading a sample')
                        traceback.print_exc()

    def save(self, filename):
        # RIFF addresses up to 0x1000 in the file
        # do like e2s:
        #
        riffAddrs=[(0,None)]*1020
        riffNextAddr=0x1000
        for sample in self.samples:
            addr=sample.RIFF.chunkList.get_chunk(b'korg').data.chunkList.get_chunk(b'esli').data.OSC_0index
            if riffAddrs[addr][1] is not None:
                warnings.warn('Multiple samples with same OSC number, duplicates lost')
            riffAddrs[addr] = (riffNextAddr,sample)
            riffNextAddr+=len(sample)

        with open(filename,'wb') as f:
            # header
            f.write(b"e2s sample all\x1A\x00")
            for riffAddr in riffAddrs:
                f.write(struct.pack("<I", riffAddr[0]))
            for riffAddr in riffAddrs:
                if riffAddr[0]:
                    diff = riffAddr[0]-f.tell()
                    if diff:
                        warnings.warn('empty feeling')
                        f.write(b'\x00'*diff)
                    riffAddr[1].write(f)
