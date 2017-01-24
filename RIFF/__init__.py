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
import warnings

warnings.simplefilter("always")

class ChunkHeader:
    head_fmt = '<4sI'
    head_len = struct.calcsize(head_fmt)

    def __init__(self, file=None, **kw):
        if file:
            self.read(file)
        else:
            self.id = bytes(kw['id'])
            self.size = kw.get('size', 0)
            
    def read(self, file):
        self.id, self.size = struct.unpack(
                                ChunkHeader.head_fmt,
                                file.read(ChunkHeader.head_len))
        
    def write(self, file):
        file.write(struct.pack(ChunkHeader.head_fmt, self.id, self.size))
        
    def __len__(self):
        return ChunkHeader.head_len


class ChunkData:
    def __init__(self, file=None, chunkHeader=None, **kw):
        if file:
            self.read(file, chunkHeader)
        else:
            self.rawdata=kw.get('rawdata')
    
    def __len__(self):
        return len(self.rawdata)

    def read(self, file, chunkHeader):
        self.rawdata=file.read(chunkHeader.size)
        
    def write(self, file):
        file.write(self.rawdata)
        
# modify size of chunk if EOF reached
class Chunk:
    class HeaderSizeError(Exception):
        pass

    class DataSizeError(Exception):
        pass
    
    def __init__(self, file=None, **kw):
        self.registeredChunks = dict(kw.get('registeredChunks', {}))
        if file:
            self.read(file, maxSize=kw.get('maxSize'))
        else:
            self.header = kw.get('header')
            self.data = kw.get('data')
    
    def __len__(self):
        return len(self.header) + len(self.data) + (len(self.data)&1)

    def read(self, file, **kw):
        maxSize = kw.get('maxSize')
        if maxSize is not None:
            if maxSize < ChunkHeader.head_len:
                file.read(maxSize)
                raise Chunk.HeaderSizeError("not enough data to read chunk header")
            maxSize -= ChunkHeader.head_len

        self.header = ChunkHeader(file)
        
        if maxSize is not None and maxSize < self.header.size:
            file.read(maxSize)
            raise Chunk.DataSizeError("not enough data to read chunk body")

        data_class = self.registeredChunks.get(self.header.id,ChunkData)
        self.data = data_class(file,self.header)

        if maxSize is not None:
            maxSize -= self.header.size;
        # align to word size
        if len(self.data)&1 and (maxSize is None or maxSize):
            file.read(1)

    def update_header(self):
        self.header.size = len(self.data)

    def write(self, file):
        self.update_header()
        self.header.write(file)
        self.data.write(file)
        # align to word size
        if len(self.data)&1:
            file.write(b'\x00')
            

"""
  otherFieldsRAW is used to store RAW values of unknown fields
"""
class WAVE_fmt_(ChunkData):
    WAVE_FORMAT_UNKNOWN        = 0x0000 # Microsoft: Unknown format
    WAVE_FORMAT_PCM            = 0x0001 # Microsoft: Pulse Code Modulation (PCM) format
    WAVE_FORMAT_ADPCM          = 0x0002 # Microsoft: Adaptive Delta Pulse Code Modulation (ADPCM) format
    WAVE_FORMAT_IEEE_FLOAT     = 0x0003 # Microsoft: IEEE754: range (+1, -1] 32-bit/64-bit format as defined by MSVC++ float/double type IEEE float
    WAVE_FORMAT_ALAW           = 0x0006 # Microsoft: 8-bit ITU-T G.711 A-law
    WAVE_FORMAT_MULAW          = 0x0007 # Microsoft: 8-bit ITU-T G.711 µ-law
    IBM_FORMAT_MULAW           = 0x0101 # IBM: µ-law format
    IBM_FORMAT_ALAW            = 0x0102 # IBM: a-law format
    IBM_FORMAT_ADPCM           = 0x0103 # IBM AVC Adaptive Differential Pulse Code Modulation format
    WAVE_FORMAT_EXTENSIBLE     = 0xFFFE # Microsoft: Extensible Wave format
    WAVE_FORMAT_DEVELOPMENT    = 0xFFFF # Microsoft: Development format
    
    common_fields_fmt = '<HHIIH'
    specific_fields = {
        WAVE_FORMAT_PCM  : ('<H', ['bitPerSample'])
    }
    
    def __init__(self, file=None, chunkHeader=None, **kw):
        if file:
            self.read(file, chunkHeader)
        else:
            # common fields
            self.formatTag = kw.get('formatTag')
            self.channels = kw.get('channels')
            self.samplesPerSec = kw.get('samplesPerSec')
            self.avgBytesPerSec = kw.get('avgBytesPerSec')
            self.blockAlign = kw.get('blockAlign')
            # format specific fields
            if self.formatTag in WAVE_fmt_.specific_fields:
                for field in WAVE_fmt_.specific_fields[self.formatTag][1]:
                    self.__setattr__(field,kw.get(field))
            self.otherFieldsRAW = kw.get('otherFieldsRAW')

    def __len__(self):
        return (
            struct.calcsize(WAVE_fmt_.common_fields_fmt)
            + struct.calcsize(WAVE_fmt_.specific_fields.get(self.formatTag, ("",))[0])
            + (len(self.otherFieldsRAW) if self.otherFieldsRAW is not None else 0)
        )
        
    def read(self, file, chunkHeader):
        if chunkHeader.id != b'fmt ':
            raise TypeError("'fmt ' chunk expected")
        fmt=WAVE_fmt_.common_fields_fmt
        size=struct.calcsize(fmt)
        if chunkHeader.size < size:
            raise ValueError("'fmt ' chunk size is not enough")
        (self.formatTag,
         self.channels,
         self.samplesPerSec,
         self.avgBytesPerSec,
         self.blockAlign) = struct.unpack(fmt, file.read(size))

        size_read=size
        
        if self.formatTag in WAVE_fmt_.specific_fields:
            fmt, fields = WAVE_fmt_.specific_fields[self.formatTag]
            size = struct.calcsize(fmt)
            if chunkHeader.size < size_read + size:
                raise ValueError("'fmt ' chunk size is not enough")
            f_values = struct.unpack(fmt, file.read(size))
            size_read += size
            for i in range(len(fields)):
                setattr(self,fields[i],f_values[i])
        
        if size_read < chunkHeader.size:
            self.otherFieldsRAW = file.read(chunkHeader.size - size_read)
        else:
            self.otherFieldsRAW = None
        
    def write(self, file):
        file.write(
            struct.pack(
                WAVE_fmt_.common_fields_fmt,
                self.formatTag,
                self.channels,
                self.samplesPerSec,
                self.avgBytesPerSec,
                self.blockAlign
                ))
        
        if self.formatTag in WAVE_fmt_.specific_fields:
            fmt, fields = WAVE_fmt_.specific_fields[self.formatTag]
            file.write(
                struct.pack(
                    fmt,
                    *[getattr(self,field) for field in fields]
                    ))      

        if self.otherFieldsRAW:
            file.write(self.otherFieldsRAW)


class WAVE_data(ChunkData):
    def __init__(self, *a, **kw):
       super(WAVE_data, self).__init__(*a,**kw)
    # TODO: handle LIST wavl ?

class ChunkList:
    class InvalidError(Exception):
        pass

    def __init__(self, registeredChunks):
        self.chunks=[]
        self.registeredChunks = dict(registeredChunks)

    def __len__(self):
        size = 0
        for chunk in  self.chunks:
            size += len(chunk)
        return size

    def get_chunk(self, chunkId):
        for chunk in self.chunks:
            if chunk.header.id == chunkId:
                return chunk
        return None

    def valid(self):
        return True

    def read(self, file, maxSize=None):
        while maxSize > 0:
            try:
                chunk = Chunk(file,
                              maxSize=maxSize,
                              registeredChunks=self.registeredChunks)
                self.chunks.append(chunk)
                maxSize -= len(chunk)
                #warnings.warn("got a {} chunk of size={}, maxSize={}".format(chunk.header.id,chunk.header.size,maxSize))
            except Chunk.HeaderSizeError:
                warnings.warn("'RIFF' chunk does not finish after a chunk")
                maxSize = 0;
            except Chunk.DataSizeError:
                warnings.warn("'RIFF' chunk contains an ignored truncaded chunk")
                maxSize = 0;
        if not self.valid():
            raise ChunkList.InvalidError("'RIFF' form seems to be invalid")
    
    def write(self, file):
        if not self.valid():
            raise ChunkList.InvalidError()
        for chunk in self.chunks:
            chunk.write(file)
    
    

class WAVEChunkList(ChunkList):

    registeredChunks = {
        b'fmt ' : WAVE_fmt_,
        b'data' : WAVE_data
    }
    
    def __init__(self, registeredChunks):
        super(WAVEChunkList, self).__init__(WAVEChunkList.registeredChunks)
        for key, val in registeredChunks.items():
            self.registeredChunks[key] = val

    def valid(self):
        has_fmt=False
        has_data=False
        fmt_before_data=False
        for chunk in self.chunks:
            if chunk.header.id == b'fmt ':
                has_fmt=True
            elif chunk.header.id == b'data':
                has_data=True
                if has_fmt:
                    fmt_before_data=True
        return has_fmt and has_data and fmt_before_data
    
    
    

class Form(ChunkData):
    RMID_FORM_TYPE = b'RMID' # RIFF MIDI Format
    WAVE_FORM_TYPE = b'WAVE' # Waveform Audio Format
    
    registeredForms = {
        WAVE_FORM_TYPE : WAVEChunkList
    }    
    
    type_fmt = '4s'
    type_len = struct.calcsize(type_fmt)

    def __init__(self, file=None, chunkHeader=None, **kw):
        self.registeredChunks = kw.get('registeredChunks', {})
        self.registeredForms = dict(Form.registeredForms)
        for key, val in kw.get('registeredForms', {}).items():
            self.registeredForms[key] = val
        if file:
            self.read(file, chunkHeader)
        else:
            self.type = kw.get('type')
            self.chunkList = kw.get('chunkList')
        
    def __len__(self):
        size = Form.type_len
        for ck in self.chunkList.chunks:
            size += len(ck)
        return size

    def read(self, file, chunkHeader):
        if chunkHeader.id != b'RIFF':
            raise TypeError("'RIFF' chunk expected")
        size_to_read=chunkHeader.size
        if size_to_read < Form.type_len:
                raise ValueError("'RIFF' chunk size is not enough")        
        self.type=struct.unpack(Form.type_fmt,file.read(Form.type_len))[0]
        size_to_read -= Form.type_len
        
        chunkList_class = self.registeredForms[self.type]
        self.chunkList = chunkList_class(self.registeredChunks)

        self.chunkList.read(file,size_to_read)

    def write(self, file):
        file.write(struct.pack(Form.type_fmt,self.type))
        self.chunkList.write(file)