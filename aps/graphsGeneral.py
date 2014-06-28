import networkx as nx
import community

def getStats(graphDict, stats=['components']):
	statsDict = {s:{k:None for k in graphDict.keys()} for s in stats}
	for k in graphDict.keys():
		G = graphDict[k]
		for s in statsDict:
			print "Working on {!s} for {!s}".format(s, k)
			res = statsTable[s](G)
			statsDict[s][k] = res
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
			'density':nx.density
			}