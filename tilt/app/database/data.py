import re

from .init import client

# pymongo connecting to mongoDB
documents = client["data"]["tilts"]

def insert_tilt(tilt):
    if documents.find_one({ "meta": { "url": tilt["meta"]["url"] } }) is None:
        return documents.insert_one(tilt).acknowledged
    return documents.update_one({ "meta": { "url": tilt["meta"]["url"] } }, tilt).acknowledged

def insert_tilts(tilts):
    for tilt in tilts:
        if documents.find_one({ "meta": { "url": tilt["meta"]["url"] } }) is None:
            if not documents.insert_one(tilt).acknowledged:
                return False
        else:
            if not documents.update_one({ "meta": { "url": tilt["meta"]["url"] } }, tilt).acknowledged:
                return False
    return True

def delete_tilt(domain):
    return documents.delete_one({ "meta.url": re.compile("^" + domain + "$|^" + domain + "/|/" +
            domain + "$|\." + domain + "$|/" + domain + "/|\." + domain + "/") }).acknowledged

def delete_tilts(domains):
    for domain in domains:
       if not documents.delete_one({ "meta.url": re.compile("^" + domain + "$|^" + domain + "/|/" +
            domain + "$|\." + domain + "$|/" + domain + "/|\." + domain + "/") }).acknowledged:
                return False
    return True
