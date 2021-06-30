import mmap

# FileReader class performs file reading functionality
class FileReader:
    def __init__(self, blk_file):
        # memory mapped file
        self.blk_file = mmap.mmap(blk_file.fileno(), length = 0, flags=mmap.MAP_PRIVATE, prot=mmap.PROT_READ)
        self.blk_length = self.getLength()

    # get cursor position in blk_file
    def getPos(self):
        return self.blk_file.tell()
    
    # set absolute cursor position counted from begining of the file
    def setPos(self, pos : int):
        self.blk_file.seek(pos, 0)
    
    # move cursor relative to current position
    def move(self, pos : int):
        self.blk_file.seek(pos, 1)

    def getLength(self):
        currPos = self.getPos()
        self.blk_file.seek(0, 2)
        lastPos = self.getPos()
        self.setPos(currPos)
        return lastPos
    
    # read length of bytes, movement of the cursor is automated, no need to call move()
    # read also performs little endian conversion
    def read(self, length : int):
        return self.blk_file.read(length)[::-1]
    
    def reset(self):
        self.blk_file.seek(0, 0)
    
    def close(self):
        self.blk_file.close()