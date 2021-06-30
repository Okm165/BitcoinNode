import utils.fStream as FS
import utils.bStream as BS
import utils.address as AC
import utils.utils as UT

# UndoBlock class
class UndoBlock:

    def __init__(self) -> None:
        self.hash = None                # hash of this block
        self.hashPrev = None            # prev hash of this block
        self.nFile = None               # file number to look for the block tmp: rev?????.dat / blk?????.dat
        self.nDataPos = None            # pointer to block in blk file
        self.nUndoPos = None            # pointer to undoBlock in rev file
        self.txArray = []               # undo transaction records (list of Tx objects)
        self.checksum = None            # hash of entire block for safety purposes
    
    def __str__(self, n = 0) -> str:
        string =  UT.dent(n) + "UndoBlock{\n"
        string += UT.dent(n+1) + "hash = " + str(self.hash) + "\n"
        string += UT.dent(n+1) + "hashPrev = " + str(self.hashPrev) + "\n"
        string += UT.dent(n+1) + "nFile = " + str(self.nFile) + "\n"
        string += UT.dent(n+1) + "nDataPos = " + str(self.nDataPos) + "\n"
        string += UT.dent(n+1) + "nUndoPos = " + str(self.nUndoPos) + "\n"
        string += UT.dent(n+1) + "txArray:\n"
        for tx in self.txArray:
            string += tx.__str__(n+1)
        string += UT.dent(n+1) + "checksum = " + str(self.checksum) + "\n"
        string += UT.dent(n) + "}\n"
        return string

# transaction object
class Tx:

    def __init__(self) -> None:
        self.blkHeight = None       # height of the block transaction is coming from
        self.txHeight = None        # transaction height in block
        self.nHeight = None         # transfer height in transaction
        self.isCoinBase = None      # is transaction coinbase
        self.version = None         # transaction version only when height > 0
        self.value = None           # transaction vlaue in SAT /100000000 to get BTC
        self.scriptType = None      # script type
        self.address = None         # address
    
    def __str__(self, n = 0) -> str:
        string =  UT.dent(n) + "Tx{\n"
        string += UT.dent(n+1) + "blkHeight = " + str(self.blkHeight) + "\n"
        string += UT.dent(n+1) + "txHeight = " + str(self.txHeight) + "\n"
        string += UT.dent(n+1) + "nHeight = " + str(self.nHeight) + "\n"
        string += UT.dent(n+1) + "isCoinBase = " + str(self.isCoinBase) + "\n"
        string += UT.dent(n+1) + "version = " + str(self.version) + "\n"
        string += UT.dent(n+1) + "value = " + str(self.value/100000000) + "\n"
        string += UT.dent(n+1) + "scriptType = " + str(self.scriptType) + "\n"
        string += UT.dent(n+1) + "address = " + str(self.address) + "\n"
        string += UT.dent(n) + "}\n"
        return string
        # rev reader

# rev?????.dat file reder
class Rev:

    def __init__(self, idb_obj, rev_folder_path) -> None:
        self.idb = idb_obj
        self.rev_folder_path = rev_folder_path

    def getUndoBlock(self, hash) -> UndoBlock:
        indexBlock = self.idb.fetchBlock(hash)

        # compose UndoBlock object
        
        block = UndoBlock()
        block.hash = hash
        block.hashPrev = indexBlock.hashPrev
        block.nFile = indexBlock.nFile
        block.nDataPos = indexBlock.nDataPos
        block.nUndoPos = indexBlock.nUndoPos

        file_path = (self.rev_folder_path + "rev" + str(100000+block.nFile)[1:] + ".dat")
        rev_file_reader = FS.FileReader(open(file_path, "rb"))
        # set position to nUndoPos
        rev_file_reader.setPos(block.nUndoPos)
        rev_file_reader.move(-8)
        rev_id = rev_file_reader.read(4)[::-1]
        rev_size = int.from_bytes(rev_file_reader.read(4), "big")

        rev_body = BS.ByteReader(rev_file_reader.read(rev_size)[::-1])
        rev_num = rev_body.readCompactSize()

        for i in range(rev_num):
            num = rev_body.readCompactSize()

            for n in range(num):
                tx = Tx()
                tx.txHeight = i
                tx.nHeight = n
                rev_code = rev_body.rVarInt()
                isCoinbase = bool(rev_code & 1)
                rev_height = rev_code >> 1
                tx.blkHeight = rev_height
                tx.isCoinBase = isCoinbase
                if (rev_height > 0):
                    rev_version = rev_body.rVarInt()
                    tx.version = rev_version
                
                rev_val = UT.amountDecompress(rev_body.rVarInt())
                tx.value = rev_val
    
                script_type = rev_body.rVarInt()
                tx.scriptType = script_type
    
                # type switcher
                address = None
                # Base58 P2PKH
                if(script_type == 0x00):
                    script = rev_body.read(20)[::-1]
                    address = AC.Base58_P2PKH(script)
    
                # Base58 P2SH
                elif(script_type == 0x01):
                    script = rev_body.read(20)[::-1]
                    address = AC.Base58_P2SH(script)
    
                # Base58 P2PKH no ripemdsha
                elif(script_type == 0x02 or script_type == 0x03):
                    script = bytearray(rev_body.read(32))[::-1]
                    script.insert(0, script_type)
                    address = AC.Base58_P2PK_ripemdsha(script)
    
                # Base58 P2PKH compressed
                elif(script_type == 0x04 or script_type == 0x05):
                    script = bytearray(rev_body.read(32))[::-1]
                    pub_key = AC.decompressPK(script, script_type)
                    address = AC.Base58_P2PK_ripemdsha(pub_key)
    
                # Bech32 P2WPKH
                elif(script_type == 0x1c):
                    script = rev_body.read(22)[::-1]
                    address = AC.Bech32_P2WPKH(script)
    
                # Bech32 P2WSH
                elif(script_type == 0x28):
                    script = rev_body.read(34)[::-1]
                    address = AC.Bech32_P2WSH(script)
                tx.address = address
                block.txArray.append(tx)

        block.checksum = rev_file_reader.read(32).hex()
        return block