import plyvel

class DbHandler:
    def __init__(self, addressDb_folder_path, create_if_missing=False) -> None:
        self.addressDb_folder_path = addressDb_folder_path
        self.db = plyvel.DB(self.addressDb_folder_path, create_if_missing=create_if_missing)
    
    # function that adds (can take negative amount values)
    def updateRecord(self, addrKey : bytes, amount : int):
        addrValue = self.db.get(addrKey)
        if addrValue is None: 
            if amount > 0:
                self.db.put(addrKey, amount.to_bytes((amount.bit_length() + 7)//8, 'big'))
            return
        
        nAddrValue = int.from_bytes(addrValue, "big") + amount
        if nAddrValue > 0:
            self.db.put(addrKey, nAddrValue.to_bytes((nAddrValue.bit_length() + 7)//8, 'big'))
        else: self.db.delete(addrKey)
    
    def writeRecord(self, addrKey : bytes, amount):
        self.db.put(addrKey, amount.to_bytes((amount.bit_length() + 7)//8, 'big'))