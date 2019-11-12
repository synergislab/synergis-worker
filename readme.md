# synpat service
https://steemit.com/steem-dev/@jesuscirino/steem-python-step-by-step-1-getting-started

https://github.com/steemit/steem-python
https://steem.readthedocs.io/en/latest/
https://developers.steem.io/
https://steem.esteem.ws/
#decode logs from tx receipt
https://codeburst.io/deep-dive-into-ethereum-logs-a8d2047c7371

r = client.get_discussions_by_created(
    {"tag":"synergislab",
    "limit":100, #number of posts
    #"tag":"synergislab" #tag of posts
    #"community": "synergislab_community"

    }

For connect to mongo container from host we need know ip in dockcer network
```bash
export MONGODB_URI='mongodb://'$(docker inspect --format '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' mongo)
```

```bash
http -v http://127.0.0.1:5000/synapi/V1/posts steemauthor=maxsiz steemtitle=Title_of_my_steemet_post steembody='This is a great service from clever people' ethaddr=0xa0363Cd6fC7A1BD68D2e330178B19eb6F7642F13 steemtags:='["wer","eth"]'
```

'body': 'Что означает community', 'json_metadata': '{"eth": "0x1234567897845462313", "community": "synergislab_community", "tags": ["synergislab", "te"]}',


{'ref_block_num': 16617, 'ref_block_prefix': 2653013870, 'expiration': '2018-11-18T09:22:28', 
'operations': [
    [
        'comment',
         {
            'parent_author': '', 
            'parent_permlink': 'testsynergis', 
            'author': 'maxsiz', 
            'permlink': 'title-of-my-steemet-post-2', 
            'title': 'Title_of_my_steemet_post 2', 
            'body': 'NotSoLongWordInEnglishLang', 
            'json_metadata': '{"eth": "0xa0363Cd6fC7A1BD68D2e330178B19eb6F7642F13", "app": "synpat", "community": "synergislab_community", "tags": ["testsynergis", "wer", "eth"]}'
         }
    ]
], 
'extensions': [], 
'signatures': ['1f68979c6474343940dc6bc1ee87abb06d4e410f22bbcfcd735e3c938e2988d5b32c3d86855248e9cbf9d89ef63a0681824a7b4f6f55611aa19988798629529a4a']
}

Smart on Rynkeby
https://rinkeby.etherscan.io/address/0x128cb817be464de1df828fb1f44b4d28c7e7e1d8#code

Smart on MainnEt
https://etherscan.io/address/0x2350b874d0eff523c5847223eb7144e1e56f06ce#code

20181222 refreskey

20191112 refreskey