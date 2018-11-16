
### Snipets
```python
event_signature_hash = web3.sha3(text="eventName(uint32)").hex()
event_filter = web3.eth.filter({
    "address": myContract_address,
    "topics": [event_signature_hash,
               "0x000000000000000000000000000000000000000000000000000000000000000a"],
    })
```

### Usefull links
https://api.mongodb.com/python/current/tutorial.html  
https://docs.mongodb.com/manual/reference/operator/update/addToSet/  
https://docs.mongodb.com/manual/reference/operator/aggregation/toUpper/  
