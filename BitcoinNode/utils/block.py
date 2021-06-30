import utils.utils as UT
import utils.address as AC
import utils.fStream as FS
import utils.bStream as BS

# Block class performs block object functionality
class Block:
    def __init__(self):
        self.hash = None                # value containing hash of this block
        self.hashPrev = None            # 32 byte SHA256 hash of the previous block hash
        self.height = None              # block haight in blockCHain
        self.id = None                  # value same for all block, no need to store it but helps in debugging
        self.headerLength = None        # contains the length of thus block in total
        self.version = None             # expected to be equal to 1 (0x00000001)
        self.hashMerkleRoot = None      # 32 byte hash of merkleTree root
        self.timeStamp = None           # the creation time of this block
        self.bits = None                # target difficulty
        self.nonce = None               # number added to block in order to make final hash be as desired
        self.txCount = None             # variable length integer describing number of transactions
        self.txArray = []               # array of Tx objects (transaction objects) representing each transaction in this block

    # block display function
    def __str__(self, n = 0):
        string =  UT.dent(n) + "Block{\n"
        string += UT.dent(n+1) + "hash = " + str(self.hash.hex()) + "\n"
        string += UT.dent(n+1) + "hashPrev = " + str(self.hashPrev.hex()) + "\n"
        string += UT.dent(n+1) + "id = " + str(self.id) + "\n"
        string += UT.dent(n+1) + "headerLength = " + str(self.headerLength) + "\n"
        string += UT.dent(n+1) + "version = " + str(self.version) + "\n"
        string += UT.dent(n+1) + "hashMerkleRoot = " + str(self.hashMerkleRoot.hex()) + "\n"
        string += UT.dent(n+1) + "timeStamp = " + str(self.timeStamp) + "\n"
        string += UT.dent(n+1) + "bits = " + str(self.bits) + "\n"
        string += UT.dent(n+1) + "nonce = " + str(self.nonce) + "\n"
        string += UT.dent(n+1) + "txCount = " + str(self.txCount) + "\n"
        string += UT.dent(n+1) + "txArray:\n"
        for tx in self.txArray:
            string += tx.__str__(n+1)
        string += UT.dent(n) + "}\n"
        return string

    # compute hash of the block
    def cmpHash(self, block_body:BS.ByteReader, blk_point1, blk_point2):
        diff = blk_point2 - blk_point1
        block_body.setPos(blk_point1)
        data = block_body.read(diff)[::-1]
        self.hash = AC.sha256(AC.sha256(data))[::-1]

# Tx transaction object
class Tx:
    def __init__(self) -> None:
        self.hash = None                # transaction hash
        self.version = None             # transaction version
        self.nHeight = None             # transaction height in block
        self.VinVec = []                # array of vin objects
        self.VoutVec = []               # array of vout objects
        self.nLockTime = None           # transaction lock time

        # experimental
        self.hashbuff = None
    
    def __str__(self, n = 0) -> str:
        string =  UT.dent(n) + "Tx[\n"
        string += UT.dent(n+1) + "hash = " + str(self.hash.hex()) + "\n"
        string += UT.dent(n+1) + "version = " + str(self.version) + "\n"
        string += UT.dent(n+1) + "nHeight = " + str(self.nHeight) + "\n"
        string += UT.dent(n+1) + "VinVec:\n"
        for vin in self.VinVec:
            string += vin.__str__(n+1)
        string += UT.dent(n+1) + "VoutVec:\n"
        for vout in self.VoutVec:
            string += vout.__str__(n+1)
        string += UT.dent(n+1) + "nLockTime = " + str(self.nLockTime) + "\n"
        string += UT.dent(n) + "]\n"
        return string

# CTxIn transaction input object
class CTxIn:
    def __init__(self) -> None:
        # COutPoint
        self.hash = None                #  a combination of a transaction hash
        self.n = None                   #  and an index n into origin transaction (previous one)
        # CScript
        self.script_length = None
        self.script = None              # CTxIn script
        # seq
        self.sequence = None
        #CScriptWitness                 # script.h :556
        self.scriptWitness = []         # witness script

        self.scriptDecoded = None
        self.witnessDecoded = None
    
    def __str__(self, n = 0) -> str:
        string =  UT.dent(n) + "CTxIn[\n"
        string += UT.dent(n+1) + "from_hash = " + str(self.hash.hex()) + " : " + str(self.n) + "\n"
        string += UT.dent(n+1) + "script_length = " + str(self.script_length) + "\n"
        string += UT.dent(n+1) + "script = " + str(self.script) + "\n"
        string += UT.dent(n+1) + "scriptDecoded = " + str(self.scriptDecoded) + "\n"
        string += UT.dent(n+1) + "sequence = " + str(self.sequence) + "\n"
        string += UT.dent(n+1) + "scriptWitness:" + "\n"
        for wscript in self.scriptWitness:
            string += UT.dent(n+1) + str(wscript) + "\n"
        string += UT.dent(n) + "]\n"
        return string

# CTxOut transaction output object
class CTxOut:
    def __init__(self) -> None:
        # CAmount
        self.amount = None              # transaction output value in SAT (SAT = 1/100000000 BTC)
        # CScript
        self.script_length = None
        self.script = None              # CTxOut script

        self.scriptDecoded = None
    
    def __str__(self, n = 0) -> str:
        string =  UT.dent(n) + "CTxOut[\n"
        string += UT.dent(n+1) + "amount = " + str(int.from_bytes(self.amount, "big")) + "\n"
        string += UT.dent(n+1) + "script_length = " + str(self.script_length) + "\n"
        string += UT.dent(n+1) + "script = " + str(self.script) + "\n"
        string += UT.dent(n+1) + "scriptDecoded = " + str(self.scriptDecoded) + "\n"
        string += UT.dent(n) + "]\n"
        return string

# Block reading functionality
class BlockReader:

    def __init__(self, idb_obj, blk_folder_path, opcodes_file_path):

        self.idb = idb_obj
        self.opcodes_file_path = opcodes_file_path
        self.blk_folder_path = blk_folder_path
        self.opCodeDecoder = AC.opCodes(self.opcodes_file_path)

    def readVinVec(self, block_body:BS.ByteReader) -> list:
        length = block_body.readCompactSize()
        vin_vec = []
        for i in range(length):
            ctx = CTxIn()
            # COutPoint
            ctx.hash = block_body.read(32)
            ctx.n = int.from_bytes(block_body.read(4), "big")
            # CScript
            ctx.script_length = block_body.readCompactSize()
            ctx.script = block_body.read(ctx.script_length)[::-1]
            # ctx.scriptDecoded = self.opCodeDecoder.vinScriptDecode(ctx.script)
            # Seq
            ctx.sequence = block_body.read(4)[::-1]
            vin_vec.append(ctx)

        return vin_vec

    def readVoutVec(self, block_body:BS.ByteReader) -> list:
        length = block_body.readCompactSize()
        vout_vec = []
        for i in range(length):
            ctx = CTxOut()
            # CAmount
            ctx.amount = int.from_bytes(block_body.read(8), "big")
            # CScript
            ctx.script_length = block_body.readCompactSize()
            ctx.script = block_body.read(ctx.script_length)[::-1]
            ctx.scriptDecoded = self.opCodeDecoder.voutScriptDecode(ctx.script)
            vout_vec.append(ctx)

        return vout_vec

    def getBlock(self, hash:str) -> Block:

        indexBlock = self.idb.fetchBlock(hash)

        block = Block()
        
        block.height = indexBlock.height
        nFile = indexBlock.nFile
        nDataPos = indexBlock.nDataPos

        file_path = (self.blk_folder_path + "blk" + str(100000+nFile)[1:] + ".dat")
        blk_file_reader = FS.FileReader(open(file_path, "rb"))
        # set position to nUndoPos
        blk_file_reader.setPos(nDataPos)

        blk_file_reader.move(-8)
        block.id = blk_file_reader.read(4)
        block.headerLength = int.from_bytes(blk_file_reader.read(4), "big")

        # get block body
        block_body = blk_file_reader.read(block.headerLength)[::-1]
        block_body = BS.ByteReader(block_body)

        block_pointer1 = block_body.getPos()

        block.version = int.from_bytes(block_body.read(4), "big")
        block.hashPrev = block_body.read(32)
        block.hashMerkleRoot = block_body.read(32)
        block.timeStamp = int.from_bytes(block_body.read(4), "big")
        block.bits = int.from_bytes(block_body.read(4), "big")
        block.nonce = int.from_bytes(block_body.read(4), "big")

        block_pointer2 = block_body.getPos()

        # compute hash
        block.cmpHash(block_body, block_pointer1, block_pointer2)

        # CTransaction vector unserialization
        block.txCount = block_body.readCompactSize()

        allow_witness = True # client version dependent, for updated clients always TRUE

        for ct in range(block.txCount):
            tx = Tx()

            tx.version = int.from_bytes(block_body.read(4), "big")
            block_body.move(-4)
            tx.hashbuff = block_body.read(4)[::-1]
            tx.nHeight = ct
            
            # read vin and vout
            flags = 0
            p1 = block_body.getPos()
            vin_vec = self.readVinVec(block_body)
            if len(vin_vec) == 0 and allow_witness:
                flags = int.from_bytes(block_body.read(1), "big")
                if flags != 0:
                    p1 = block_body.getPos()

                    vin_vec = self.readVinVec(block_body)
                    vout_vec = self.readVoutVec(block_body)

                    p2 = block_body.getPos()
                    block_body.setPos(p1)
                    tx.hashbuff += block_body.read(p2-p1)[::-1]
                    block_body.setPos(p2)
            else:
                vout_vec = self.readVoutVec(block_body)
                p2 = block_body.getPos()
                block_body.setPos(p1)
                tx.hashbuff += block_body.read(p2-p1)[::-1]
                block_body.setPos(p2)
            
            # read Witness
            if ((flags & 1) and allow_witness):
                flags ^= 1
                for vin in vin_vec:
                    wit_len = block_body.readCompactSize()
                    for _ in range(wit_len):
                        wit_item_len = block_body.readCompactSize()
                        vin.scriptWitness.append(block_body.read(wit_item_len)[::-1])
            
            tx.VinVec = vin_vec
            tx.VoutVec = vout_vec

            # nLockTime
            tx.nLockTime = block_body.read(4)[::-1]
            block_body.move(-4)
            tx.hashbuff += block_body.read(4)[::-1]
            
            # compute tx hash
            tx.hash = AC.sha256(AC.sha256(tx.hashbuff))[::-1]

            block.txArray.append(tx)

        return block