# -*- coding: utf-8 -*-
import logging
import os
import sys
import json
from web3 import Web3, HTTPProvider, IPCProvider, WebsocketProvider
import time
import settings
import pymongo
import steem
from steembase.exceptions import RPCError, RPCErrorRecoverable, PostOnlyEvery5Min
    
def handler_post_write(_p):
    """
    Write post to steem.  Returns tuple(boolean, [<obj>|str])
    """
    logging.debug(_p)
    global last_steem_write
    try:
        r = client.commit.post(
            title=_p.get('steemtitle','Synpat service article'), 
            body=_p.get('steembody','This is a place for some ideas'), 
            author=settings.STEEM_SYNPAT_AUTHOR, 
            #author='mstest',
            tags=[settings.STEEM_TAG]+_p.get('steemtags',[]), 
            permlink=_p.get('steempermlink', None),
            community = 'Synergis',
            json_metadata ={
                'eth':_p.get('ethaddr',settings.ADDRESS_OPERATOR),
                'app':'synpat'
            } 
        )
    except  PostOnlyEvery5Min as e :
        # This  part not  work on dev moment(20181121)
        # In fact there is RPCError occur when write interval too shot
        #Need inc poll intervall
        #poll_interval = 300
        logging.debug(e.args)
        logging.debug(r)
        logging.debug('Poll interval increased')
        res = (False, 'PostOnlyEvery5Min')
        last_steem_write = int(time.time())
    except  :
        logging.debug('All other error')  
        logging.debug(sys.exc_info()[0:2])
        res = (False, str(sys.exc_info()[1]))
        last_steem_write = int(time.time())
    else:
        #Write -OK, that why we may decrease poll interval to default value
        last_steem_write = int(time.time())
        logging.debug('last_steem_write set to '+ str(last_steem_write))
        #poll_interval = 12
        logging.debug(r)
        res = (True, r)
    return res

def log_loop(event_filter=[]):
    """
    Main loop 
    """
    while True:
        try:
            logging.info('w3.eth.blockNumber=' + str(w3.eth.blockNumber))
            ##################################        
            ##################################
            #w3 events from smart contracts ("w3.eth.filter" type )
            # for event in event_filter[0].get_new_entries():
            #     #handler selector
            #     if  event['topics'][0] == w3.sha3(text='Confirm(address,uint64)'):
            #         handle_event_Confirm(event)
            #     elif event['topics'][0] == w3.sha3(text='SimpleEvent(address,uint64)'):
            #         handle_event_SimpleEvent(event)
            
            # #w3 events from smart contracts (!!!!another filter type)
            # for event in event_filter[1].get_new_entries():
            #     handle_event_Transfer(event)
            
            ##################################        
            ##################################
            #new posts for steem processing
            write_interval = int(time.time())-last_steem_write
            logging.debug('write_interval='+ str(write_interval))
            if  write_interval > 300:
                p = posts.find_one({'state':'new'});
                logging.debug(p)
                if  p is not None:
                    r = handler_post_write(p)
                    if  r[0]:
                        #Let`s update db record with status and some fields
                        res = posts.update_one(
                            {'_id':p['_id']},
                            {'$set': 
                                {
                                    'steempermlink':r[1]['operations'][0][1]['permlink'],
                                    'steemauthor'  :r[1]['operations'][0][1]['author'],
                                    'steemtitle'   :r[1]['operations'][0][1]['title'],
                                    'steembody'    :r[1]['operations'][0][1]['body'],
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
            ##################################        
            ##################################
            #new posts for Ethereum processing        
            p = posts.find_one(
                {'state':'steemed', 
                 #'ethaddr': settings.ADDRESS_OPERATOR
                }
            )
            logging.debug('********Ethereum operations start')
            logging.debug(p)
            if  p is not None:
                #Let`s get steem post from steem blockchain
                steem_post = client.get_content(p['steemauthor'], p['steempermlink'])
                #Check existing of steem post
                if  steem_post['id'] != 0 :
                    logging.debug('**Post from steem:')
                    logging.debug(steem_post)
                    nonce=w3.eth.getTransactionCount(eval(steem_post['json_metadata'])['eth'])
                    logging.debug(nonce)
                    #Now  let`s save post hash in Ethereum blockchain
                    #First build transaction
                    tx = synpatregister.functions.writeSha3(
                        steem_post['url'], #/category/@author/permlink
                        w3.soliditySha3(
                            ['string', 'string'], 
                            [steem_post['title'],steem_post['body']]
                        )
                    ).buildTransaction(
                        {
                            ###########################
                            #  !!!! Check Params below 
                            ###########################
                             'chainId': settings.WEB3_NETWORK,
                             'gasPrice': w3.toWei('16', 'gwei'),
                            ########################### 
                             'nonce': nonce,
                        }
                    )
                    logging.debug('*****Tx ready for sign***')
                    logging.debug(tx)
                    #Save tx to db  for next sign
                    res = posts.update_one(
                        {'_id':p['_id']},
                        {
                            '$set':{
                                'state'  :'readyForSign',
                                'ethaddr': eval(steem_post['json_metadata'])['eth'],
                                'txForSign': tx
                            },
                        }
                    )
                    logging.debug('db updated with tx and readyForSign state')
                    logging.debug(res)
                    #If eth address from post match to settings.ADDRESS_OPERATOR
                    # - sign and send tx
                    if  (eval(steem_post['json_metadata'])['eth'] 
                         == settings.ADDRESS_OPERATOR
                        ):
                        signed = w3.eth.account.signTransaction(tx, settings.PK_OPERATOR)
                        logging.debug('*signed tx:')
                        logging.debug(signed)
                        res = posts.update_one(
                            {'_id':p['_id']},
                            {
                                '$set':{
                                    'state'  :'ethSigned',
                                },
                                '$addToSet':{
                                    'blockchainplus' :{'txHash': signed.hash.hex()},
                                },
                            }
                        )
                        #sending
                        r = w3.eth.sendRawTransaction(signed.rawTransaction)
                        logging.debug('*Rawtx sended:')
                        logging.debug(r)
                        if  r == signed.hash :
                            res = posts.update_one(
                                {'_id':p['_id']},
                                {
                                    '$set':{
                                        'state'  :'ethPending',
                                        'txForSign': None
                                    },
                                }
                            )
            ###########################################        
            ###########################################
            #new posts for check tx status in Ethereum        
            p = posts.find_one(
                {'state':'ethPending'}
            )
            logging.debug('********Posts for check tx status in Ethereum (in ethPending)')
            logging.debug(p)
            if  p is not None:
                #check last txHash
                r = w3.eth.getTransactionReceipt(p['blockchainplus'][-1:][0]['txHash'])
                logging.debug('Tx Receipt')
                logging.debug(r)
                if  r is not None :
                    #Update status from Receipt
                    if  r['status'] != 0 :
                        tx_state = 'Success'
                    else:
                        tx_state = 'Failure'
                        #tx Fail
                    res = posts.update_one(
                                {
                                        '_id':p['_id'], 'blockchainplus.txHash':r['transactionHash'].hex()
                                        #{'blockchainplus':{'$elemMatch':{'txHash':r['transactionHash']}}}
                                },
                                {
                                    '$set':{
                                        'state'  :tx_state,
                                        'blockchainplus.$.blockNumber': r['blockNumber'],
                                    },
                                    
                                },
                                # {
                                #       'arrayFilters': [ { "elem.txHash": r['transactionHash'].hex()}],
                                #       'upsert': False
                                # }
                            )
        except Exception as e:
            logging.info(e)
            res = posts.update_one(
                {'_id':p['_id']},
                {'$set':{'state'  :'error'}}
            )


        time.sleep(poll_interval)

def main():
    log_loop()
    
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
#
#    !!!!!TODO try/except
#
try:
    logging.info('w3.eth.blockNumber=' + str(w3.eth.blockNumber))
    w3.eth.defaultAccount  = settings.ADDRESS_OPERATOR
except Exception as e:
    logging.info('!!!!! w3.eth.blockNumber ERROR')   


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
    keys=[settings.STEEM_POSTING_PK , settings.STEEM_ACTIVE_PK]
)
try:
    logging.debug('************Steem init check...')
    logging.debug('STEEM_POSTING_PK like = ' + settings.STEEM_POSTING_PK[:7]+'...')
    logging.debug('STEEM_POSTING_PK like = ' + settings.STEEM_ACTIVE_PK[:7]+'...')
    r = client.get_content('menaskop', 'fixedpermlink')
    logging.debug(r)
except Exception as e:
    logging.debug(e)


poll_interval = 12
last_steem_write = 0

#logging.debug(proofOfConnect.functions.version().call())
###########################################
if __name__ == '__main__':
    main()