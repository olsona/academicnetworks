import parseAPS
import networkx as nx

def getAdjListSimple(df, what='authors', authorInitialsOnly=False, subsetPACS=None, subsetYears=None):
	result = {}
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
			if lead not in result:
				result[lead] = {}
				for follow in items[1:]:
					result[lead][follow] = {'weight': 1}
			else:
				for follow in items[1:]:
					if follow not in result[lead]:
						result[lead][follow] = {'weight': 1}
					else:
						result[lead][follow]['weight'] += 1
	return result


def getAdjListBipartite(df, authorInitialsOnly=False, subsetPACS=None, subsetYears=None):
	result = {}
	aio = authorInitialsOnly
	sp = subsetPACS
	sy = subsetYears
	for index, row in df.iterrows():
		auths = parseAPS.getAuthors(row, authorInitialsOnly=aio, subsetPACS=sp, subsetYears=sy)
		pacs = parseAPS.getPACS(row, subsetPACS=sp, subsetYears=sy)
		if auths and pacs:
			for a in auths:
				if a not in result:
					result[a] = {}
					for p in pacs:
						result[a][p] = {'weight': 1}
				else:
					for p in pacs:
						if p not in result[a]:
							result[a][p] = {'weight': 1}
						else:
							result[a][p]['weight'] += 1
	return result


def makeGraph(df, authorInitialsOnly=False, subsetPACS=None, subsetYears=None, what=['authors']):
	aio = authorInitialsOnly
	sp = subsetPACS
	sy = subsetYears
	w = what
	if len(what) == 1:
		adjList = getAdjListSimple(df, authorInitialsOnly=aio, subsetPACS=sp, subsetYears=sy, what=w[0])
	elif len(what) == 2:
		adjList = getAdjListBipartite(df, authorInitialsOnly=aio, subsetYears=sy, subsetPACS=sp)

	if adjList:
		G = nx.from_dict_of_dicts(adjList)
		return G
	else:
		return None
		
		
def getDynamicNetwork(df, what='authors', authorInitialsOnly=False, subsetPACS=None, startYear=1982, endYear=2008, window=5):
	diam = window/2
	yearSet = {y:range(y-diam,y+diam+1) for y in range(startYear,endYear+1)}
	results = {y:{} for y in yearSet}
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
					if lead not in results:
						results[yearKey][lead] = {}
						for follow in items[1:]:
							results[yearKey][lead][follow] = {'weight': 1}
					else:
						for follow in items[1:]:
							if follow not in result[lead]:
								results[yearKey][lead][follow] = {'weight': 1}
							else:
								results[yearKey][lead][follow]['weight'] += 1
	return results
	
	
def makeDynamicGraphs(df, what='authors', authorInitialsOnly=False, subsetPACS=None, startYear=1982, endYear=2008, window=5, stats=['edges']):
	aio = authorInitialsOnly
	sp = subsetPACS
	sy = startYear
	ey = endYear
	wi = window
	w = what
	adjLists = getDynamicNetwork(df, what=w, authorInitialsOnly=aio, subsetPACS=sp, startYear=sy, endYear=ey, window=wi)
	numY = len(adjLists)
	print numY
	statsLists = {st:[0.0]*numY for st in stats}
	for yearKey in sorted(adjLists.keys()):
		graphDict = adjLists[yearKey]
		G = nx.from_dict_of_dicts(graphDict)
		for st in statsLists.keys():
			if st in ['edges','nodes']:
				statsLists[st][yearKey-startYear] = len(statsDict[st](G))
			else:
				statsLists[st][yearKey-startYear] = statsDict[st](G)
	return statsLists
	
	
# because I love dispatch tables	
statsDict = {'edges':nx.edges,
			'nodes':nx.nodes,
			'degree_assortativity':nx.degree_pearson_correlation_coefficient,
			'components':nx.number_connected_components
			}