# -*- coding: utf-8 -*-
import os
import json
##########################
##########################
## COMMON service settings
##########################
ENVIRON          = os.environ.get('ENVIRON','TEST')
#Some common params (secret)
MONGO_URI        = os.environ.get('MONGODB_URI', 'mongodb://172.18.0.3/')
WEB3_PROVIDER    = os.environ.get('WEB3_PROVIDER','wss://rinkeby.infura.io/ws/v3/22238a03c4ce4f6e9b2a3e0e899a77e6')
PK_OPERATOR      = os.environ.get('PK_OPERATOR','384D9719F2CDFA068A58811541AA1A6059306A4AE61A0A360EE6443D3F610977')
STEEM_POSTING_PK = os.environ.get('STEEM_POSTING_PK','5Kb1scKxP5cP4bujsPmL6z5YnRfEkMwWA1JidvV9DeddKRVPMhr')
STEEM_ACTIVE_PK  = os.environ.get('STEEM_ACTIVE_PK','5KWKj7TVQwnzk4awfAFEqfk9q54mUJDN8ycKLUqgCJREy6EZcTP')

if  ENVIRON == 'TEST' :
    WEB3_NETWORK = 4
    #ADDRESS_SYNPATREGISTER = '0x128CB817Be464DE1df828FB1f44B4d28C7E7e1d8'
    ADDRESS_SYNPATREGISTER = '0xC40E4F272Cf6E37B28eeC0F3E0128e73C6627A80'
    ADDRESS_OPERATOR = '0xafB42ffDC859f82eDb3E93680F95212200f0CCA1'
    STEEM_TAG = 'testsynergis'
    STEEM_SYNPAT_AUTHOR = 'maxsiz'
else: #PROD settings
    WEB3_NETWORK = 1
    ADDRESS_SYNPATREGISTER = ''
    ADDRESS_OPERATOR = ''
    STEEM_TAG = 'synpat'
    STEEM_SYNPAT_AUTHOR = 'maxsiz'

# contracts ABI (!!!!! true->True, false ->False    - Python style)
ABI_SYNPATREGISTER = json.loads('[{"constant":true,"inputs":[{"name":"_hashinput","type":"string"}],"name":"calculateSha3","outputs":[{"name":"","type":"bytes32"}],"payable":false,"stateMutability":"pure","type":"function"},{"constant":false,"inputs":[],"name":"kill","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[{"name":"","type":"bytes32"}],"name":"permlinkSaved","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"version","outputs":[{"name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"owner","outputs":[{"name":"","type":"address"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"_permlink","type":"string"},{"name":"_hashSha","type":"bytes32"}],"name":"writeSha3","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"pendingOwner","outputs":[{"name":"","type":"address"}],"payable":false,"stateMutability":"view","type":"function"},{"payable":false,"stateMutability":"nonpayable","type":"fallback"},{"anonymous":false,"inputs":[{"indexed":true,"name":"permlinkSaved_permlink","type":"string"},{"indexed":false,"name":"_hashSha","type":"bytes32"}],"name":"SynpatRecord","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"name":"previousOwner","type":"address"},{"indexed":true,"name":"newOwner","type":"address"}],"name":"OwnershipTransferred","type":"event"}]')
##############################
## End of COMMON settings
##############################
##############################
#New infura
#https://rinkeby.infura.io/v3/22238a03c4ce4f6e9b2a3e0e899a77e6
#https://mainnet.infura.io/v3/22238a03c4ce4f6e9b2a3e0e899a77e6

#w3 = Web3(HTTPProvider('https://mainnet.infura.io/5i7ovfspYawMeU8Ik0Q4')) 
#MainNet infuraw3 = Web3(HTTPProvider('https://rinkeby.infura.io/5i7ovfspYawMeU8Ik0Q4')) #Rinkeby infurra
#w3 = Web3(HTTPProvider('http://127.0.0.1:8545'))
#w3 = Web3(Web3.WebsocketProvider("ws://172.31.21.15:8546"))
#


#MONGO_DBNAME = 'eve'


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
    print('====================> MONGO_URI:'+str(MONGO_URI))

    # #Need some injection on Rinkeby and -dev networks  - not work with infura
    # if  w3.admin.nodeInfo['protocols']['eth']['network'] == 4:
    #     from web3.middleware import geth_poa_middleware
    #     w3.middleware_stack.inject(geth_poa_middleware, layer=0)

