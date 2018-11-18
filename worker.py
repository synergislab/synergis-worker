# -*- coding: utf-8 -*-
import logging
import os
import sys
import json
from web3 import Web3, HTTPProvider, IPCProvider, WebsocketProvider
import time
import settings
import pymongo
from settings import SYNPAT_CONF
import steem
from steembase.exceptions import RPCError, RPCErrorRecoverable, PostOnlyEvery5Min
def handle_event_Confirm(event):
    """
    This function searce wallet from event  in DB  and  mark it as confirmed
    if time of incoming event more then request time
    """
    logging.info('*****ConfirmEvent handler***')
    logging.debug(event)
    # logging.info(event['topics'][1].hex()[-40:])
    # logging.info(w3.toInt(hexstr=event['data']))
    # logging.info(event['transactionHash'].hex())
    # c = wallets.count_documents({'addr':'0x'+str(event['topics'][1].hex()[-40:])}
    #     #for caseIncentive searche
    #     ,collation=pymongo.collation.Collation(locale='en_US', caseLevel=False, strength=1)
    # )
    # logging.debug(str(c)+ ' address found')
    # if  c > 0:
    #     wallets.find_one_and_update(
    #         {'addr':'0x'+str(event['topics'][1].hex()[-40:])},#filter
    #         {'$set': { 
    #             'status': 'confirmed', 
    #             'status_date': int(time.time())
    #          },
    #          '$addToSet':{'confirmation':{
    #                         'txHash' : event['transactionHash'].hex(),
    #                         'logdate': w3.toInt(hexstr=event['data']),
    #                         'param': 'reserved'
    #                     }
    #          }
    #         }
    #         #for caseIncentive searche
    #         ,collation=pymongo.collation.Collation(locale='en_US', caseLevel=False, strength=1)
    #     )    
    # else:
    #     pass    



def handle_event_SimpleEvent(event):
    """
    This is test event handler
    """
    logging.info('*****SimpleEvent handler***')
    logging.debug(event)

        
    
def handler_post_write(_p):
    """
    Write post to steem.  Returns tuple(boolean, [<obj>|str])
    """
    logging.debug(_p)
    try:
        r = client.commit.post(
            title=_p.get('steemtitle','Synpat service article'), 
            body=_p.get('steembody','This is a place for some ideas'), 
            author=SYNPAT_CONF['STEEM_SYNPAT_AUTHOR'], 
            #author='mstest',
            tags=[SYNPAT_CONF['STEEM_TAG']]+_p.get('steemtags',[]), 
            permlink=_p.get('steempermlink', None),
            community = 'synergislab_community',
            json_metadata ={
                'eth':_p.get('ethaddr',settings.ADDRESS_OPERATOR),
                'app':'synpat'
            } 
        )
    except  PostOnlyEvery5Min as e :
        #Need inc poll intervall
        poll_interval = 300
        logging.debug(e.args)
        logging.debug(r)
        logging.debug('Poll interval increased')
        res = (False, 'PostOnlyEvery5Min')
    except  :
        logging.debug('All other error')  
        logging.debug(sys.exc_info()[0:2])
        res = (False, str(sys.exc_info()[1]))
    else:
        #Write -OK, that why we may decrease poll interval to default value
        poll_interval = 12
        logging.debug(r)
        res = (True, r)
    return res

    #Check for params
    # if  (w3.isAddress(_op['params']['content_provider_acc']) 
    #     and _op['params']['amount'] != 0
    #     ) :
    #     #Lets Unlock account, from which we exec transaction
    #     w3.personal.unlockAccount(settings.ADDRESS_OPERATOR, settings.PASSW_OPERATOR)
    #     # Go!!
    #     txHash = proofOfConnect.functions.connected(_op['params']['content_provider_acc'], 
    #          w3.toWei(abs(_op['params']['amount']),'ether') # ether - beaouse EXO decimals=18
    #     ).transact({'gas':70000})
    #     w3.personal.lockAccount(settings.ADDRESS_OPERATOR)
    #     logging.debug(txHash.hex())
    #     txn_receipt = w3.eth.waitForTransactionReceipt(txHash)
    #     logging.debug(txn_receipt)
    #     if  txn_receipt['status'] != 0 :
    #         res = operations.update_one(
    #             {'_id':_op['_id']},
    #             {'$set': 
    #                 {
    #                     'params.txHash':txHash.hex(),
    #                     'opstate':'finished'
    #                 },
    #             }
    #         )
    #         logging.debug(res)

# def write_to_steem(_items):
#     """
#     write post to steem block and update record status in db
#     """
#     logging.debug('write_to_steem')
#     logging.debug(_items)
#     title = 'Post ' + str(time.time())
#     body = 'Новость'
#     #author = 'mstest'
#     author = 'maxsiz'
#     taglist = ['synergislab', 'te']
#     permlink = 'fixedpermlink4'
#     community = 'synergislab_community'
#     r = client.commit.post(title=title, body=body, author=author, tags=taglist, 
#         permlink=permlink, 
#          community = community,
#          json_metadata ={'eth':'0x1234567897845462313'} 
#     )


def log_loop(event_filter):
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
        
        # #w3 events from smart contracts (!!!!another filter type)
        # for event in event_filter[1].get_new_entries():
        #     handle_event_Transfer(event)
        
        #new posts for steem processing
        p = posts.find_one({'state':'new'});
        logging.debug(p)
        if  p is not None:
            #operations handler selector
            #if  p['optype']=='connect':
            r = handler_post_write(p)
            if  r[0]:
                #Let`s update db record with status and some fields
                res = posts.update_one(
                    {'_id':p['_id']},
                    {'$set': 
                        {
                            'steempermlink':r[1]['operations'][0][1]['permlink'],
                            'steemauthor'  :r[1]['operations'][0][1]['author'],
                            'state':'steemed'
                        },
                    }
                )
                logging.debug('db update with permlink')
                logging.debug(str(res))
            else:
                res = posts.update_one(
                    {'_id':p['_id']},
                    {'$set': 
                        {
                            'state':r[1]
                        },
                    }
                )
                logging.debug('db update with err')
                logging.debug(str(res))

        #new posts for Ethereum processing        
        p = posts.find_one({'state':'steemed'});
        logging.debug('********Ethereum operations start')
        logging.debug(p)
        if  p is not None:
            #Now  let`s save post hash in Ethereum blockchain

            pass
        time.sleep(poll_interval)

def main():
    #Define filters and start loop
    Synpatreg_filter = w3.eth.filter(
         {
         "address": settings.ADDRESS_SYNPATREGISTER,
        }
    )


    # Exotoken_filter = synpatregister.events.Transfer.createFilter(
    #     fromBlock=settings.START_FROM
    # )


    filters = [
        #Exoreg_filter,
        Synpatreg_filter
    ]
    #log_loop(Exoreg_filter, 12)
    # in case starting from the   past (blocNumber)
    if  settings.START_FROM != 'latest' :
        for event in filters[0].get_all_entries():
            #handler selector
            if  event['topics'][0] == w3.sha3(text='Confirm(address,uint64)'):
                handle_event_Confirm(event)
        
        # for event in filters[1].get_all_entries():
        #     handle_event_Transfer(event)

    log_loop(filters)
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

#web3 provider initializing
if ('http:'.upper() in settings.WEB3_PROVIDER.upper() or
    'https:'.upper() in settings.WEB3_PROVIDER.upper()):
    w3 = Web3(HTTPProvider(settings.WEB3_PROVIDER))
elif ('ws:'.upper() in settings.WEB3_PROVIDER.upper() or
      'wss:'.upper() in settings.WEB3_PROVIDER.upper()):
    w3 = Web3(Web3.WebsocketProvider(settings.WEB3_PROVIDER))    
else:
    w3 = Web3(IPCProvider(settings.WEB3_PROVIDER))
logging.info('w3.eth.blockNumber=' + str(w3.eth.blockNumber))
w3.eth.defaultAccount  = settings.ADDRESS_OPERATOR

# #Need some injection on Rinkeby and -dev networks
# if  w3.admin.nodeInfo['protocols']['eth']['network'] == 4:
#     from web3.middleware import geth_poa_middleware
#     w3.middleware_stack.inject(geth_poa_middleware, layer=0)

synpatregister = w3.eth.contract(address=settings.ADDRESS_SYNPATREGISTER,
    abi=settings.ABI_SYNPATREGISTER
)


#mongoDB initializing
mongo_client = pymongo.MongoClient(settings.MONGO_URI)
db = mongo_client.eve
posts  = db.posts


#Steem initializing   
client = steem.Steem(no_broadcast=False,
    keys=[SYNPAT_CONF['STEEM_POSTING_PK'],SYNPAT_CONF['STEEM_ACTIVE_PK']]
)

poll_interval = 12

#logging.debug(proofOfConnect.functions.version().call())
###########################################
if __name__ == '__main__':
    main()