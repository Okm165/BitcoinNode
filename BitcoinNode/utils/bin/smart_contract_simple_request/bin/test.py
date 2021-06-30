class SmartContract:
    def __init__(self):
        self.function = SmartContractFunctions()
        
    
class SmartContractFunctions:
    def __init__(self):
        setattr(self, "zmienna", 10)

entity = SmartContract()
entity.function.balance()