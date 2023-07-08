from py2neo import Graph
from py2neo.matching import NodeMatcher

from ..constants import *

# non-object class: neo4j_requests
graph = Graph(NEO4J['DOCKER_URI'], auth=(NEO4J['Username'], NEO4J['Password']))

class GraphOps:

    # returns the first matching node to the given domain
    def get_node(domain):
        nodes = NodeMatcher(graph)
        return nodes.match("Domain", domain=domain).first()

    # returns the first matching relationship to the given relationship
    def get_relationship(relationship):
        a = GraphOps.get_node(relationship[0])
        b = GraphOps.get_node(relationship[1])
        return graph.relationships.match((a, b)).first()

    def get_child_nodes(parentDomain):
        query = 'MATCH (p:Domain)-[:SENDS_DATA_TO *]->(d:Domain) WHERE p.domain="' + parentDomain + '" WITH COLLECT (d) + p AS all UNWIND all as p MATCH (p)-[:SENDS_DATA_TO]->(d) RETURN DISTINCT d.domain'
        nodes = graph.run(query).data()

        childNodes = []
        visitedNodes = []
        for node in nodes:
            if node["d.domain"] not in visitedNodes:
                childNodes.append(node["d.domain"])
                visitedNodes.append(node["d.domain"])
        return childNodes

    # get subgraph
    def get_number_child_relationships(parentDomain):
        query = 'MATCH (p:Domain)-[:SENDS_DATA_TO *]->(d:Domain) WHERE p.domain="' + parentDomain + '" WITH COLLECT (d) + p AS all UNWIND all as p MATCH (p)-[:SENDS_DATA_TO]->(d) RETURN p.domain'
        nodes = graph.run(query).data()
        if nodes is None:
            return 0
        return len(nodes)

    def get_cluster(parentDomain):
        query = 'MATCH (p:Domain)-[:SENDS_DATA_TO *]->(d:Domain) WHERE p.domain="' + parentDomain + '" WITH COLLECT (d) + p AS all UNWIND all as p MATCH (p)-[:SENDS_DATA_TO]->(d) RETURN p.domain'
        data = graph.run(query).data()

        count = 0
        nodes = []
        for node in data:
            count += 1
            nodes.append(node["p.domain"])

        print(count)

    # creates a sharing network with createNode() and createRelationship()
    def create_sharing_network(properties, relationships):
        if(properties is not None and relationships is not None):
            for property in properties:
                GraphOps.create_node(property)

            for relationship in relationships:
                GraphOps.create_relationship(relationship)

    # creates a node in the default database of the Neo4j instance
    # {0: domain}, {1: country}, {2: numberOfBreaches}, {3: severityOfBreaches}, {4: dataTypeShared[]}, {5: marketCapitalization}, {6: industrialSector}
    def create_node(properties):
        if GraphOps.get_node(properties[0]) is None:
            graph.run('CREATE (n:Domain { domain: "' + str(properties[0]) + '", country: "' + str(properties[1]) + '", numberOfBreaches: "' + str(properties[2]) + '", severityOfBreaches: "' + str(properties[3]) + '", dataTypes: "' + str(properties[4]) + '", marketCapitalization: "' + str(properties[5]) + '", industrialSector: "' + str(properties[6]) + '" })')
            return True
        return False

    # creates a relationship in the default database of the Neo4j instance
    def create_relationship(relationship):
        if(GraphOps.get_relationship(relationship) is None):
            graph.run("MATCH (a:Domain), (b:Domain) WHERE a.domain = '" + str(relationship[0]) + "' AND b.domain = '" + str(relationship[1]) + "' CREATE (a)-[r:SENDS_DATA_TO]->(b)")
            return True
        return False

class GraphDataScience:

    def drop_database():
        graph.run("MATCH ()-[rel]->() DELETE rel")
        graph.run("MATCH (n) DELETE n")

    def remove_property(property):
        graph.run("MATCH (n) REMOVE n." + property)

    def count_nodes_cluster(cluster):
        return graph.run("MATCH (n {louvain: " + str(cluster) + "}) RETURN count(n) AS count").data()[0]["count"]

    def set_property_first(property, value):
        graph.run("MATCH (n) WHERE NOT EXISTS (n." + property + ") SET n." + property + " = '" + str(value) + "'")

    def set_property(property, value):
        graph.run("MATCH (n) SET n." + property + " = '" + str(value) + "'")

    def set_property_cluster(cluster, property, value):
        graph.run("MATCH (n {louvain: " + str(cluster) + "}) SET n." + property + " = '" + str(value) + "'")

    def distinct_louvain_cluster():
        return graph.run("MATCH (n:Domain) RETURN DISTINCT n.louvain AS cluster").data()

    def breached_domains():
        return graph.run("MATCH (n) WHERE n.numberOfBreaches>0 RETURN id(n)")

    def get_domains():
        return graph.run("MATCH (n) RETURN n.domain as domain").data()

    #Graph Data Science Stuff

    def __delete_graph(graph_name):
        graph.run("CALL gds.graph.drop('" + graph_name + "')")

    def __project_graph(graph_name, orientation):
        graph.run("CALL gds.graph.create('" + graph_name + "', 'Domain', {SENDS_DATA_TO: {orientation: '" + orientation + "'}})")

    def __project_louvain_graph(graph_name, cluster):
        graph.run("CALL gds.graph.create.cypher('" + graph_name + "', 'MATCH (n:Domain {louvain: " + str(cluster) + "}) RETURN id(n) as id', 'MATCH (n {louvain: " + str(cluster) + "})-[rel:SENDS_DATA_TO]->(m) WHERE m.louvain = " + str(cluster) + " RETURN id(n) AS source, id(m) AS target')")

    # depreciated by writeArticleRank
    def __write_page_rank():
        GraphDataScience.__project_graph("pageRankGraph", "REVERSE")
        graph.run("CALL gds.pageRank.write('pageRankGraph', {writeProperty: 'pageRank'})")
        GraphDataScience.__delete_graph("pageRankGraph")

    def write_article_rank():
        GraphDataScience.__project_graph("articleRankGraph", "REVERSE")
        try:
            graph.run("CALL gds.alpha.articleRank.write('articleRankGraph', {writeProperty: 'articleRank'})")
        except Exception as e:
            GraphDataScience.set_property("articleRank", 0)
            #print(e)
        GraphDataScience.__delete_graph("articleRankGraph")

    def write_article_rank_cluster(cluster):
        GraphDataScience.__project_louvain_graph("articleRankGraph", cluster)
        try:
            #graph.run("CALL gds.alpha.articleRank.write('articleRankGraph', {writeProperty: 'articleRank'})")
            graph.run("CALL gds.articleRank.write('articleRankGraph', {writeProperty: 'articleRank'})")
        except Exception as e:
            GraphDataScience.set_property_cluster(cluster, "articleRank", 0)
            print(e)
        GraphDataScience.__delete_graph("articleRankGraph")

    def __write_eigenvector():
        GraphDataScience.__project_graph("eigenvectorGraph", "REVERSE")
        graph.run("CALL gds.alpha.eigenvector.write('eigenvectorGraph', {writeProperty: 'eigenvector'})")
        GraphDataScience.__delete_graph("eigenvectorGraph")

    def __write_eigenvector_cluster(cluster):
        GraphDataScience.__project_louvain_graph("eigenvectorGraph", cluster)
        graph.run("CALL gds.alpha.eigenvector.write('eigenvectorGraph', {writeProperty: 'eigenvector'})")
        GraphDataScience.__delete_graph("eigenvectorGraph")

    def write_betweenness():
        GraphDataScience.__project_graph("betweennessGraph", "REVERSE")
        try:
            graph.run("CALL gds.betweenness.write('betweennessGraph', { writeProperty: 'betweenness' })")
        except Exception as e:
            GraphDataScience.set_property("betweenness", 0)
            #print(e)
        GraphDataScience.__delete_graph("betweennessGraph")

    def write_betweenness_cluster(cluster):
        GraphDataScience.__project_louvain_graph("betweennessGraph", cluster)
        try:
            graph.run("CALL gds.betweenness.write('betweennessGraph', { writeProperty: 'betweenness' })")
        except Exception as e:
            GraphDataScience.set_property_cluster(cluster, "betweenness", 0)
            print(e)
        GraphDataScience.__delete_graph("betweennessGraph")

    def write_degree():
        GraphDataScience.__project_graph("degreeGraph", "REVERSE")
        try:
            graph.run("CALL gds.alpha.degree.write('degreeGraph', { writeProperty: 'degree' })")
        except Exception as e:
            GraphDataScience.set_property("degree", 0)
            #print(e)
        GraphDataScience.__delete_graph("degreeGraph")

    def write_degree_cluster(cluster):
        GraphDataScience.__project_louvain_graph("degreeGraph", cluster)
        try:
            #graph.run("CALL gds.alpha.degree.write('degreeGraph', { writeProperty: 'degree' })")
            graph.run("CALL gds.degree.write('degreeGraph', { writeProperty: 'degree' })")
        except Exception as e:
            GraphDataScience.set_property_cluster(cluster, "degree", 0)
            print(e)
        GraphDataScience.__delete_graph("degreeGraph")

    # depreciated through writeHarmonicCloseness
    def __write_closeness():
        GraphDataScience.__project_graph("closenessGraph", "REVERSE")
        graph.run("CALL gds.alpha.closeness.write('closenessGraph', {writeProperty: 'closeness'})")
        GraphDataScience.__delete_graph("closenessGraph")

    # depreciated through writeHarmonicClosenessCluster
    def __write_closeness_cluster(cluster):
        GraphDataScience.__project_louvain_graph("closenessGraph", cluster)
        graph.run("CALL gds.alpha.closeness.write('closenessGraph', {writeProperty: 'closeness'})")
        GraphDataScience.__delete_graph("closenessGraph")

    def write_harmonic_closeness():
        GraphDataScience.__project_graph("harmonicClosenessGraph", "REVERSE")
        try:
            graph.run("CALL gds.alpha.closeness.harmonic.write('harmonicClosenessGraph', {writeProperty: 'harmonicCloseness'})")
        except Exception as e:
            GraphDataScience.set_property("harmonicCloseness", 0)
            #print(e)
        GraphDataScience.__delete_graph("harmonicClosenessGraph")

    def write_harmonic_closeness_cluster(cluster):
        GraphDataScience.__project_louvain_graph("harmonicClosenessGraph", cluster)
        try:
            graph.run("CALL gds.alpha.closeness.harmonic.write('harmonicClosenessGraph', {writeProperty: 'harmonicCloseness'})")
        except Exception as e:
            GraphDataScience.set_property_cluster(cluster, "harmonicCloseness", 0)
            print(e)
        GraphDataScience.__delete_graph("harmonicClosenessGraph")

    def write_louvain():
        GraphDataScience.__project_graph("louvainGraph", "REVERSE")
        graph.run("CALL gds.louvain.write('louvainGraph', {writeProperty: 'louvain'})")
        GraphDataScience.__delete_graph("louvainGraph")

    def write_label_propagation():
        GraphDataScience.__project_graph("labelPropagationGraph", "REVERSE")
        graph.run("CALL gds.labelPropagation.write('labelPropagationGraph', {writeProperty: 'labelPropagation'})")
        GraphDataScience.__delete_graph("labelPropagationGraph")

    def write_weakly_connected_components():
        GraphDataScience.__project_graph("weaklyConnectedComponentsGraph", "REVERSE")
        graph.run("CALL gds.wcc.write('weaklyConnectedComponentsGraph', {writeProperty: 'wcc'})")
        GraphDataScience.__delete_graph("weaklyConnectedComponentsGraph")

    def write_triangle_count():
        GraphDataScience.__project_graph("triangleCountGraph", "UNDIRECTED")
        graph.run("CALL gds.triangleCount.write('triangleCountGraph', {writeProperty: 'triangleCount'})")
        GraphDataScience.__delete_graph("triangleCountGraph")

    def write_local_clustering_coefficient():
        GraphDataScience.__project_graph("localClusteringCoefficientGraph", "UNDIRECTED")
        graph.run("CALL gds.localClusteringCoefficient.write('localClusteringCoefficientGraph', {writeProperty: 'localClusteringCoefficient'})")
        GraphDataScience.__delete_graph("localClusteringCoefficientGraph")

    def write_node_similarity():
        GraphDataScience.__project_graph("nodeSimilarityGraph", "REVERSE")
        graph.run("CALL gds.nodeSimilarity.write('nodeSimilarityGraph', {writeRelationshipType: 'SIMILAR', writeProperty: 'similarity'})")
        GraphDataScience.__delete_graph("nodeSimilarityGraph")

    def write_pearson_similarity():
        graph.run("MATCH (n) WITH {item: id(n), weights: [n.articleRank, n.betweenness, n.degree, n.harmonicCloseness]} AS userData WITH collect(userData) AS data CALL gds.alpha.similarity.pearson.write({data: data, topK: 0, similarityCutoff: 0.1}) YIELD nodes, similarityPairs, writeRelationshipType, writeProperty, min, max, mean, stdDev, p25, p50, p75, p90, p95, p99, p999, p100 RETURN nodes, similarityPairs, writeRelationshipType, writeProperty, min, max, mean, p95")

    def pearson_similarity_measures(cluster, measures):
        # Article, Betweenness, Degree, Closeness
        #measures = [True, True, True, True]

        item = graph.run("MATCH (n {louvain: " + str(cluster) + "}) RETURN id(n) AS item LIMIT 1").data()[0]
        try:
            articleBetweenness = graph.run("MATCH (n {louvain: " + str(cluster) + "}) WITH [{item: " + str(item["item"]) + ", weights: collect(n.articleRank)}, {item: " + str(item["item"]) + ", weights: collect(n.betweenness)}] as data CALL gds.alpha.similarity.pearson.stream({data: data, topK: 0}) YIELD similarity RETURN similarity ORDER BY similarity DESC").data()[0]["similarity"]
        except Exception as e:
            print(e)
            articleBetweenness = 1.0
        try:
            articleDegree = graph.run("MATCH (n {louvain: " + str(cluster) + "}) WITH [{item: " + str(item["item"]) + ", weights: collect(n.articleRank)}, {item: " + str(item["item"]) + ", weights: collect(n.degree)}] as data CALL gds.alpha.similarity.pearson.stream({data: data, topK: 0}) YIELD similarity RETURN similarity ORDER BY similarity DESC").data()[0]["similarity"]
        except Exception as e:
            print(e)
            articleDegree = 1.0
        try:
            articleCloseness = graph.run("MATCH (n {louvain: " + str(cluster) + "}) WITH [{item: " + str(item["item"]) + ", weights: collect(n.articleRank)}, {item: " + str(item["item"]) + ", weights: collect(n.harmonicCloseness)}] as data CALL gds.alpha.similarity.pearson.stream({data: data, topK: 0}) YIELD similarity RETURN similarity ORDER BY similarity DESC").data()[0]["similarity"]
        except Exception as e:
            print(e)
            articleCloseness = 1.0
        try:
            betweennessDegree = graph.run("MATCH (n {louvain: " + str(cluster) + "}) WITH [{item: " + str(item["item"]) + ", weights: collect(n.betweenness)}, {item: " + str(item["item"]) + ", weights: collect(n.degree)}] as data CALL gds.alpha.similarity.pearson.stream({data: data, topK: 0}) YIELD similarity RETURN similarity ORDER BY similarity DESC").data()[0]["similarity"]
        except Exception as e:
            print(e)
            betweennessDegree = 1.0
        try:
            betweennessCloseness = graph.run("MATCH (n {louvain: " + str(cluster) + "}) WITH [{item: " + str(item["item"]) + ", weights: collect(n.betweenness)}, {item: " + str(item["item"]) + ", weights: collect(n.harmonicCloseness)}] as data CALL gds.alpha.similarity.pearson.stream({data: data, topK: 0}) YIELD similarity RETURN similarity ORDER BY similarity DESC").data()[0]["similarity"]
        except Exception as e:
            print(e)
            betweennessCloseness = 1.0
        try:
            degreeCloseness = graph.run("MATCH (n {louvain: " + str(cluster) + "}) WITH [{item: " + str(item["item"]) + ", weights: collect(n.degree)}, {item: " + str(item["item"]) + ", weights: collect(n.harmonicCloseness)}] as data CALL gds.alpha.similarity.pearson.stream({data: data, topK: 0}) YIELD similarity RETURN similarity ORDER BY similarity DESC").data()[0]["similarity"]
        except Exception as e:
            print(e)
            degreeCloseness = 1.0

        #Degree can always be calculated
        if articleBetweenness == 1.0 and articleDegree == 1.0 and articleCloseness == 1.0 and betweennessDegree == 1.0 and betweennessCloseness == 1.0 and degreeCloseness == 1.0:
            return [False, False, True, False]

        if measures[0] and measures[1] and articleBetweenness >= 0.9:
            if (articleDegree + 1.0) + (articleCloseness + 1.0) < (betweennessDegree + 1.0) + (betweennessCloseness + 1.0):
                measures[1] = False
            else:
                measures[0] = False
        if measures[0] and measures[2] and articleDegree >= 0.9:
            if (articleBetweenness + 1.0) + (articleCloseness + 1.0) < (betweennessDegree + 1.0) + (degreeCloseness + 1.0):
                measures[2] = False
            else:
                measures[0] = False
        if measures[0] and measures[3] and articleCloseness >= 0.9:
            if (articleBetweenness + 1.0) + (articleDegree + 1.0) < (betweennessCloseness + 1.0) + (degreeCloseness + 1.0):
                measures[3] = False
            else:
                measures[0] = False
        if measures[1] and measures[2] and betweennessDegree >= 0.9:
            if (articleBetweenness + 1.0) + (betweennessCloseness + 1.0) < (articleDegree + 1.0) + (degreeCloseness + 1.0):
                measures[2] = False
            else:
                measures[1] = False
        if measures[1] and measures[3] and betweennessCloseness >= 0.9:
            if (articleBetweenness + 1.0) + (betweennessDegree + 1.0) < (articleCloseness + 1.0) + (degreeCloseness + 1.0):
                measures[2] = False
            else:
                measures[1] = False
        if measures[2] and measures[3] and degreeCloseness >= 0.9:
            if (articleDegree + 1.0) + (betweennessDegree + 1.0) < (articleCloseness + 1.0) + (betweennessCloseness + 1.0):
                measures[3] = False
            else:
                measures[2] = False
        if measures[3] and articleCloseness == 1.0 and betweennessCloseness == 1.0 and degreeCloseness == 1.0:
            measures[3] = False

        return measures

    def pearson_similarity_nodes(node, breachedNode, comparedSimilarity):
            if comparedSimilarity[0] and comparedSimilarity[1] and comparedSimilarity[2] and comparedSimilarity[3]:
                return graph.run("MATCH (n) WHERE n.domain = '" + str(node) + "' OR n.domain = '" + str(breachedNode) + "' WITH {item: id(n), weights: [n.articleRank, n.betweenness, n.degree, n.harmonicCloseness]} AS dataMeasures WITH collect(dataMeasures) AS data CALL gds.alpha.similarity.pearson.stream({data: data, topK: 0}) YIELD similarity RETURN similarity ORDER BY similarity DESC").data()[0]

            elif comparedSimilarity[0] and comparedSimilarity[1] and comparedSimilarity[2]:
                return graph.run("MATCH (n) WHERE n.domain = '" + str(node) + "' OR n.domain = '" + str(breachedNode) + "' WITH {item: id(n), weights: [n.articleRank, n.betweenness, n.degree]} AS dataMeasures WITH collect(dataMeasures) AS data CALL gds.alpha.similarity.pearson.stream({data: data, topK: 0}) YIELD similarity RETURN similarity ORDER BY similarity DESC").data()[0]

            elif comparedSimilarity[0] and comparedSimilarity[1] and comparedSimilarity[3]:
                return graph.run("MATCH (n) WHERE n.domain = '" + str(node) + "' OR n.domain = '" + str(breachedNode) + "' WITH {item: id(n), weights: [n.articleRank, n.betweenness, n.harmonicCloseness]} AS dataMeasures WITH collect(dataMeasures) AS data CALL gds.alpha.similarity.pearson.stream({data: data, topK: 0}) YIELD similarity RETURN similarity ORDER BY similarity DESC").data()[0]

            elif comparedSimilarity[0] and comparedSimilarity[2] and comparedSimilarity[3]:
                return graph.run("MATCH (n) WHERE n.domain = '" + str(node) + "' OR n.domain = '" + str(breachedNode) + "' WITH {item: id(n), weights: [n.articleRank, n.degree, n.harmonicCloseness]} AS dataMeasures WITH collect(dataMeasures) AS data CALL gds.alpha.similarity.pearson.stream({data: data, topK: 0}) YIELD similarity RETURN similarity ORDER BY similarity DESC").data()[0]

            elif comparedSimilarity[1] and comparedSimilarity[2] and comparedSimilarity[3]:
                return graph.run("MATCH (n) WHERE n.domain = '" + str(node) + "' OR n.domain = '" + str(breachedNode) + "' WITH {item: id(n), weights: [n.betweenness, n.degree, n.harmonicCloseness]} AS dataMeasures WITH collect(dataMeasures) AS data CALL gds.alpha.similarity.pearson.stream({data: data, topK: 0}) YIELD similarity RETURN similarity ORDER BY similarity DESC").data()[0]

            elif comparedSimilarity[0] and comparedSimilarity[1]:
                return graph.run("MATCH (n) WHERE n.domain = '" + str(node) + "' OR n.domain = '" + str(breachedNode) + "' WITH {item: id(n), weights: [n.articleRank, n.betweenness]} AS dataMeasures WITH collect(dataMeasures) AS data CALL gds.alpha.similarity.pearson.stream({data: data, topK: 0}) YIELD similarity RETURN similarity ORDER BY similarity DESC").data()[0]

            elif comparedSimilarity[0] and comparedSimilarity[2]:
                return graph.run("MATCH (n) WHERE n.domain = '" + str(node) + "' OR n.domain = '" + str(breachedNode) + "' WITH {item: id(n), weights: [n.articleRank, n.degree]} AS dataMeasures WITH collect(dataMeasures) AS data CALL gds.alpha.similarity.pearson.stream({data: data, topK: 0}) YIELD similarity RETURN similarity ORDER BY similarity DESC").data()[0]

            elif comparedSimilarity[0] and comparedSimilarity[3]:
                return graph.run("MATCH (n) WHERE n.domain = '" + str(node) + "' OR n.domain = '" + str(breachedNode) + "' WITH {item: id(n), weights: [n.articleRank, n.harmonicCloseness]} AS dataMeasures WITH collect(dataMeasures) AS data CALL gds.alpha.similarity.pearson.stream({data: data, topK: 0}) YIELD similarity RETURN similarity ORDER BY similarity DESC").data()[0]

            elif comparedSimilarity[1] and comparedSimilarity[2]:
                return graph.run("MATCH (n) WHERE n.domain = '" + str(node) + "' OR n.domain = '" + str(breachedNode) + "' WITH {item: id(n), weights: [n.betweenness, n.degree]} AS dataMeasures WITH collect(dataMeasures) AS data CALL gds.alpha.similarity.pearson.stream({data: data, topK: 0}) YIELD similarity RETURN similarity ORDER BY similarity DESC").data()[0]

            elif comparedSimilarity[1] and comparedSimilarity[3]:
                return graph.run("MATCH (n) WHERE n.domain = '" + str(node) + "' OR n.domain = '" + str(breachedNode) + "' WITH {item: id(n), weights: [n.betweenness, n.harmonicCloseness]} AS dataMeasures WITH collect(dataMeasures) AS data CALL gds.alpha.similarity.pearson.stream({data: data, topK: 0}) YIELD similarity RETURN similarity ORDER BY similarity DESC").data()[0]

            elif comparedSimilarity[2] and comparedSimilarity[3]:
                return graph.run("MATCH (n) WHERE n.domain = '" + str(node) + "' OR n.domain = '" + str(breachedNode) + "' WITH {item: id(n), weights: [n.degree, n.harmonicCloseness]} AS dataMeasures WITH collect(dataMeasures) AS data CALL gds.alpha.similarity.pearson.stream({data: data, topK: 0}) YIELD similarity RETURN similarity ORDER BY similarity DESC").data()[0]

            elif comparedSimilarity[0]:
                return graph.run("MATCH (n) WHERE n.domain = '" + str(node) + "' OR n.domain = '" + str(breachedNode) + "' WITH {item: id(n), weights: [n.articleRank]} AS dataMeasures WITH collect(dataMeasures) AS data CALL gds.alpha.similarity.pearson.stream({data: data, topK: 0}) YIELD similarity RETURN similarity ORDER BY similarity DESC").data()[0]

            elif comparedSimilarity[1]:
                return graph.run("MATCH (n) WHERE n.domain = '" + str(node) + "' OR n.domain = '" + str(breachedNode) + "' WITH {item: id(n), weights: [n.betweenness]} AS dataMeasures WITH collect(dataMeasures) AS data CALL gds.alpha.similarity.pearson.stream({data: data, topK: 0}) YIELD similarity RETURN similarity ORDER BY similarity DESC").data()[0]

            elif comparedSimilarity[2]:
                return graph.run("MATCH (n) WHERE n.domain = '" + str(node) + "' OR n.domain = '" + str(breachedNode) + "' WITH {item: id(n), weights: [n.degree]} AS dataMeasures WITH collect(dataMeasures) AS data CALL gds.alpha.similarity.pearson.stream({data: data, topK: 0}) YIELD similarity RETURN similarity ORDER BY similarity DESC").data()[0]

            elif comparedSimilarity[3]:
                return graph.run("MATCH (n) WHERE n.domain = '" + str(node) + "' OR n.domain = '" + str(breachedNode) + "' WITH {item: id(n), weights: [n.harmonicCloseness]} AS dataMeasures WITH collect(dataMeasures) AS data CALL gds.alpha.similarity.pearson.stream({data: data, topK: 0}) YIELD similarity RETURN similarity ORDER BY similarity DESC").data()[0]

            return None

    def euclidean_similarity_cluster(cluster):
        try:
            articleRankSimilarity = graph.run("MATCH (n {louvain: " + str(cluster) + "}) WITH {item: id(n), weights: [n.articleRank]} AS userData WITH collect(userData) AS data CALL gds.alpha.similarity.euclidean.stream({data: data, topK: 0}) YIELD similarity RETURN avg(similarity) AS similarityAvg").data()[0]["similarityAvg"] #YIELD item1, item2, similarity RETURN gds.util.asNode(item1).domain AS from, gds.util.asNode(item2).domain AS to, similarity ORDER BY similarity DESC")
        except Exception as e:
            print(e)
            articleRankSimilarity = 0.0

        try:
            betweennessSimilarity = graph.run("MATCH (n {louvain: " + str(cluster) + "}) WITH {item: id(n), weights: [n.betweenness]} AS userData WITH collect(userData) AS data CALL gds.alpha.similarity.euclidean.stream({data: data, topK: 0}) YIELD similarity RETURN avg(similarity) AS similarityAvg").data()[0]["similarityAvg"]
        except Exception as e:
            print(e)
            betweennessSimilarity = 0.0

        try:
            degreeSimilarity = graph.run("MATCH (n {louvain: " + str(cluster) + "}) WITH {item: id(n), weights: [n.degree]} AS userData WITH collect(userData) AS data CALL gds.alpha.similarity.euclidean.stream({data: data, topK: 0}) YIELD similarity RETURN avg(similarity) AS similarityAvg").data()[0]["similarityAvg"]
            if degreeSimilarity is None:
                degreeSimilarity = 0.0
        except Exception as e:
            print(e)
            degreeSimilarity = 0.0

        try:
            harmonicClosenessSimilarity = graph.run("MATCH (n {louvain: " + str(cluster) + "}) WITH {item: id(n), weights: [n.harmonicCloseness]} AS userData WITH collect(userData) AS data CALL gds.alpha.similarity.euclidean.stream({data: data, topK: 0}) YIELD similarity RETURN avg(similarity) AS similarityAvg").data()[0]["similarityAvg"]
        except Exception as e:
            print(e)
            harmonicClosenessSimilarity = 0.0

        # Article, Betweenness, Degree, Closeness
        measures = [True, True, True, True]

        if articleRankSimilarity is None or articleRankSimilarity < 0.01:
            measures[0] = False
        if betweennessSimilarity is None or betweennessSimilarity < 0.1:
            measures[1] = False
        if degreeSimilarity is None or degreeSimilarity < 0.1:
            measures[2] = False
        if harmonicClosenessSimilarity is None or harmonicClosenessSimilarity < 0.01:
            measures[3] = False

        return measures

    def similarity_probability(domain):
        similarity = [graph.run("MATCH (n) WHERE n.domain = '" + str(domain) + "' RETURN n.domain AS domain, n.numberOfBreaches AS breaches, n.louvain AS cluster, n.severityOfBreaches AS severity, n.articleRank AS articleRank, n.betweenness AS betweenness, n.degree AS degree, n.harmonicCloseness as harmonicCloseness").data()[0]]
        validMeasuresInCluster = []

        domainCluster = graph.run("MATCH (n) WHERE n.domain = '" + str(domain) + "' RETURN n.louvain AS cluster").data()[0]["cluster"]

        validDomainMeasures = GraphDataScience.euclidean_similarity_cluster(domainCluster)
        similarityDomain = GraphDataScience.pearson_similarity_measures(domainCluster, validDomainMeasures)
        #print(similarityDomain)

        cluster = graph.run("MATCH (n) RETURN DISTINCT n.louvain AS cluster").data()
        for c in cluster:
            validMeasures = GraphDataScience.euclidean_similarity_cluster(c["cluster"])
            similarityCluster = GraphDataScience.pearson_similarity_measures(c["cluster"], validMeasures)

            validMeasuresInCluster.append({"cluster": c["cluster"], "articleRank": similarityCluster[0], "betweenness": similarityCluster[1], "degree": similarityCluster[2], "harmonicCloseness": similarityCluster[3]})

            comparedSimilarity = [similarityDomain[0] and similarityCluster[0]]
            comparedSimilarity.append(similarityDomain[1] and similarityCluster[1])
            comparedSimilarity.append(similarityDomain[2] and similarityCluster[2])
            comparedSimilarity.append(similarityDomain[3] and similarityCluster[3])
            #if comparedSimilarity[0] == False and comparedSimilarity[1] == False and comparedSimilarity[2] == False and comparedSimilarity[3] == False:
            #    comparedSimilarity[2] = True
            print(validMeasures)#comparedSimilarity)

            bestEntry = 0.9
            if c["cluster"] == domainCluster:
                bestEntry = 1.0
            bestNodes = []
            clusterNodes = graph.run("MATCH (n {louvain: " + str(c["cluster"]) + "}) RETURN n.domain AS domain, n.numberOfBreaches AS breaches, n.louvain AS cluster, n.severityOfBreaches AS severity, n.articleRank AS articleRank, n.betweenness AS betweenness, n.degree AS degree, n.harmonicCloseness as harmonicCloseness").data()
            for n in clusterNodes:
                if n["domain"] is not None and domain not in n["domain"]:
                    sim = GraphDataScience.pearson_similarity_nodes(domain, n["domain"], comparedSimilarity)
                    #print(sim)
                    if sim is None:
                        continue
                    elif sim["similarity"] == 1.0:
                        bestEntry = 1.0
                        bestNodes.clear()
                        similarity.append(n)
                    elif sim["similarity"] > bestEntry:
                        bestEntry = sim["similarity"]
                        bestNodes.clear()
                        bestNodes.append(n)
                    elif sim["similarity"] == bestEntry:
                        bestNodes.append(n)

            if bestEntry < 1.0:
                similarity.extend(bestNodes)

        if len(similarity) <= 1:
            riskScore = graph.run("MATCH (n) WHERE n.numberOfBreaches > 0  MATCH (m) RETURN toFloat(count(DISTINCT n)) / toFloat(count(DISTINCT m)) AS riskScore").data()[0]
            riskScore["domain"] = domain
            return riskScore

        breachedNodes = []
        avgSeverity = 0
        numberOfBreaches = 0
        for n in similarity:
            if n["breaches"] > 0:
                breachedNodes.append(n)
                avgSeverity += n["severity"]
                numberOfBreaches += n["breaches"]

        return { "domain": domain,
                 "riskScore": len(breachedNodes) / len(similarity),
                 "avgSeverityOfBreaches": avgSeverity,
                 "similarBreachedDomains": breachedNodes,
                 "similarNodes": similarity,
                 "validMeasuresInCluster": validMeasuresInCluster }
