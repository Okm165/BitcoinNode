import plyvel

class indexDbBlock:
    def __init__(self) -> None:

        self.nVersion = None                    # version
        self.height = None                      # block height in blockchain
        self.nStatus = None                     # blcok status
        self.nTx = None                         # number of transactions in block
        self.nFile = None                       # file number in which the block is stored blk?????.dat/ rev?????.dat
        self.nDataPos = None                    # pointer in blk file where block is stored
        self.nUndoPos = None                    # pointer in rev file where undoblock is stored

        self.version = None                     # block version header
        self.hashPrev = None                    # previous block hash
        self.hashMerkleRoot = None              # merkle tree root hash
        self.nTime = None                       # timestamp
        self.nBits = None                       # nBits
        self.nNonce = None                      # nNonce

# LevelDb class performs index_db reading functionality
class IndexDb:
    
    def __init__(self, indexDb_folder_path):
        self.indexDb_folder_path = indexDb_folder_path
        self.db = plyvel.DB(self.indexDb_folder_path, create_if_missing=False)

    #requires hash in hex string
    def fetchBlock(self , hash:str) -> indexDbBlock:
        key = bytearray.fromhex(hash)[::-1]
        key.insert(0, ord('b'))
        self.dbvalue_byte_array = self.db.get(bytes(key))
        if self.dbvalue_byte_array is None: raise Exception("LevelDbReader:fetchBlock couldn't find block in indexDb")
        self.value = []
        self.readVarInt()
        self.readBlockHeader()

        block = indexDbBlock()
        block.nVersion = self.value[0]
        block.height = self.value[1]
        block.nStatus = self.value[2]
        block.nTx = self.value[3]
        block.nFile = self.value[4]
        block.nDataPos = self.value[5]
        block.nUndoPos = self.value[6]
        block.version = self.value[7]
        block.hashPrev = self.value[8]
        block.hashMerkleRoot = self.value[9]
        block.nTime = self.value[10]
        block.nBits = self.value[11]
        block.nNonce = self.value[12]

        return block
    
    def readVarInt(self):
        temp = 0
        while True:
            i = self.dbvalue_byte_array[0]
            self.dbvalue_byte_array = self.dbvalue_byte_array[1:]
            temp = (temp << 7) | (i & 0x7F)
            if(i & 0x80):
                temp += 1
            else:
                self.value.append(temp)
                temp = 0
            if(len(self.dbvalue_byte_array)==0 or len(self.value) > 6):
                return

    def readBlockHeader(self):
        #read nVersion
        self.value.append(int.from_bytes(self.readNext(4), "little"))
        #read hashPrev
        self.value.append(self.readNext(32)[::-1].hex())
        #read hashMerkleRoot
        self.value.append(self.readNext(32)[::-1].hex())
        #read nTime
        self.value.append(int.from_bytes(self.readNext(4), "little"))
        #read nBits
        self.value.append(int.from_bytes(self.readNext(4), "little"))
        #read nNonce
        self.value.append(int.from_bytes(self.readNext(4), "little"))

    def readNext(self, amount):
        ret = self.dbvalue_byte_array[:amount]
        self.dbvalue_byte_array = self.dbvalue_byte_array[amount:]
        return ret
    
    def clear(self):
        self.key = None
        self.value = []
        self.dbvalue_byte_array = []