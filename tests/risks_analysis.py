import json

f = open('./dbseed/risks.json')

data = json.load(f)

hasSimilarNodes = 0
numberSimilarNodes = 0

hasRisk = 0
totalRisk = 0
maxRisk = 0

totalBreached = []
totalBreaches = 0

seenCluster = []
validArticleRank = 0
validBetweenness = 0
validDegree = 0
validHarmonicCloseness = 0

for d in data:
    if "similarNodes" in d and len(d["similarNodes"]) > 0:
        hasSimilarNodes += 1
        numberSimilarNodes += len(d["similarNodes"])
    else:
        print(d)
    if "riskScore" in d:
        hasRisk += 1
        totalRisk += d["riskScore"]
        if d["riskScore"] > maxRisk:
            maxRisk = d["riskScore"]
    if "similarBreachedDomains" in d:
        for breached in d["similarBreachedDomains"]:
            if breached["domain"] not in totalBreached:
                totalBreached.append(breached["domain"])
                totalBreaches += breached["breaches"]
    if "validMeasuresInCluster" in d:
        for c in d["validMeasuresInCluster"]:
            if c["cluster"] not in seenCluster:
                seenCluster.append(c["cluster"])
                if c["articleRank"]:
                    validArticleRank += 1
                if c["betweenness"]:
                    validBetweenness += 1
                if c["degree"]:
                    validDegree += 1
                if c["harmonicCloseness"]:
                    validHarmonicCloseness += 1

print(len(data))

print("Has similar nodes: ", hasSimilarNodes)
print("Average amount of similar nodes: ", numberSimilarNodes/hasSimilarNodes)

print("Has risk: ", hasRisk)
print("Average risk: ", totalRisk/hasRisk)
print("maxRisk: ", maxRisk)

print("Total breached: ", len(totalBreached))
print("Total breaches: ", totalBreaches)

print("Number of cluster: ", len(seenCluster))
print("Number of valid ArticleRanks: ", validArticleRank)
print("Number of valid Betweenness: ", validBetweenness)
print("Number of valid Degree: ", validDegree)
print("Number of valid Harmonic Closeness: ", validHarmonicCloseness)
