import utils.serialize as SER
import utils.adb as ADB
import utils.idb as IDB
import utils.block as BLK
import utils.rev as REV
import utils.utils as UT
import utils.paths as PA
import tqdm

#   in order to go back on the chainstate we need to fullfill two stages input gratification and output reduction
#   input gratification is function that will recreate inputs state that was before the BLOCK, on the other hand 
#   output reduction function will undo the transactions in the BLOCK 
#   
#   reason for this solution is that in block transaction there is no information about amount that was withdrawn from input, 
#   that is why there is need to use both block reader/analizer (to undo outputs) and rev files reader/analizer (to undo inputs)
    
class ChainW:
    def __init__(self) -> None:
        # create IndexDbReader object
        self.idb = IDB.IndexDb(PA.idb)
        # rev?????.dat reader object
        self.rev = REV.Rev(self.idb, PA.rev_folder_path)
        # blk?????.dat reader object
        self.blk = BLK.BlockReader(self.idb, PA.blk_folder_path, PA.op)

    def getRevUndoData(self, hash) -> list:
        # add values from rev file to chainstate,
        # these are values that were taken from corresponding addresses in current block
        # and should be added back to recreate previous chainstate
        revUndoList = list()
        undo_block = self.rev.getUndoBlock(hash)
        
        for tx in undo_block.txArray:
            if tx.address == "" or tx.address is None: continue
            revUndoList.append((tx.address, tx.value))
        return revUndoList

    def getBlkUndoData(self, hash) -> list:
        # substract values blk file data from chainstate,
        # these are values that were added to addresses in this block
        # and should be substracted in order to imitate previous chainstate state
        blkUndoList = list()
        undo_block = self.blk.getBlock(hash)

        for tx in undo_block.txArray:
            for vout in tx.VoutVec:
                if vout.scriptDecoded[1] == "" or vout.scriptDecoded[1] is None: continue
                blkUndoList.append((vout.scriptDecoded[1], vout.amount))
        return blkUndoList

    def composeChangeDict(self, hash, progress=False) -> dict:
        # undoDict stores data about how corresponding addresses should be changed based on prev addressDb
        # (with possitive sign, amount should be added to existing addresses)
        if progress: print("Computing changeDict...", end ="", flush=True)

        changeDict = dict()
        revUndoList = self.getRevUndoData(hash)
        blkUndoList = self.getBlkUndoData(hash)
        for key, value in revUndoList:
            UT.dictWrite(changeDict, key, value, op=UT.SUBSTRACT)
        for key, value in blkUndoList:
            UT.dictWrite(changeDict, key, value, op=UT.ADD)
        
        if progress: print("Done")

        return changeDict
    
    def composeAmountChangeDict(self, addressChangeDict, adbaddr, sign, progress=False) -> dict:
        if progress:
            print("Composing amountChangeDict...")
            bar = tqdm.tqdm(
                total=len(addressChangeDict),
                colour="#bbc4c5",
                smoothing=0.01)
        amountChangeDict = dict()
        for key, value in addressChangeDict.items():
            prev = adbaddr.db.get(key)
            if prev is None: 
                akey = abs(value).to_bytes(64, "big", signed=False)
                UT.dictWrite(amountChangeDict, akey, 1)
            else:
                prev = int.from_bytes(prev, "big", signed=False)

                akey = abs(prev).to_bytes(64, "big", signed=False)
                UT.dictWrite(amountChangeDict, akey, -1)
                if prev + value*sign == 0: 
                    if progress: bar.update(1)
                    continue
                akey = abs(prev + value*sign).to_bytes(64, "big", signed=False)
                UT.dictWrite(amountChangeDict, akey, 1)
            if progress: bar.update(1)
        if progress:
            bar.refresh()
            bar.close()

        return amountChangeDict
    
    def loadChangeDict(self, path, progress=False) -> dict:
        # changeDict = dict()
        # adb = ADB.DbHandler(path)
        # for key, value in adb.db:
        #     val = int.from_bytes(value, "big", signed=signed)
        #     if key in changeDict:
        #         temp = changeDict[key]
        #         val += temp
        #     changeDict[key] = val
        # return changeDict

        ser = SER.DictSerialize()
        file = open(path, "rb")
        cdict = ser.deserializeDict(file.read(), progress=progress)
        file.close()
        del ser
        return cdict

    def saveChangeDict(self, cdict, path, progress=False):
        # adb = ADB.DbHandler(PA.adb_pb + hash + "/", create_if_missing=True)
        # for key, value in cdict.items():
        #     adb.writeRecord(key, value)
        
        ser = SER.DictSerialize()
        file = open(path, "wb")
        file.write(ser.serializeDict(cdict, progress=progress))
        file.close()
        del ser
      
    def getHashPath(self, StartHash, DstHash, override=False) -> list:
        # generate hash path to target hash
        hashList = []
        newStartHash = None
        sign = UT.sign((self.idb.fetchBlock(DstHash)).height-(self.idb.fetchBlock(StartHash)).height)
        if sign == 0: return hashList, sign
        elif sign == 1:
            while StartHash != DstHash:
                if UT.checkIfDirExists(PA.adb_cs + DstHash + "/") and not override: 
                    newStartHash = DstHash
                    break
                hashList.insert(0, DstHash)
                DstHash = (self.idb.fetchBlock(DstHash)).hashPrev
        else:
            while StartHash != DstHash:
                if UT.checkIfDirExists(PA.adb_cs + StartHash + "/") and not override: 
                    hashList = []
                    newStartHash = StartHash
                hashList.append(StartHash)
                StartHash = (self.idb.fetchBlock(StartHash)).hashPrev
                
        return hashList, sign, newStartHash
    
    def generateState(self, StartHash, DstHash, progress=False, override=False):
        if UT.checkIfDirExists(PA.adb_cs + DstHash) and not override: return

        hashPath, sign, StartHash = self.getHashPath(StartHash=StartHash, DstHash=DstHash, override=override)
        addressChangeDict = dict()
        
        if progress:
            print("Composing addressChangeDict...")
            bar = tqdm.tqdm(
                total=len(hashPath),
                colour="#bbc4c5",
                smoothing=0.01)

        for hashStep in hashPath:
            path = PA.adb_pb + hashStep + ".dict"
            if not UT.checkIfFileExists(path):
                cdict = self.composeChangeDict(hashStep)
                self.saveChangeDict(cdict, path, progress=False)
            else:
                cdict = self.loadChangeDict(path)

            for key, value in cdict.items():
                UT.dictWrite(addressChangeDict, key, value)

            if progress: bar.update(1)

        if progress:
            bar.refresh()
            bar.close()

        # repair StartHash
        adbaddrold = ADB.DbHandler(PA.adb_cs + StartHash + "/addressDb/")
        amountChangeDict = self.composeAmountChangeDict(addressChangeDict, adbaddrold, sign, progress=True)
        adbaddrold.db.close()

        UT.copyDir(PA.adb_cs + StartHash + "/", PA.adb_cs + DstHash + "/", progress=True)

        adbaddr = ADB.DbHandler(PA.adb_cs + DstHash + "/addressDb/")
        adbamou = ADB.DbHandler(PA.adb_cs + DstHash + "/amountDb/")

        if progress:
            print("Marking addressDb...")
            bar = tqdm.tqdm(
                total=len(addressChangeDict),
                colour="#bbc4c5",
                smoothing=0.01)
        for key, value in addressChangeDict.items():
            adbaddr.updateRecord(key, value*sign)
            if progress: bar.update(1)
        if progress: 
            bar.refresh()
            bar.close()
        adbaddr.db.close()

        if progress:
            print("Marking amountDb...")
            bar = tqdm.tqdm(
                total=len(amountChangeDict),
                colour="#bbc4c5",
                smoothing=0.01)
        for key, value in amountChangeDict.items():
            adbamou.updateRecord(key, value)
            if progress: bar.update(1)
        if progress: 
            bar.refresh()
            bar.close()
        adbamou.db.close()
        
# chainw = ChainW()

# chainw.generateState(
#     StartHash = "00000000000000000009734043fa44a6859e6085c8a5ec6679afc5a01cda22a3",
#     DstHash = "000000000000000000083a925be6e51b6197222c52e8d9b64a13e12833cff607",
#     progress=True,
#     # override=True
# )
