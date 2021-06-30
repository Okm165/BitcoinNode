from ecdsa import VerifyingKey, SECP256k1
import utils.bStream as BS
import hashlib
import base58
import bech32
import json

def sha256(data):
    return bytearray(hashlib.sha256(data).digest())

def ripemd160(data):
    return bytearray(hashlib.new('ripemd160', data).digest())

def ripemdsha(data):
    return ripemd160(sha256(data))

def decompressPK(script, script_type):
    sh = bytearray(script)
    sh.insert(0, script_type-2)
    vk = VerifyingKey.from_string(bytes(sh), curve=SECP256k1)
    pub_key = vk.to_string("uncompressed")
    return pub_key

def Base58(data, id):
    sh = bytearray(data)
    sh.insert(0, id)
    checksum = sha256(sha256(sh))[:4]
    sh.extend(checksum)
    return (base58.b58encode(sh))

def Bech32(witver, data):
    return (bech32.encode("bc", witver, data).encode("ascii"))

def Base58_P2PKH(script):
    return Base58(script, 0)

def Base58_P2SH(script):
    return Base58(script, 5)

def Base58_P2PK_ripemdsha(script):
    sh = bytearray(script)
    sh = ripemdsha(sh)
    return Base58(sh, 0)

def Bech32_P2WPKH(script):
    witver = script[0]
    witprog_len = script[1]
    if(witver):
        witver -= 80
    return Bech32(witver, script[2:][:witprog_len])

def Bech32_P2WSH(script):
    witver = script[0]
    witprog_len = script[1]
    if(witver):
        witver -= 80
    return Bech32(witver, script[2:][:witprog_len])

# address decoding functionality for block_reader
def addressDecode(data):
    address = None
    if len(data) == 2:
        
        # Burn
        if data[0] == "OP_RETURN" or data[1] == "OP_RETURN":
            address = ""
        
        # Bech32_P2WPKH
        if data[0] == "OP_0" and len(data[1]) == 20:
            data = bytearray(data[1])
            data.insert(0, 20)
            data.insert(0, 0)
            address = Bech32_P2WPKH(data)
        
        # Bech32_P2WSH
        if data[0] == "OP_0" and len(data[1]) == 32:
            data = bytearray(data[1])
            data.insert(0, 32)
            data.insert(0, 0)
            address = Bech32_P2WSH(data)
        # Bech32_P2PK
        if data[1] == "OP_CHECKSIG":
            
            if len(data[0]) == 65:
                address = Base58_P2PK_ripemdsha(data[0])
            if len(data[0]) == 33:
                pub_key = decompressPK(data[0][1:], data[0][:1])
                address = Base58_P2PK_ripemdsha(pub_key)
    # Base58_P2SH
    elif len(data) == 3:
        if data[0] == "OP_HASH160" and len(data[1]) == 20 and data[2] == "OP_EQUAL":
            address = Base58_P2SH(data[1])
    
    # Base58_P2PKH
    elif len(data) == 5:
        if data[0] == "OP_DUP" and data[1] == "OP_HASH160" and len(data[2]) == 20 and data[3] == "OP_EQUALVERIFY" and data[4] == "OP_CHECKSIG":
            address = Base58_P2PKH(data[2])
    
    return address

# general script decoding functionality for block_reader
def scriptDecode(op_dict, data):
    decoded = []
    reader = BS.ByteReader(data)
    length = len(data)
    while(reader.getPos() < length):
        curr_byte = int.from_bytes(reader.read(1), "big")
        chex = hex(curr_byte)
        decoded.append(op_dict[chex])

        # special opcodes (that read data from script)
        if op_dict[chex] == "N/A":
            decoded.pop()
            decoded.append(reader.read(curr_byte)[::-1])
        elif op_dict[chex] == "OP_PUSHDATA1":
            decoded.append(reader.read(1)[::-1])
        elif op_dict[chex] == "OP_PUSHDATA2":
            decoded.append(reader.read(2)[::-1])
        elif op_dict[chex] == "OP_PUSHDATA4":
            decoded.append(reader.read(4)[::-1])
        elif op_dict[chex] == "OP_RETURN":
            decoded.append(reader.readToEnd()[::-1])
    
    return decoded

# opCodes class performs required initialization and creates dict for encoder
class opCodes:

    def __init__(self, opcodes_file_path) -> None:
        self.opcodes_file_path = opcodes_file_path
        self.json = json.load(open(self.opcodes_file_path, "r"))
        self.op_dict = self.createOpDict()

    def createOpDict(self):
        op_dict = dict()
        items = self.json.items()
        for key, value in items:
            key = key.split(",")
            if len(key) == 2:
                start = int(key[0], 16)
                stop = int(key[1], 16)
                while stop >= start:
                    op_dict[hex(start)] = value
                    start += 1
            else:
                op_dict[key[0]] = value
        return op_dict
    
    def vinScriptDecode(self, data):
        decoded = scriptDecode(self.op_dict, data)
        return decoded

    def voutScriptDecode(self, data):
        decoded = scriptDecode(self.op_dict, data)
        address = addressDecode(decoded)
        return (decoded, address)