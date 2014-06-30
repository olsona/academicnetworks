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


def getAuthorPacInfo(bipartiteDict, authorList):
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
	

def assignPACSpartition(partitionDict, G):
	partition = {n:0 for n in G.nodes()}
	for n in G.nodes():
		for p in partitionDict.keys():
			part = partitionDict[p]
			if n in part:
				partition[n] = p
	return partition
	

def plotDynamicGraphs(graphsDict, stat, xlim, ylim, xlabel, ylabel, title, outFile):
	import matplotlib.pyplot as plt
	import matplotlib.colors as colors
	import matplotlib.cm as cmx
	#initialize
	plt.clf()
	fig = plt.figure()
	ax = plt.subplot(111)
	
	#colors
	cm = plt.get_cmap('jet')
	cNorm  = colors.Normalize(vmin=0, vmax=100)
	scalarMap = cmx.ScalarMappable(norm=cNorm, cmap=cm)
	
	#stats
	statf = stat
	if stat in ['best_modularity_num','best_modularity_val']:
		statf = 'best_modularity'
	for subj in sorted(graphsDict.keys()):
		x = []
		y = []
		for year in sorted(graphsDict[subj][statf].keys()):
			x.append(year)
			if stat == 'best_modularity_num':
				y.append(graphsDict[subj]['best_modularity'][year][1])
			elif stat == 'best_modularity_val':
				y.append(graphsDict[subj]['best_modularity'][year][0])
			else:
				y.append(graphsDict[subj][statf][year])
		colorVal = scalarMap.to_rgba(subj)
		ax.plot(x,y,label=subj,color=colorVal)
	box = ax.get_position()
	ax.set_position([box.x0, box.y0, box.width * 0.9, box.height])
	ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
	ax.set_xlabel(xlabel)
	ax.set_ylabel(ylabel)
	ax.set_xlim(xlim[0],xlim[1])
	ax.set_ylim(ylim[0],ylim[1])
	plt.title(title)
	plt.savefig(outFile)
			