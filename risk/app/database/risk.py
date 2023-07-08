from ..database.models.http_responses import *
from ..database.init import client
from ..constants import MONGO


# pymongo connecting to mongoDB
risks = client[MONGO["DATABASE"]]["risks"]

def get_risk(domain: str):
    try:
        return risks.find_one( { "domain": domain }, { "_id": 0 } )
    except Exception as e:
        print(e)
        return None
