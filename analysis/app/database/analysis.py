from tld import get_fld

from .init import client
from ..helpers.network_utils import GraphOps, GraphDataScience
from ..helpers.tilt_utils import TILTOps

# pymongo connecting to mongoDB
risks = client["data"]["risks"]


def update():
    cursor = TILTOps().all_TILTs()

    def multiUpdate(doc):
        changes = False
        
        doc["meta"]["url"] = get_fld(doc["meta"]["url"])
        nodeData = TILTOps().node_data(doc)
        if GraphOps.get_node(doc["meta"]["url"]) is None:
            changes = GraphOps.create_node(nodeData[0])
        for recipient in nodeData[1]:
            if GraphOps.get_node(recipient) is None:
                changes = GraphOps.create_node(recipient)
            if GraphOps.get_relationship([doc["meta"]["url"], recipient[0]]) is None:
                changes = GraphOps.create_relationship([doc["meta"]["url"], recipient[0]])

        return changes

    changes = False
    for doc in cursor:
        if multiUpdate(doc):
            changes = True

    if changes:
        __calculate_measures()
        
    __calculate_risks()

def __calculate_measures():
    GraphDataScience.write_louvain()
    cluster = GraphDataScience.distinct_louvain_cluster()
    for c in cluster:
        print(c)
        GraphDataScience.write_article_rank_cluster(c["cluster"])
        GraphDataScience.write_betweenness_cluster(c["cluster"])
        GraphDataScience.write_degree_cluster(c["cluster"])
        GraphDataScience.write_harmonic_closeness_cluster(c["cluster"])

def __calculate_risks():
    domains = GraphDataScience.get_domains()
        
    for domain in domains:
        if risks.find_one( { "domain": domain["domain"] } ) is None:
            risks.insert_one(GraphDataScience.similarity_probability(domain["domain"]))
