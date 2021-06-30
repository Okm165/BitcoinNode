import tqdm
from typing import OrderedDict


class DictSerialize:
    def __init__(self) -> None:
        self.data = None
        self.cursor = None

    def read(self, length):
        result = self.data[self.cursor : self.cursor + length]
        self.cursor += length
        return result
    
    def readVarInt(self) -> int:
        temp = 0
        a = 0
        while True:
            i = self.data[self.cursor]
            self.cursor += 1
            temp = temp | (i & 0x7F) << a
            if(i & 0x80):
                a += 7
                continue
            else:
                return temp
    
    def writeVarInt(self, n:int) -> bytearray:
        u = (n.bit_length() + 7)//8
        tmp = bytearray(u + (u+6)//7 + 1)
        a = 0
        while True:
            if n > 0x7F:
                dat = 0x80
            else:
                dat = 0x00

            tmp[a] = (n & 0x7F) | dat
            if n <= 0x7F:
                break
            n = (n >> 7)
            a += 1

        # clean excesive zeros
        while True:
            if tmp[len(tmp)-1] == 0x00 and len(tmp) > 1:
                tmp = tmp[0:len(tmp)-1]
            else:
                break
        return tmp
    
    def UIntCode(self, n:int) -> int:
        bl = (n.bit_length()+7)//8
        while True:
            mid_val = (2**(bl*8)-1)//2
            m = int(n + mid_val)
            if m < 0:
                bl += 1
                continue
            if (m.bit_length()+7)//8 == bl:
                b = m
                break
            else:
                bl += 1
        return b
    
    def UIntDecode(self, n:int) -> int:
        bit_len = (n.bit_length()+7)//8
        dec = n - (2**(bit_len*8)-1)//2
        return dec
    
    def serializeDict(self, dict, progress=False) -> bytearray:
        data = bytearray()
        length = self.writeVarInt(len(dict))
        data.extend(length)
        if progress:
            print("Serializing dict...")
            bar = tqdm.tqdm(
                total=len(dict),
                colour="#bbc4c5",
                smoothing=0.01)
        for key, value in dict.items():
            len_key = self.writeVarInt(len(key))
            data.extend(len_key)
            data.extend(key)
            data.extend(self.writeVarInt(self.UIntCode(value)))
            if progress: bar.update(1)
        if progress:
            bar.refresh()
            bar.close()
        self.clear()
        return data

    def deserializeDict(self, data:bytearray, progress=False) -> dict:
        self.data = data
        self.cursor = 0
        dictionary = dict()
        length = self.readVarInt()
        if progress:
            print("Deserializing dict...")
            bar = tqdm.tqdm(
                total=length,
                colour="#bbc4c5",
                smoothing=0.01)
        for _ in range(length):
            len_key = self.readVarInt()
            key = self.read(len_key)
            value = self.UIntDecode(self.readVarInt())
            dictionary[key] = value
            if progress: bar.update(1)
        if progress:
            bar.refresh()
            bar.close()
        self.clear()
        return dictionary

    def deserializeDictToList(self, data:bytearray, progress=False) -> list:
        self.data = data
        self.cursor = 0
        list = []
        length = self.readVarInt()
        if progress:
            print("Deserializing dict...")
            bar = tqdm.tqdm(
                total=length,
                colour="#bbc4c5",
                smoothing=0.01)
        for _ in range(length):
            len_key = self.readVarInt()
            key = self.read(len_key)
            value = self.UIntDecode(self.readVarInt())
            list.append((key,value))
            if progress: bar.update(1)
        if progress:
            bar.refresh()
            bar.close()
        self.clear()
        return list



    def clear(self):
        self.data = None
        self.cursor = None