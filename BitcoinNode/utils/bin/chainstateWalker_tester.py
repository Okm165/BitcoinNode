import utils.adb as ADB
import utils.chainstate as CS
import utils.paths as PA
import tqdm



db1 = ADB.DbHandler(PA.adb + str("00000000000000000009f5be8a0f298bfae3952fb45ac22a59fce268f9560bfd"))
db2 = ADB.DbHandler(PA.adb + str("00000000000000000009f5be8a0f298bfae3952fb45ac22a59fce268f9560bfd_1"))
# 00000000000000000000766418ba1fa707f69be37a1179ff1c4e00f677f7e3e5

# determine length
print("Calculating length...")
length = 0
for _ in db1.db:
    length += 1
print("length = " + str(length))
print("Testing...")
bar = tqdm.tqdm(
    total=length,
    colour="#bbc4c5",
    smoothing=0.01)

MMcounter = 0
Mcounter = 0
for key, value in db1.db:
    db2value = db2.db.get(key)
    if value != db2value:
        MMcounter += 1
    else:
        Mcounter += 1
    bar.update(1)
bar.refresh()
bar.close()

print("Match counter = " + str(Mcounter))
print("MissMatch counter = " + str(MMcounter))