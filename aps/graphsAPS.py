import parseAPS
import networkx as nx
import community

def getAdjListSimple(df, what='authors', authorInitialsOnly=False, subsetPACS=None, subsetYears=None):
	'''Builds a dictionary of edges (and a list of node weights) from a given data frame df.
	Helper function.
	what: the nodes you want to look at.  If what = 'authors', the nodes are authors.  If what = 'pacs', the nodes are PACS codes.
	authorInitialsOnly: boolean indicating whether you want to only save the first and middle initials, or the full names.
	subsetPACS: an integer list of PACS codes you want to look at (only consider papers in that subject range)
		Looks at all subjects if subsetPACS is None.
	subsetYears: an integer list of years you want to consider.
		Looks at all years if subsetYears is None.'''
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
				resultDict[lead] = {}
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
	'''As above, but for a bipartite authors->PACS graph.
	Builds a dictionary of edges (and a list of node weights, and a list of authors) from a given data frame df.
	Helper function.
	what: the nodes you want to look at.  If what = 'authors', the nodes are authors.  If what = 'pacs', the nodes are PACS codes.
	authorInitialsOnly: boolean indicating whether you want to only save the first and middle initials, or the full names.
	subsetPACS: an integer list of PACS codes you want to look at (only consider papers in that subject range)
		Looks at all subjects if subsetPACS is None.
	subsetYears: an integer list of years you want to consider.
		Looks at all years if subsetYears is None.'''
	resultDict = {}
	aio = authorInitialsOnly
	sp = subsetPACS
	sy = subsetYears
	nodeWeights = {}
	authorList = []
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
						if p not in resultDict[a]:
							resultDict[a][p] = {'weight': 1}
						else:
							resultDict[a][p]['weight'] += 1
			for a in auths:
				if a in nodeWeights:
					nodeWeights[a] += 1
				else:
					nodeWeights[a] = 1
				authorList.append(a)
			for p in pacs:
				if p in nodeWeights:
					nodeWeights[p] += 1
				else:
					nodeWeights[p] = 1
				
	return resultDict, nodeWeights, authorList


def getAuthorPacsInfo(bipartiteDict, authorList):
	'''Gets a dictionary of PACS information for each author in a bipartite dictionary.
	authorList is the list of authors, so we do not bother with PACS information.
	Returns a dictionary where each key is an author name, 
		and the value is another dictionary storing entropy information 
		and the full list of subjects and their frequencies.'''
	G = nx.from_dict_of_dicts(bipartiteDict)
	authorInfo = {a:{'pacsList':{},'entropy':0.0} for a in authorList}
	for a in authorList:
		subjectList = G.neighbors(a)
		subjectFreq3 = {subj:G[a][subj]['weight'] for subj in subjectList}
		subjectFreq2 = {p:0 for p in range(0,100,10)}
		for s in subjectFreq3.keys():
			n = subjectFreq3[s]
			p = (s/10)*10
			if p in subjectFreq2.keys():
				subjectFreq2[p] += n
			else:
				subjectFreq2[p] = n
		entropy = parseAPS.entropy(subjectFreq2)
		authorInfo[a]['entropy'] = entropy
		authorInfo[a]['pacsList'] = subjectFreq2
	return authorInfo 
	

def makeGraph(df, authorInitialsOnly=False, subsetPACS=None, subsetYears=None, what=['authors']):
	'''Actually builds a networkx graph, using the helper functions.
	what: the nodes you want to look at.  
		If what = ['authors'], the nodes are authors.  
		If what = ['pacs'], the nodes are PACS codes.
		If what = ['authors','pacs'], the resulting graph is a bipartite graph with author and PACS nodes.
	authorInitialsOnly: boolean indicating whether you want to only save the first and middle initials, or the full names.
	subsetPACS: an integer list of PACS codes you want to look at (only consider papers in that subject range)
		Looks at all subjects if subsetPACS is None.
	subsetYears: an integer list of years you want to consider.
		Looks at all years if subsetYears is None.'''
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
		nx.set_node_attributes(G,'weight',nodeWeights)
		return G
	else:
		return None
		
		
def getDynamicNetwork(df, what='authors', authorInitialsOnly=False, subsetPACS=None, startYear=1982, endYear=2007, window=5):
	'''Creates a dictionary of dictionaries in order to make graphs, where each dictionary is made using getAdjListSimple.  
	The keys of the dictionary are years from startYear to endYear, and the values are the graph dictionaries.
	If window=1, the graph only considers papers from a single year.
	If window=3, the graph considers papers from year-1, year, and year+1.
	If window=5, the graph considers papers from year-2,year-1,year,year+1,year+2.
	Make sure that startYear and endYear are set appropriately for the window; the bottom limit is 1980, and the top is 2010.'''
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
	
	
def makeDynamicGraphs(df, what='authors', authorInitialsOnly=False, subsetPACS=None, startYear=1982, endYear=2008, window=5):
	'''Actually makes the graphs - this is what you run if you want a list of graphs.
	Produces a dictionary where the keys are years and the values are graphs.
	See getDynamicNetwork for an explanation of arguments.'''
	aio = authorInitialsOnly
	sp = subsetPACS
	sy = startYear
	ey = endYear
	wi = window
	w = what
	adjLists, nodeWeights = getDynamicNetwork(df, what=w, authorInitialsOnly=aio, subsetPACS=sp, startYear=sy, endYear=ey, window=wi)
	graphsList = {y:None for y in adjLists.keys()}
	for yearKey in sorted(adjLists.keys()):
		graphDict = adjLists[yearKey]
		G = nx.from_dict_of_dicts(graphDict)
		nx.set_node_attributes(G,'weight',nodeWeights[yearKey])
		graphsList[yearKey] = G
	return graphsList