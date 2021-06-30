import utils.adb as ADB
import shutil
import os
import tqdm

# opcodes definitions
ADD = 1
SUBSTRACT = -1

def dent(n) -> str:
    string = ""
    for _ in range(n):
        string += " "
    return string

def dictWrite(dict, key, value, op=ADD):
    if value == 0: return
    if op == ADD:
        val = value
    elif op == SUBSTRACT:
        val = -value
    # check if record exists in dict already
    if key in dict:
        prevVal = dict[key]
        val = val + prevVal
        if val == 0: 
            del dict[key]
            return
        dict[key] = val
    else:
        dict[key] = val

def copyDir(src, dst, progress=False):
    if progress: print("Copying...", end="", flush=True)
    if checkIfDirExists(dst): removeFolder(dst)
    shutil.copytree(src, dst, copy_function = shutil.copy) 
    if progress: print("Done")
    
def clearFolder(path):
    for file in os.listdir(path):
        file_path = os.path.join(path, file)
        if os.path.isfile(file_path):
            os.unlink(file_path)
        elif os.path.isdir(file_path):
            clearFolder(file_path)
            os.rmdir(file_path)

def removeFolder(path):
    clearFolder(path)
    os.rmdir(path)

def createFolder(path):
    os.mkdir(path)

def checkIfDirExists(path) -> bool:
    if os.path.isdir(path):
        # exists
        return True
    else:
        return False

def checkIfFileExists(path) -> bool:
    if os.path.isfile(path):
        # exists
        return True
    else:
        return False

def sign(num) -> int:
    if num > 0: return 1
    elif num < 0: return -1
    elif num == 0: return 0

def amountDecompress(x: int) -> int:
    # x = 0    x = 1+10*(9*n + d - 1) + e    x = 1+10*(n - 1) + 9
    if x == 0:
        return 0
    x -=1
    # x = 10*(9*n + d - 1) + e
    e = x % 10
    x = int(x / 10)
    n = 0
    if e < 9:
        # x = 9*n + d - 1
        d = (x % 9) + 1
        x = int(x / 9)
        # x = n
        n = x*10 + d
    else:
        n = x+1
    while e:
        n *= 10
        e -= 1
    return n

def amountCompress(x: int) -> int:
    if x == 0:return 0
    e = 0
    while (x % 10) == 0 and e < 9:
        x = x // 10
        e += 1
    if e < 9:
        d = x % 10
        assert d >= 1 and d <= 9
        x = x // 10
        return 1 + (x*9 + d - 1)*10 + e
    else:
        return 1 + (x - 1)*10 + 9

def mergeSort(list) -> list:
    if len(list) > 2:
        dev = len(list)//2
        a = mergeSort(list[:dev])
        b = mergeSort(list[dev:])
        # merge two lists
        list = []
        while True:
            if a[0] < b[0]:
                list.append(a[0])
                a = a[1:]
                if len(a) == 0:
                    list += b
                    break
            else:
                list.append(b[0])
                b = b[1:]
                if len(b) == 0:
                    list += a
                    break
        return list

    elif len(list) == 1: return list
    elif len(list) == 2:
        a = list[0]
        b = list[1]
        if b > a: return list
        else:
            # swap
            list[0] = b
            list[1] = a
            return list

def mergeSortTuple(list) -> list:
    if len(list) > 2:
        dev = len(list)//2
        a = mergeSort(list[:dev])
        b = mergeSort(list[dev:])
        # merge two lists
        list = []
        while True:
            if a[0][0] < b[0][0]:
                list.append(a[0])
                a = a[1:]
                if len(a) == 0:
                    list += b
                    break
            else:
                list.append(b[0])
                b = b[1:]
                if len(b) == 0:
                    list += a
                    break
        return list

    elif len(list) == 1: return list
    elif len(list) == 2:
        a = list[0]
        b = list[1]
        if b[0] > a[0]: return list
        else:
            # swap
            list[0] = b
            list[1] = a
            return list

def orderedListInsert(arr:list, val:int, st, en) -> None:
    length = en-st
    if length == 0:
        if arr[st] > val: arr.insert(st, val)
        else: arr.insert(st+1, val)
        return

    dev = length//2
    if arr[st+dev] > val: orderedListInsert(arr, val, st, st+dev)
    else: orderedListInsert(arr, val, st+dev+1, en)
    # extensive tests passed

def orderedTupleListInsert(arr:list, val:tuple, st, en) -> None:
    length = en-st
    if length == 0:
        if arr[st][0] > val[0]: arr.insert(st, val)
        else: arr.insert(st+1, val)
        return

    dev = length//2
    if arr[st+dev][0] > val[0]: orderedListInsert(arr, val, st, st+dev)
    else: orderedListInsert(arr, val, st+dev+1, en)
    # extensive tests passed

def saveDictToAdb(path, dict:dict, progress=False):
    if checkIfDirExists(path): clearFolder(path)
    else: createFolder(path)
    adb = ADB.DbHandler(path, create_if_missing=True)
    if progress:
        bar = tqdm.tqdm(
            print("Marking..."),
            total=len(dict),
            colour="#bbc4c5",
            smoothing=0.01)
    for key, value in dict.items():
        adb.writeRecord(key, value)
        if progress: bar.update(1)
    if progress:
        bar.refresh()
        bar.close()