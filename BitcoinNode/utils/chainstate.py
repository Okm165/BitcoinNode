import utils.bStream as BS
import utils.address as AC
import utils.utils as UT
import plyvel

# transaction object
class Tx:

    def __init__(self) -> None:
        self.hash = None            # transaction hash in bytes
        self.blkHeight = None       # height of the block transaction is coming from
        self.txHeight = None        # transaction height in block
        self.isCoinBase = None      # is transaction coinbase
        self.value = None           # transaction vlaue in SAT /100000000 to get BTC
        self.scriptType = None      # script type
        self.address = None         # address
    
    def __str__(self) -> str:
        string = ""
        string += "{\n"
        string += " hash = " + str(self.hash.hex()) + "\n"
        string += " blkHeight = " + str(self.blkHeight) + "\n"
        string += " txHeight = " + str(self.txHeight) + "\n"
        string += " isCoinBase = " + str(self.isCoinBase) + "\n"
        string += " value = " + str(self.value/100000000) + "\n"
        string += " scriptType = " + str(self.scriptType) + "\n"
        string += " address = " + str(self.address) + "\n"
        string += "}"
        return string

# chainstate database reader and decoder
class ChainDb:

    def __init__(self, chainstate_db_path, cursor = 0) -> None:
        self.db = plyvel.DB(chainstate_db_path, create_if_missing = False)
        # make everything tidy
        self.cursor = cursor
        self.db_it = self.db.raw_iterator()
        self.db_it.seek_to_first()
        # initialize
        self.obfuscation_key = None
        self.latest_block_hash = None
        self.dbInit()

    # read basic data (initialization step)
    def dbInit(self) -> None:
        self.getObfuscationKey()
        self.getLatestBlockHash()

    # read single row of chainstate database and decode it no endian conversions
    def getRow(self):
        data = self.db_it.item()
        self.cursor += 1
        self.db_it.next()
        return (data[0], self.applyObfuscationKey(data[1]))

    # get current position of iterator
    def getPos(self) -> int:
        return self.cursor
    
    def getLength(self, length = 0):
        if length == 0:
            for _ in self.db:
                length += 1
            return length - 2 # correction for obuscation key and block hash
        return length
    
    def getObfuscationKey(self):
        first_row = self.db_it.item()
        self.cursor += 1
        self.db_it.next()
        if not first_row[0] == b'\x0e\x00obfuscate_key': raise Exception("chainDb::getObfuscationKey could not localize obfuscation_key")
        self.obfuscation_key = first_row[1][1:]
    
    def applyObfuscationKey(self, data : bytes) -> bytes:
        return bytes(data[index] ^ self.obfuscation_key[index % len(self.obfuscation_key)] for index in range(len(data)))

    def getLatestBlockHash(self):
        second_row = self.getRow()
        if not second_row[0] == b'B': raise Exception("chainDb::getLatestBlockHash could not localize latest_block_hash")
        self.latest_block_hash = second_row[1][::-1].hex() # little endian conversion
    
    def getTx(self):
        data = self.getRow()
        tx = Tx()

        # read tx hash and index of output
        keyReader = BS.ByteReader(data[0])
        keyReader.move(1)
        tx.hash = keyReader.read(32)[::-1]
        tx.txHeight = keyReader.rVarInt()

        # read tx
        valueReader = BS.ByteReader(data[1])
        code = valueReader.rVarInt()
        tx.isCoinBase = bool(code & 0x01)
        tx.blkHeight = code >> 1
        tx.value = UT.amountDecompress(valueReader.rVarInt())

        script_type = int.from_bytes(valueReader.read(1), "big")
        tx.scriptType = script_type
        script = valueReader.readToEnd()

        # type switcher

        # Base58 P2PKH
        if(script_type == 0x00):
            tx.address = AC.Base58_P2PKH(script)
        
        # Base58 P2SH
        elif(script_type == 0x01):
            tx.address = AC.Base58_P2SH(script)
        
        # Base58 P2PKH no ripemdsha
        elif(script_type == 0x02 or script_type == 0x03):
            script.insert(0, script_type)
            tx.address = AC.Base58_P2PK_ripemdsha(script)
        
        # Base58 P2PKH compressed
        elif(script_type == 0x04 or script_type == 0x05):
            pub_key = AC.decompressPK(script, script_type)
            tx.address = AC.Base58_P2PK_ripemdsha(pub_key)

        # Bech32 P2WPKH
        elif(script_type == 0x1c):
            tx.address = AC.Bech32_P2WPKH(script)
        
        # Bech32 P2WSH
        elif(script_type == 0x28):
            tx.address = AC.Bech32_P2WSH(script)
        
        return tx
