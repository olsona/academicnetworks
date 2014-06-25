import parseAPS

def getAdjListSimple(df, what='authors', authorInitialsOnly=False, subsetPACS=None):
	result = {}
	for index, row in df.iterrows():
		if what == 'authors':
			items = parseAPS.getAuthors(row, authorInitialsOnly, subsetPACS)
		elif what == 'categories':
			items = parseAPS.getPacs(row, subsetPACS)
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


def getAdjListBipartite(df, authorInitialsOnly=False, subsetPACS=None):
	result = {}
	for index, row in df.iterrows():
		auths = parseAPS.getAuthors(row, authorInitialsOnly, subsetPACS)
		pacs = parseAPS.getPacs(row, subsetPACS)
		if auths and pacs:
			for a in auths:
				if a not in result:
					result[a] = {}
					result[a][p] = {'weight': 1}
				else:
					for p in pacs:
						if p not in result[a]:
							result[a][p] = {'weight': 1}
						else:
							result[a][p]['weight'] += 1
	return result


def makeGraph(df, authorInitialsOnly=False, subsetPACS=None, what=['authors']):
	import networkx as nx 
	w = what
	aio = authorInitialsOnly
	sp = subsetPACS
	if len(what) == 1:
		adjList = getAdjListSimple(df, authorInitialsOnly=aio, subsetPACS=sp, what=w[0])
	elif len(what) == 2:
		adjList = getAdjListBipartite(df, authorInitialsOnly=aio, subsetPACS=sp)

	if adjList:
		G = nx.from_dict_of_dicts(adjList)
		return G
	else:
		return None