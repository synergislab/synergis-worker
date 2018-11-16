# -*- coding: utf-8 -*-
import logging
import os
import json
from web3 import Web3, HTTPProvider, IPCProvider, WebsocketProvider
import time
import settings
import pymongo

def handle_event_Confirm(event):
    """
    This function searce wallet from event  in DB  and  mark it as confirmed
    if time of incoming event more then request time
    """
    logging.info('*****ConfirmEvent handler***')
    logging.debug(event)
    logging.info(event['topics'][1].hex()[-40:])
    logging.info(w3.toInt(hexstr=event['data']))
    logging.info(event['transactionHash'].hex())
    c = wallets.count_documents({'addr':'0x'+str(event['topics'][1].hex()[-40:])}
        #for caseIncentive searche
        ,collation=pymongo.collation.Collation(locale='en_US', caseLevel=False, strength=1)
    )
    logging.debug(str(c)+ ' address found')
    if  c > 0:
        wallets.find_one_and_update(
            {'addr':'0x'+str(event['topics'][1].hex()[-40:])},#filter
            {'$set': { 
                'status': 'confirmed', 
                'status_date': int(time.time())
             },
             '$addToSet':{'confirmation':{
                            'txHash' : event['transactionHash'].hex(),
                            'logdate': w3.toInt(hexstr=event['data']),
                            'param': 'reserved'
                        }
             }
            }
            #for caseIncentive searche
            ,collation=pymongo.collation.Collation(locale='en_US', caseLevel=False, strength=1)
        )    
    else:
        pass    



def handle_event_SimpleEvent(event):
    """
    This is test event handler
    """
    logging.info('*****SimpleEvent handler***')
    logging.debug(event)

def handle_event_Transfer(event):
    """
    ERC20 event handler function: Transfer
    If one of address from event topics present in db accounts
    collection 
    then records to incoming/outcoming will be added
    """ 
    ###########################################
    ###########################################
    def acc_aggregate_balance(_acc):
        """
        Internal function for balance recalc
        """
        r=accounts.aggregate(
                [
                    {"$match" : {"name": _acc}},
                    {"$match"  : 
                        {"$or":
                            [
                                {"incomings":{"$exists":"true"}},
                                {"outcomings":{"$exists":"true"}}
                            ]
                        }
                    },
                    {"$project"  : 
                        {
                            "_id":0, "name":1,"units":1, 
                            "incoming_amount":{"$sum":"$incomings.amount"},
                            "outcoming_amount":{"$sum":"$outcomings.amount"}
                        }
                    },
                    {"$project"  :
                        {
                            "name":1,"units":1, 
                            "incoming_amount":1,
                            "outcoming_amount":1,
                            "balance":{"$add":["$incoming_amount","$outcoming_amount"]}
                        }
                    }
                ]
        )
        for doc in r:
            logging.debug('=======Aggregatio result')
            logging.debug(doc)
            return doc['balance']

    def acc_make_record(_acc, _amount, _flow):
        """
        Internal function for make incoming/outcoming record for account
        """ 
        logging.debug('acc_make_record**')
        trans_dict = {
            'txHash'  : event['transactionHash'].hex(),
            'logdate' : _logdate,
            'amount'  : _amount
        }
        if  _flow == 'outcomings':
            trans_dict['amount'] = -_amount
        r = accounts.update_one(
            {'name': _acc }, #filter
            {
                '$addToSet':{_flow: trans_dict}
            }
        )
        #Full balance recalc
        r = accounts.update_one(
            {'name': _acc }, #filter
            {
                '$set':{ 'balance': acc_aggregate_balance(_acc)},
            }
        )

    ###############################################
    ###############################################
    logging.debug(event)
    logging.info('*****TransferEvent handler***, from=' 
        + str(event['args']['from'])
        + ', to ='+ str(event['args']['to'])
        + ', value='+ str(event['args']['value'])
    )
    _from = str(event['args']['from'])
    _to   = str(event['args']['to'])
    _amount =  float(w3.fromWei(event['args']['value'], 'ether'))

    _logdate = w3.eth.getBlock(event['blockNumber'])['timestamp']
    #_logdate = event['blockNumber']
    # Each address from event may be debet or/and credit
    # Outcome
    if  _from in auto_tracked_accounts :
        acc_make_record(_from, _amount, _flow='outcomings')
        #If _to address have  account in exosettlement system
        # we need make second part of our "double enrty" - big
        # respect to Luca Pacioli
        r = accounts.count_documents({'name': _to, 'acc_type': 'deposit'})
        logging.debug('Check deposit list')
        logging.debug(r)
        if  r != 0:
            #Becouse deposit - "passiv" acc
            acc_make_record(_to, _amount, _flow='outcomings')
    # Income
    if  _to in auto_tracked_accounts :
        acc_make_record(_to, _amount, _flow='incomings')
        #If _from address have  account in exosettlement system
        # we need make second part of our "double enrty" - big
        # respect to Luca Pacioli
        r = accounts.count_documents({'name': _from, 'acc_type': 'deposit'})
        logging.debug('Check deposit list')
        logging.debug(r)
        if  r != 0:
            #Becouse deposit - "passiv" acc
            acc_make_record(_from, _amount, _flow='incomings')
        
    
def handler_operation_connect(_op):
    """
    Execute smart contract method for token distribution
    """
    logging.debug(_op['_id'])
    logging.debug(_op['params']['acc'])
    #Check for params
    if  (w3.isAddress(_op['params']['content_provider_acc']) 
        and _op['params']['amount'] != 0
        ) :
        #Lets Unlock account, from which we exec transaction
        w3.personal.unlockAccount(settings.ADDRESS_OPERATOR, settings.PASSW_OPERATOR)
        # Go!!
        txHash = proofOfConnect.functions.connected(_op['params']['content_provider_acc'], 
             w3.toWei(abs(_op['params']['amount']),'ether') # ether - beaouse EXO decimals=18
        ).transact({'gas':70000})
        w3.personal.lockAccount(settings.ADDRESS_OPERATOR)
        logging.debug(txHash.hex())
        txn_receipt = w3.eth.waitForTransactionReceipt(txHash)
        logging.debug(txn_receipt)
        if  txn_receipt['status'] != 0 :
            res = operations.update_one(
                {'_id':_op['_id']},
                {'$set': 
                    {
                        'params.txHash':txHash.hex(),
                        'opstate':'finished'
                    },
                }
            )
            logging.debug(res)



def log_loop(event_filter, poll_interval):
    """
    Main loop for events from ExoRegister smartcontract
    """
    while True:
        #w3 events from smart contracts ("w3.eth.filter" type )
        for event in event_filter[0].get_new_entries():
            #handler selector
            if  event['topics'][0] == w3.sha3(text='Confirm(address,uint64)'):
                handle_event_Confirm(event)
            elif event['topics'][0] == w3.sha3(text='SimpleEvent(address,uint64)'):
                handle_event_SimpleEvent(event)
        
        #w3 events from smart contracts (!!!!another filter type)
        for event in event_filter[1].get_new_entries():
            handle_event_Transfer(event)
        
        #new ops for web3 processing
        op = operations.find_one({'opstate':'new', 'auto': True});
        #logging.info(str(len(ops)) + ' new operations found')
        logging.debug(op)
        if  op is not None:
            #operations handler selector
            if  op['optype']=='connect':
                handler_operation_connect(op)
        time.sleep(poll_interval)

def main():
    #Define filters and start loop
    Exoreg_filter = w3.eth.filter(
         {
         "address": settings.ADDRESS_EXOREGISTER,
        }
    )

    # Exotoken_filter = w3.eth.filter(
    #      {
    #      "address": settings.ADDRESS_EXOTOKEN,
    #      "fromBlock":3257839
    #     }
    # )

    Exotoken_filter = token.events.Transfer.createFilter(
        fromBlock=settings.START_FROM
    )


    filters = [
        Exoreg_filter,
        Exotoken_filter
    ]
    #log_loop(Exoreg_filter, 12)
    # in case starting from the   past (blocNumber)
    if  settings.START_FROM != 'latest' :
        for event in filters[0].get_all_entries():
            #handler selector
            if  event['topics'][0] == w3.sha3(text='Confirm(address,uint64)'):
                handle_event_Confirm(event)
        
        for event in filters[1].get_all_entries():
            handle_event_Transfer(event)

    log_loop(filters, 12)
####################################################################
####################################################################

####################################################################
####################################################################
####################################################################
####################################################################
####################################################################
####################################################################

########################################
###  Module initialize section      ####
########################################
logging.basicConfig(format='%(asctime)s->%(levelname)s:[in %(filename)s:%(lineno)d]:%(message)s'
    , level=int(os.environ.get('EXO_LOGLEVEL',logging.DEBUG))
)

#txSenderAddress = '0x86C3582b6505CcB8faDAcb211fC1E5a8fDD26E91' #ExoACCICO
#web3 provider initializing
if 'http:'.upper() in settings.WEB3_PROVIDER.upper():
    w3 = Web3(HTTPProvider(settings.WEB3_PROVIDER))
elif 'ws:'.upper() in settings.WEB3_PROVIDER.upper():
    w3 = Web3(Web3.WebsocketProvider(settings.WEB3_PROVIDER))    
else:
    w3 = Web3(IPCProvider(settings.WEB3_PROVIDER))
logging.info('w3.eth.blockNumber=' + str(w3.eth.blockNumber))
w3.eth.defaultAccount  = settings.ADDRESS_OPERATOR

#Need some injection on Rinkeby and -dev networks
if  w3.admin.nodeInfo['protocols']['eth']['network'] == 4:
    from web3.middleware import geth_poa_middleware
    w3.middleware_stack.inject(geth_poa_middleware, layer=0)

proofOfConnect = w3.eth.contract(address=settings.ADDRESS_EXOPROOFOFCONNECT,
    abi=settings.ABI_EXOPROOFOFCONNECT
)

token = w3.eth.contract(address=settings.ADDRESS_EXOTOKEN,
    abi=settings.ABI_EXOTOKEN
)

auto_tracked_accounts = [settings.ADDRESS_EXOPROOFOFCONNECT]


#mongoDB initializing
mongo_client = pymongo.MongoClient(settings.MONGO_URI)
db = mongo_client.settle
wallets  = db.wallets
accounts = db.accounts
operations = db.operations


#logging.debug(proofOfConnect.functions.version().call())
###########################################
if __name__ == '__main__':
    main()