# BytesReader class performs bytes reading functionality
class ByteReader:
    
    def __init__(self, bytesArray, cursor = 0):
        self.bytes = bytesArray
        self.cursor = cursor
    
    # get cursor position
    def getPos(self):
        return self.cursor
    
    # set absolute cursor position counted from begining of the bytesArray
    def setPos(self, pos : int):
        self.cursor = pos
    
    # move cursor relative to current position
    def move(self, pos : int):
        self.cursor += pos

    def getLength(self):
        return len(self.bytes)

    # read length of bytes, movement of the cursor is automated, no need to call move()
    # performs little endian conversion
    def read(self, length : int):
        result = self.bytes[self.cursor : self.cursor + length][::-1]
        self.cursor += length
        return result

    def reset(self):
        self.cursor = 0

    # read variable length integer, movement of the cursor is automated, no need to call move()
    def readCompactSize(self):
        chSize = int.from_bytes(self.read(1), "big" ,signed=False)
        nSize = 0
        if chSize < 253:
            nSize = chSize
        elif chSize == 253:
            nSize = int.from_bytes(self.read(2), "big" ,signed=False)
        elif chSize == 254:
            nSize = int.from_bytes(self.read(4), "big" ,signed=False)
        else:
            nSize = int.from_bytes(self.read(8), "big" ,signed=False)
        
        return nSize
    
    # read all next bytes
    def readToEnd(self) -> bytearray:
        result = self.bytes[self.cursor :]
        self.cursor = self.getLength()
        return bytearray(result)
    
    # read variable length integer functionality, moves cursor automaticaly
    def rVarInt(self):
        temp = 0
        while True:
            i = self.bytes[self.cursor]
            self.cursor +=1
            temp = (temp << 7) | (i & 0x7F)
            if(i & 0x80):
                temp += 1
            else:
                return temp