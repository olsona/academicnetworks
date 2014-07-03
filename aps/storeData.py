def makeCSV(entropyStats, dynamicStats, yearRange, outFile):
	import unicodedata
	
	# write headers
	fOut = open(outFile,'w')
	fOut.write("Author_name;Entropy;Num_Subjects;")
	fOut.write(";".join("Total_{!s}".format(y) for y in yearRange)+";")
	fOut.write(";".join("Eigen_{!s}".format(y) for y in yearRange)+"\n")
	#fOut.write(";".join("Betweenness_{!s}".format(y) for y in yearRange)+"\n")
	
	# get data for each author
	authorList = entropyStats.keys()
	authorDict = {a:{'entropy':0.0,
				'pacsNum':0,
				'totals':{y:0 for y in yearRange},
				'eigenvector_centrality':{y:0.0 for y in yearRange}}
				for a in authorList}
	print len(authorList)
	
	for author in entropyStats.keys():
		authorDict[author]['entropy'] = entropyStats[author]['entropy']
		authorDict[author]['pacsNum'] = entropyStats[author]['pacsNum']
	
	for y in yearRange:
		for author in dynamicStats[y]['node_weight'].keys():
			try:
				authorDict[author]['totals'][y] = dynamicStats[y]['node_weight'][author]
				authorDict[author]['eigenvector_centrality'][y] = dynamicStats[y]['eigenvector_centrality'][author]
				ct += 1
			except KeyError:
				print author	
	
	for author in authorDict:
		fOut.write("{!s}\t{:.5e}\t{:d}".format(author,authorDict[author]['entropy'],authorDict[author]['pacsNum']))
		for y in yearRange:
			val = authorDict[author]['totals'][y]
			fOut.write("\t{:d}".format(val))
		for y in yearRange:
			val = authorDict[author]['eigenvector_centrality'][y]
			if val > 0.0:
				fOut.write("\t{:.5e}".format(val))
			else:
				fOut.write("\t0.0")
		fOut.write("\n")
	
	fOut.close()