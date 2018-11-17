# -*- coding: utf-8 -*-
import os
import time
import json

#Some common params
WEB3_PROVIDER = os.environ.get('WEB3_PROVIDER','wss://rinkeby.infura.io/ws/v3/22238a03c4ce4f6e9b2a3e0e899a77e6')
#New infura
#https://rinkeby.infura.io/v3/22238a03c4ce4f6e9b2a3e0e899a77e6
#https://mainnet.infura.io/v3/22238a03c4ce4f6e9b2a3e0e899a77e6

#w3 = Web3(HTTPProvider('https://mainnet.infura.io/5i7ovfspYawMeU8Ik0Q4')) 
#MainNet infuraw3 = Web3(HTTPProvider('https://rinkeby.infura.io/5i7ovfspYawMeU8Ik0Q4')) #Rinkeby infurra
#w3 = Web3(HTTPProvider('http://127.0.0.1:8545'))
#w3 = Web3(Web3.WebsocketProvider("ws://172.31.21.15:8546"))
#
ADDRESS_SYNPATREGISTER = '0xeBE8708A58D7BA56e91677e99cA117CA1F32C9a9'
ADDRESS_OPERATOR = '0xafB42ffDC859f82eDb3E93680F95212200f0CCA1'
PK_OPERATOR = os.environ.get('PK_OPERATOR','12345678')
# contracts ABI (!!!!! true->True, false ->False    - Python style)
ABI_SYNPATREGISTER = json.loads('[{"constant":true,"inputs":[],"name":"version","outputs":[{"name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[],"name":"confirmMyWallet","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[],"name":"getEvenet","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"anonymous":false,"inputs":[{"indexed":true,"name":"_from","type":"address"},{"indexed":false,"name":"_when","type":"uint64"}],"name":"Confirm","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"name":"_from","type":"address"},{"indexed":false,"name":"_when","type":"uint64"}],"name":"SimpleEvent","type":"event"}]')

START_FROM = 3257839
# We want to seamlessy run our API both locally and on Heroku. If running on
# Heroku, sensible DB connection settings are stored in environment variables.
MONGO_URI = os.environ.get('MONGODB_URI', 'mongodb://172.18.0.3/')
MONGO_DBNAME = 'eve'

###############################
### Synpat settings       #####
###############################
SYNPAT_CONF = {
'SMARTCONTRACT' :'',
'STEEM_TAG'      : 'testsynergis',
'STEEM_SYNPAT_AUTHOR':'maxsiz',
'STEEM_POSTING_PK' :'5Kb1scKxP5cP4bujsPmL6z5YnRfEkMwWA1JidvV9DeddKRVPMhr',
'STEEM_ACTIVE_PK' :'5KWKj7TVQwnzk4awfAFEqfk9q54mUJDN8ycKLUqgCJREy6EZcTP'
}

if __name__ == '__main__':
    from web3 import Web3, HTTPProvider, IPCProvider, WebsocketProvider
    #web3 provider initializing
    if ('http:'.upper() in WEB3_PROVIDER.upper() or
        'https:'.upper() in WEB3_PROVIDER.upper()):
        w3 = Web3(HTTPProvider(WEB3_PROVIDER))
    elif ('ws:'.upper() in WEB3_PROVIDER.upper() or
         'wss:'.upper() in WEB3_PROVIDER.upper()):
        w3 = Web3(Web3.WebsocketProvider(WEB3_PROVIDER))    
    else:
        w3 = Web3(IPCProvider(WEB3_PROVIDER))
    print('w3.eth.blockNumber=' + str(w3.eth.blockNumber))
    print(MONGO_URI)

    # #Need some injection on Rinkeby and -dev networks  - not work with infura
    # if  w3.admin.nodeInfo['protocols']['eth']['network'] == 4:
    #     from web3.middleware import geth_poa_middleware
    #     w3.middleware_stack.inject(geth_poa_middleware, layer=0)

