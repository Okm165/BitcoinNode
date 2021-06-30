import json
import sha3
import requests

configFile = open("config/node.json", "r")
config = json.loads(configFile.read())

class SmartContract:
    def __init__(self, url):
        self.url = url

    def request(self, params, QUANTITY, ID):
        payload = '{"jsonrpc":"2.0","method":"eth_call","params": [{' + params + '}, "' + QUANTITY + '"],"id":' + ID + '}'
        receive = requests.post(self.url , data = payload)
        return receive.json()

    def function(self, eth_call_args, abi, name, eth_sm_args, QUANTITY = "latest", ID = "1"):
        functions = [item for item in abi if item["type"] == "function"]
        target_function = [item for item in functions if item["name"] == name][0]
        target_function_inputs = [item["internalType"] for item in target_function["inputs"]]
        string_buff = target_function["name"] + "("
        for item in target_function_inputs:
            string_buff += item + ","
        string_buff = string_buff[:-1]
        string_buff += ")"
        alg = sha3.keccak_256()
        alg.update(string_buff.encode("ASCII"))
        params = ""
        eth_call_args_list = [item for item in eth_call_args.items()]
        for arg in eth_call_args_list:
            params += '"' + arg[0] + '":"' + arg[1] + '",'
        params += '"data":' + '"0x' + alg.hexdigest()[:8]
        for eth_sm_arg in eth_sm_args:
            params += eth_sm_arg.zfill(64)
        params += '"'
        return self.request(params, QUANTITY, ID)


entity = SmartContract(url=config["SETUP"]["url"])

eth_call_args = {"to" : config["SMART_CONTRACT"]["CAKE"]["address"]}

eth_sm_args = ["72FDe84Db024a82459B6Cf2EE0b96c4890BCC18D"]

print(entity.function(eth_call_args, config["SMART_CONTRACT"]["CAKE"]["abi"], "balanceOf", eth_sm_args))

