import utils.utils as UT
import utils.paths as PA
import tqdm

# func that makes address dictionary from raw chainstate
def composeAddressDict(cs, progress=False) -> dict:
    if progress: print("\rCalculating chainstate db length...")
    chainstate_length = cs.getLength(1000)
    if progress: print("chainstate db length = " + str(chainstate_length))
    cdict = dict()
    if progress:
        print("composing AddressDict...")
        bar = tqdm.tqdm(
            total=chainstate_length,
            colour="#bbc4c5",
            smoothing=0.01)

    for _ in range(chainstate_length):
        tx = cs.getTx()
        if tx.address is None:
            if progress: bar.update(1)
            continue
        address = tx.address
        dbrow = None
        if address in cdict:
            dbrow = cdict[address]

        if dbrow is not None:
            amount_total = dbrow + tx.value
            cdict[address] = amount_total
        else:
            cdict[address] = tx.value
        if progress:bar.update(1)
    if progress:
        bar.refresh()
        bar.close()
    return cdict

# func that makes amount dictionary from address dictionary
def composeAmountDict(cdict, progress=False) -> dict:
    adict = dict()
    if progress:
        print("composing AmountDict...")
        bar = tqdm.tqdm(
            total=len(cdict),
            colour="#bbc4c5",
            smoothing=0.01)
    for key, value in cdict.items():
        value = value.to_bytes(64, "big", signed=False)
        if value in adict:
            adict[value] = adict[value] + 1
        else:
            adict[value] = 1
        if progress:bar.update(1)
    if progress:
        bar.refresh()
        bar.close()
    
    return adict

def parse(cs, progress=False) -> bool:
    path = PA.adb_cs + str(cs.latest_block_hash) + '/'
    if UT.checkIfDirExists(path): UT.clearFolder(path)
    else: UT.createFolder(path)

    cdict = composeAddressDict(cs, progress=progress)
    UT.saveDictToAdb(path + PA.p__addressDict, cdict, progress=progress)

    adict = composeAmountDict(cdict, progress=progress)
    UT.saveDictToAdb(path + PA.p__amountDict, adict, progress=progress)
    return True