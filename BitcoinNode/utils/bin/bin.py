    def amount_compress(self, n: int) -> int:
        if n == 0:
            return 0
        e = 0
        while (n % 10) == 0 and e < 9:
            n = int(n / 10)
            e += 1
        if e < 9:
            d = n % 10
            assert d >= 1 and d <= 9
            n = int(n / 10)
            return 1 + (n*9 + d - 1)*10 + e
        else:
            return 1 + (n - 1)*10 + 9

    def amount_decompress(self, x: int) -> int:
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
    
     def decodeVarInt(self, data:bytearray) -> int:
        temp = 0
        a = 0
        while True:
            i = data[0]
            data = data[1:]
            temp = temp | (i & 0x7F) << a
            if(i & 0x80):
                a += 7
                continue
            else:
                return temp
    
    def writeVarInt(self, n:int) -> bytearray:
        u = (n.bit_length() + 7)//8
        tmp = bytearray(u + (u+7)//8 + 1)
        a = 0
        while True:
            if n > 0x7F:
                dat = 0x80
            else:
                dat = 0x00

            tmp[a] = (n & 0x7F) | dat
            if n <= 0x7F:
                break
            n = (n >> 7)
            a += 1

        # clean excesive zeros
        while True:
            if tmp[len(tmp)-1] == 0x00 and len(tmp) > 1:
                tmp = tmp[0:len(tmp)-1]
            else:
                break
        return tmp

path = PA.adb_cs + str(cs.latest_block_hash) + ".dict"
# save 
ser = SER.DictSerialize()
file = open(path, "wb")
file.write(ser.serializeDict(cdict, progress=True))
file.close()
del ser