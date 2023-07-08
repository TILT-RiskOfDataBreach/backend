from tld import get_fld
import pymongo
import os

mode = os.environ['MODE'] if 'MODE' in os.environ else 'HOST'

MONGO = {
    'DATABASE': 'data',
    'HOST': 'localhost',
    'DOCKER': 'mongo',
    'PORT': 27017,
    'USERNAME': 'root',
    'PASSWORD': 'SuperSecret',
    'AUTHENTICATION_SOURCE': 'admin'
}

client = pymongo.MongoClient(
    host=MONGO[mode],
    port=MONGO['PORT'],
    username=MONGO['USERNAME'],
    password=MONGO['PASSWORD']
)
risks = client[MONGO["DATABASE"]]["risks"]

domain = "amazon.com"

risk = risks.find_one( { "domain": domain }, { "_id": 0 } )

print(risk)
