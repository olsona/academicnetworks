import networkx as nx
import community

def getStats(graphDict, stats=None):
	if not stats:
		stats = ['edges','nodes','degree_assortativity','components',\
			'best_modularity','degree_centrality','betweenness_centrality',\
			'eigenvector_centrality','density','edge_betweenness']
	statsDict = {s:{k:None for k in graphDict.keys()} for s in stats}
	for k in graphDict.keys():
		G = graphDict[k]
		for s in statsDict:
			#print "Working on {!s} for {!s}".format(s, k)
			if s in ['betweenness_centrality','eigenvector_centrality','edge_betweenness']:
				try:
					res = statsTable[s](G,weight='total')
				except:
					print s, k
					res = None
			elif s in ['best_modularity']:
				try:
					part = statsTable[s](G)
					mod = community.modularity(part,G)
					num = len(set(part.values()))
					res = [mod,num]
					#print res
				except:
					print s,k
					res = [None, None]
			else:
				try:
					res = statsTable[s](G)
				except:
					print s,k
					res = None
			statsDict[s][k] = res
		print k
	return statsDict
	
	
#because dispatch tables are cool
statsTable = {'edges':nx.number_of_edges,
			'nodes':nx.number_of_nodes,
			'degree_assortativity':nx.degree_pearson_correlation_coefficient,
			'components':nx.number_connected_components,
			'best_modularity':community.best_partition,
			'degree_centrality':nx.degree_centrality,
			'betweenness_centrality':nx.betweenness_centrality,
			'eigenvector_centrality':nx.eigenvector_centrality,
			'density':nx.density,
			'edge_betweenness':nx.edge_betweenness_centrality
			}
	