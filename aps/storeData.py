def makeCSV(entropyStats, dynamicStats, yearRange, outFile):
	import unicodedata
	
	# write headers
	fOut = open(outFile,'w')
	fOut.write("Author_name;Entropy;Num_Subjects;")
	fOut.write(";".join("Total_{!s}".format(y) for y in yearRange)+";")
	fOut.write(";".join("Eigen_{!s}".format(y) for y in yearRange)+";")
	#fOut.write(";".join("Betweenness_{!s}".format(y) for y in yearRange)+"\n")
	
	# get data for each author
	authorList = entropyStats.keys()
	authorDict = {a:{'entropy':0.0,
				'pacsNum':0,
				'totals':{y:0 for y in yearRange},
				'eigenvector_centrality':{y:0.0 for y in yearRange}}
				for a in authorList}
	print len(authorList)
	ct = 0
	
	for author in entropyStats.keys():
		authorDict[author]['entropy'] = entropyStats[author]['entropy']
		authorDict[author]['pacsNum'] = entropyStats[author]['pacsNum']
	
	for y in yearRange:
		for author in dynamicStats['node_weight'][y].keys():
			authorDict[author]['totals'][y] = dynamicStats['node_weight'][y][author]
			authorDict[author]['eigenvector_centrality'][y] = dynamicStats['eigenvector_centrality'][y][author]
	
	for author in authorDict:
		try:
			fOut.write("{!s};{:.5e};{:.5e}".format(author,authorDict[author]['entropy'],authorDict[author]['numPacs']))
			for y in yearRange:
				val = authorDict[author]['totals'][y]
				fOut.write(";{:.5e}".format(val))
			for y in yearRange:
				val = authorDict[author]['eigenvector_centrality'][y]
				fOut.write(";{:.5e}".format(val))
			fOut.write("\n")
			ct += 1
		except:
			pass
	
	fOut.close()