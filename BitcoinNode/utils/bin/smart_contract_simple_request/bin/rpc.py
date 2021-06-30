import requests

payload = '{"jsonrpc":"2.0","method":"eth_call","params": [{"to":"0x0e09fabb73bd3ade0a17ecc321fd13a19e81ce82","data":"0x70a0823100000000000000000000000072FDe84Db024a82459B6Cf2EE0b96c4890BCC18D"}, "latest"],"id":1}'
url = "https://bsc-dataseed1.binance.org:443"
receive = requests.post(url , data = payload)
print(receive.text)


# cc864d0a