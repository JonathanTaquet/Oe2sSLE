# -*- coding: utf-8 -*-
"""
Copyright (C) 2015 Jonathan Taquet

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

import struct
import warnings

import RIFF

class RIFF_cue(RIFF.ChunkData):
    _dataMinFmt = '<I'
    _dataMinSize = struct.calcsize(_dataMinFmt)
    
    class CuePoint:
        _dataFmt = '<2I4s3I'
        _dataSize = struct.calcsize(_dataFmt)
        
        def __init__(self, cue_master, cue_point_num):
            self.fields=dict()
            self.cue = cue_master
            offset=cue_master._dataMinSize+cue_point_num*self._dataSize
            self.fields['identifier']=(offset, '<I')
            offset+=struct.calcsize('I')
            self.fields['position']=(offset, '<I')
            offset+=struct.calcsize('I')
            self.fields['fccChunk']=(offset, '<4s')
            offset+=struct.calcsize('4s')
            self.fields['chunkStart']=(offset, '<I')
            offset+=struct.calcsize('I')
            self.fields['blockStart']=(offset, '<I')
            offset+=struct.calcsize('I')
            self.fields['sampleOffset']=(offset, '<I')
            offset+=struct.calcsize('I')
            
    
        def __getattr__(self, name):
            try:
                loc, fmt = self.fields[name]
            except:
                raise AttributeError
            else:
                size = struct.calcsize(fmt)
                unpacked = struct.unpack(fmt, self.cue.rawdata[loc:loc+size])
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
                self.__dict__['cue'].rawdata[loc:loc+size] = struct.pack(fmt, value)


    def __init__(self, file=None, chunkHeader=None):
        self.fields = dict()
        self.rawdata = bytearray(RIFF_cue._dataMinSize)
        offset = 0
        self.fields['numCuePoints']=(offset, '<I')
        offset += struct.calcsize('I')

        self.cuePoints = []
        
        if file:
            self.read(file,chunkHeader)
        else:
            self.reset()
        
#    def __len__(self):
#        return len(self.rawdata)
    
    def read(self, file, chunkHeader):
        if chunkHeader.id != b'cue ':
            raise TypeError("'cue ' chunk expected")
        self.rawdata[:] = file.read(chunkHeader.size)
        if len(self.rawdata) != chunkHeader.size:
            raise EOFError('Unexpected End Of File')
        for cuePointNum in range(self.numCuePoints):
            self.cuePoints.append(self.CuePoint(self,cuePointNum))
        
    def reset(self):
        self.numCuePoints = 0
        self.cuePoints = []

#    def write(self, file):
#        file.write(self.rawdata)

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


    #TODO: easily add CuePoint(s)