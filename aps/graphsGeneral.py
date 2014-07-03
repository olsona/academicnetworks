import networkx as nx
import community

def getStatsDynamic(graphDict, stats=None):
	'''Produces statistics for a dictionary of dictionaries of graphs.
	Meant to be used for a dictionary of dynamic graphs.
	graphDict is a dictionary where the keys can be anything you want, but probably should be subjects.
	The values are dictionaries of graphs, keyed preferably by year.  
	stats is either a list of statistics you want to look at (see below) 
		or is None, in which case all statistics are computed.
	'degree_centrality','betweenness_centrality' and 'edge_betweenness' are very very slow.'''
	if not stats:
		stats = ['edges','nodes','degree_assortativity','components',\
			'best_modularity','degree_centrality','betweenness_centrality',\
			'eigenvector_centrality','density','edge_betweenness','node_weight']
	statsDict = {y:{s:{} for s in stats} for y in graphDict.keys()}	# y == year
	for y in graphDict.keys():
		G = graphDict[y]
		for s in stats:
			if s in ['betweenness_centrality','eigenvector_centrality','edge_betweenness']:
				res = statsTable[s](G,weight='weight')
			elif s in ['best_modularity']:
				try:
					part = statsTable[s](G)
					mod = community.modularity(part,G)
					num = len(set(part.values()))
					res = [mod,num]
					#print res
				except:
					print s,y
					res = [None, None]
			else:
				try:
					res = statsTable[s](G)
				except:
					print s,y
					res = None
			statsDict[y][s] = res
		print y	
	return statsDict
	

def getNodeWeights(G):
	res = {n:0 for n in G.nodes()}
	for n in G.nodes():
		res[n] = G.node[n]['weight']
	return res

	
#because dispatch tables are cool
statsTable = {'edges':nx.number_of_edges,
			'nodes':nx.number_of_nodes,
			'degree_assortativity':nx.degree_pearson_correlation_coefficient,
			'components':nx.number_connected_components,
			'best_modularity':community.best_partition,
			'degree_centrality':nx.degree_centrality,
			'betweenness_centrality':nx.betweenness_centrality,
			'eigenvector_centrality':nx.eigenvector_centrality_numpy,
			'density':nx.density,
			'edge_betweenness':nx.edge_betweenness_centrality,
			'node_weight':getNodeWeights,
			}
	
	
def plotDynamicGraphsSubject(graphsDict, stat, xlim, ylim, xlabel, ylabel, title, outFile):
	'''Takes a dictionary of dictionaries of graph statistics, where the first level keys are subjects, and
	the second level keys are statistics, and the third level keys are years.  
	This dictionary is a dictionary of results from getStats.
	The argument stat can be any key in statsTable.
	xlim is a 2-element list [xmin,xmax] - for some reason plt cannot figure this out on its own.
	ylim is a 2-element list [ymin,ymax] - again, plt is kinda stupid sometimes.
	xlabel is the label for the x-axis
	ylabel is the label for the y-axis
	title is the title that will go on the graph.
	outFile is the file where this will be written, preferably <something>.png.'''
	import matplotlib.pyplot as plt
	import matplotlib.colors as colors
	import matplotlib.cm as cmx
	#initialize
	plt.clf()
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
			

def plotDynamicGraphsSingle(graphsDict, stat, xlim, ylim, xlabel, ylabel, title, outFile):
	'''Takes a dictionary of graph statistics, where the first level keys are statistics and the second level are years. 
	This dictionary is produced by getStats.
	The argument stat can be any key in statsTable.
	xlim is a 2-element list [xmin,xmax] - for some reason plt cannot figure this out on its own.
	ylim is a 2-element list [ymin,ymax] - again, plt is kinda stupid sometimes.
	xlabel is the label for the x-axis
	ylabel is the label for the y-axis
	title is the title that will go on the graph.
	outFile is the file where this will be written, preferably <something>.png.'''
	import matplotlib.pyplot as plt
	import matplotlib.colors as colors
	import matplotlib.cm as cmx
	#initialize
	plt.clf()
	ax = plt.subplot(111)
	
	#colors
	cm = plt.get_cmap('jet')
	cNorm  = colors.Normalize(vmin=0, vmax=100)
	scalarMap = cmx.ScalarMappable(norm=cNorm, cmap=cm)
	
	#stats
	statf = stat
	if stat in ['best_modularity_num','best_modularity_val']:
		statf = 'best_modularity'
	x = []
	y = []		
	for year in sorted(graphsDict[statf].keys()):
		x.append(year)
		if stat == 'best_modularity_num':
			y.append(graphsDict['best_modularity'][year][1])
		elif stat == 'best_modularity_val':
			y.append(graphsDict['best_modularity'][year][0])
		else:
			y.append(graphsDict[subj][statf][year])
	colorVal = scalarMap.to_rgba(subj)
	ax.plot(x,y,label=subj,color=colorVal)
	box = ax.get_position()
	ax.set_xlabel(xlabel)
	ax.set_ylabel(ylabel)
	ax.set_xlim(xlim[0],xlim[1])
	ax.set_ylim(ylim[0],ylim[1])
	plt.title(title)
	plt.savefig(outFile)
 