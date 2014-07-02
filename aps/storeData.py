def makeCSV(entropyStats, dynamicStats, yearRange, outFile):
	import unicodedata
	
	# write headers
	fOut = open(outFile,'w')
	fOut.write("Author_name;Entropy;Num_Subjects;")
	fOut.write(";".join("Total_{!s}".format(y) for y in yearRange)+";")
	fOut.write(";".join("Eigen_{!s}".format(y) for y in yearRange)+";")
	#fOut.write(";".join("Betweenness_{!s}".format(y) for y in yearRange)+"\n")
	
	# write out data for each author
	authorList = entropyStats.keys()
	print len(authorList)
	ct = 0
	for author in authorList:
		if ct%10 == 0:
			print ct
			
		entropy = entropyStats[author]['entropy']
		numPacs = entropyStats[author]['pacsNum']
		fOut.write("{!s};{:.5e};{:.5e}".format(author,entropy,numPacs))
		for y in yearRange:
			if author in dynamicStats['node_weight'][y].keys():
				val = dynamicStats['node_weight'][y][author]
			else:
				val = 0.0
			fOut.write(";{:.5e}".format(val))
		for y in yearRange:
			if author in dynamicStats['eigenvector_centrality'][y].keys():
				val = dynamicStats['eigenvector_centrality'][y][author]
			else:
				val = 0.0
			fOut.write(";{:.5e}".format(val))
		fOut.write("\n")
		ct += 1
	
	fOut.close()