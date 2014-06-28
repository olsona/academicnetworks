import parseAPS
import networkx as nx
import community

def getAdjListSimple(df, what='authors', authorInitialsOnly=False, subsetPACS=None, subsetYears=None):
	resultDict = {}
	nodeWeights = {}
	aio = authorInitialsOnly
	sp = subsetPACS
	sy = subsetYears
	for index, row in df.iterrows():
		if what == 'authors':
			items = parseAPS.getAuthors(row, authorInitialsOnly=aio, subsetPACS=sp, subsetYears=sy)
		elif what == 'pacs':
			items = parseAPS.getPACS(row, subsetPACS=sp, subsetYears=sy)
		if items:  # Skip this row if items is None
			lead = items[0]
			if lead not in resultDict:
				result[lead] = {}
				for follow in items[1:]:
					resultDict[lead][follow] = {'weight': 1}
			else:
				for follow in items[1:]:
					if follow not in resultDict[lead]:
						resultDict[lead][follow] = {'weight': 1}
					else:
						resultDict[lead][follow]['weight'] += 1
			for i in items:
				if i in nodeWeights:
					nodeWeights[i] += 1
				else:
					nodeWeights[i] = 1
	return resultDict, nodeWeights


def getAdjListBipartite(df, authorInitialsOnly=False, subsetPACS=None, subsetYears=None):
	resultDict = {}
	aio = authorInitialsOnly
	sp = subsetPACS
	sy = subsetYears
	nodeWeights = {}
	for index, row in df.iterrows():
		auths = parseAPS.getAuthors(row, authorInitialsOnly=aio, subsetPACS=sp, subsetYears=sy)
		pacs = parseAPS.getPACS(row, subsetPACS=sp, subsetYears=sy)
		if auths and pacs:
			for a in auths:
				if a not in resultDict:
					resultDict[a] = {}
					for p in pacs:
						resultDict[a][p] = {'weight': 1}
				else:
					for p in pacs:
						if p not in result[a]:
							resultDict[a][p] = {'weight': 1}
						else:
							resultDict[a][p]['weight'] += 1
			for a in auths:
				if a in nodeWeights:
					nodeWeights[a] += 1
				else:
					nodeWeights[a] = 1
			for p in pacs:
				if p in nodeWeights:
					nodeWeights[p] += 1
				else:
					nodeWeights[p] = 1
				
	return resultDict, nodeWeights


def makeGraph(df, authorInitialsOnly=False, subsetPACS=None, subsetYears=None, what=['authors']):
	aio = authorInitialsOnly
	sp = subsetPACS
	sy = subsetYears
	w = what
	if len(what) == 1:
		adjList, nodeWeights = getAdjListSimple(df, authorInitialsOnly=aio, subsetPACS=sp, subsetYears=sy, what=w[0])
	elif len(what) == 2:
		adjList, nodeWeights = getAdjListBipartite(df, authorInitialsOnly=aio, subsetYears=sy, subsetPACS=sp)

	if adjList:
		G = nx.from_dict_of_dicts(adjList)
		nx.set_node_attributes(G,'total',nodeWeights)
		return G
	else:
		return None
		
		
def getDynamicNetwork(df, what='authors', authorInitialsOnly=False, subsetPACS=None, startYear=1982, endYear=2008, window=5):
	diam = window/2
	yearSet = {y:range(y-diam,y+diam+1) for y in range(startYear,endYear+1)}
	resultsDict = {y:{} for y in yearSet}
	nodeWeights = {y:{} for y in yearSet}
	aio = authorInitialsOnly
	sp = subsetPACS
	for index, row in df.iterrows():
		if what == 'authors':
			ret = parseAPS.getAuthorsYears(row, authorInitialsOnly=aio, subsetPACS=sp)
		elif what == 'pacs':
			ret = parseAPS.getPACSYears(row, subsetPACS=sp)
		[year, items] = ret
		if items:  # Skip this row if items is None
			for yearKey in yearSet.keys():
				yearRange = yearSet[yearKey]
				if year in yearRange:
					lead = items[0]
					if lead not in resultsDict[yearKey]:
						resultsDict[yearKey][lead] = {}
						for follow in items[1:]:
							resultsDict[yearKey][lead][follow] = {'weight': 1}
					else:
						for follow in items[1:]:
							if follow not in resultsDict[yearKey][lead]:
								resultsDict[yearKey][lead][follow] = {'weight': 1}
							else:
								resultsDict[yearKey][lead][follow]['weight'] += 1
					for i in items:
						if i in nodeWeights[yearKey]:
							nodeWeights[yearKey][i] += 1
						else:
							nodeWeights[yearKey][i] = 1
	return resultsDict, nodeWeights
	
	
def makeDynamicGraphs(df, what='authors', authorInitialsOnly=False, subsetPACS=None, startYear=1982, endYear=2008, window=5, stats=['edges'], partition=None):
	aio = authorInitialsOnly
	sp = subsetPACS
	sy = startYear
	ey = endYear
	wi = window
	w = what
	if 'modularity' in stats and not partition:
		print "No partition given for modularity computation"
		stats.remove('modularity')
	adjLists, nodeWeights = getDynamicNetwork(df, what=w, authorInitialsOnly=aio, subsetPACS=sp, startYear=sy, endYear=ey, window=wi)
	numY = len(adjLists)
	statsLists = {st:[0.0]*numY for st in stats}
	for yearKey in sorted(adjLists.keys()):
		graphDict = adjLists[yearKey]
		G = nx.from_dict_of_dicts(graphDict)
		nx.set_node_attributes(G,'total',nodeWeights[yearKey])
		for st in statsLists.keys():
			if st == 'modularity':
				myPartition = assignPACSpartition(partition,G)
				statsLists[st][yearKey-startYear] = statsTable[st](myPartition,G)
			elif st == 'best_modularity':
				part = statsTable[st](G)
				#print len(set(part.values()))
				statsLists[st][yearKey-startYear] = [statsTable['modularity'](part,G),len(set(part.values()))]
			else:
				statsLists[st][yearKey-startYear] = statsTable[st](G)
	return statsLists


def assignPACSpartition(partitionDict, G):
	partition = {n:0 for n in G.nodes()}
	for n in G.nodes():
		for p in partitionDict.keys():
			part = partitionDict[p]
			if n in part:
				partition[n] = p
	return partition
				
		
	
# because I love dispatch tables	
statsTable = {'edges':nx.number_of_edges,
			'nodes':nx.number_of_nodes,
			'degree_assortativity':nx.degree_pearson_correlation_coefficient,
			'components':nx.number_connected_components,
			'best_modularity':community.best_partition,
			'modularity':community.modularity
			}