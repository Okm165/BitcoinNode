import utils.adb as ADB
import utils.paths as PA
import tqdm

hashdb1 = "000000000000000000083a925be6e51b6197222c52e8d9b64a13e12833cff607_1"
hashdb2 = "000000000000000000083a925be6e51b6197222c52e8d9b64a13e12833cff607"

addressdb1 = ADB.DbHandler(PA.adb_cs + hashdb1 + "/addressDb/")
amountdb1 = ADB.DbHandler(PA.adb_cs + hashdb1 + "/amountDb/")
addressdb2 = ADB.DbHandler(PA.adb_cs + hashdb2 + "/addressDb/")
amountdb2 = ADB.DbHandler(PA.adb_cs + hashdb2 + "/amountDb/")

print("testing addressDb's")
print("Calculating addressdb1 length...")
addressdb1length = 0
for _ in addressdb1.db:
    addressdb1length += 1
print("length = " + str(addressdb1length))
print("Calculating addressdb2 length...")
addressdb2length = 0
for _ in addressdb2.db:
    addressdb2length += 1
print("length = " + str(addressdb2length))

if addressdb1length == addressdb2length: print("length match!")
else: print("length missmatch!")

print("addressdb's testing...")
bar = tqdm.tqdm(
    total=addressdb1length,
    colour="#bbc4c5",
    smoothing=0.01)
MMcounter = 0
Mcounter = 0
for key, value in addressdb1.db:
    db2value = addressdb2.db.get(key)
    if value == db2value:
        Mcounter += 1
    else:
        MMcounter += 1
    bar.update(1)
bar.refresh()
bar.close()

print("addressdb Match counter = " + str(Mcounter))
print("addressdb MissMatch counter = " + str(MMcounter))

print("===========================================================")

print("testing amountDb's")
print("Calculating amountdb1 length...")
amountdb1length = 0
for _ in amountdb1.db:
    amountdb1length += 1
print("length = " + str(amountdb1length))
print("Calculating amountdb2 length...")
amountdb2length = 0
for _ in amountdb2.db:
    amountdb2length += 1
print("length = " + str(amountdb2length))

if amountdb1length == amountdb2length: print("length match!")
else: print("length missmatch!")

print("amountdb's testing...")
bar = tqdm.tqdm(
    total=amountdb1length,
    colour="#bbc4c5",
    smoothing=0.01)
MMcounter = 0
Mcounter = 0
for key, value in amountdb1.db:
    db2value = amountdb2.db.get(key)
    if value == db2value:
        Mcounter += 1
    else:
        MMcounter += 1
    bar.update(1)
bar.refresh()
bar.close()

print("amountdb Match counter = " + str(Mcounter))
print("amountdb MissMatch counter = " + str(MMcounter))