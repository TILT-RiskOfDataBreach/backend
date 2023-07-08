import pymongo
import os

from ..constants import *

mode = os.environ['MODE'] if 'MODE' in os.environ else 'HOST'

# object class: tilt_operations
client = pymongo.MongoClient(
    host=MONGO[mode],
    port=MONGO['PORT'],
    username=MONGO['USERNAME'],
    password=MONGO['PASSWORD']
)
