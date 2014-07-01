def coAuthorsXML(infile, pacsCodes=[-1], years=[]):
	'''Usage: G = processXML(infile, <pacsCodes=[...], years=[...]>)
		infile is a file name (with path as necessary) and must be an XML file.'''
	# imports
	import pandas as pd
	import xmltodict
	import networkx as nx

	# read and process infile
	f = open(infile,'r')
	d = xmltodict.parse(f)
	df = pd.DataFrame(d['articles']['article'])
	
	# remove rows without required fields
	#for rf in reqFields:
	#	 df = df.dropna(subset=[rf])
	
	df = df.dropna(subset=['pacs'])
	df = df.dropna(subset=['authgrp'])

	# initialize graph
	Graphs = [nx.Graph() for i in range(len(pacsCodes))]  # Undirected for the moment
	
	myPacsCodes = []
	for p in pacsCodes: 
		# make list of acceptable PACS codes
		if p == -1:
			myPacsCodes.append([-1])
		elif p % 10 == 0:
			myPacsCodes.append(range(p,p+10))
		else:
			myPacsCodes.append([p])
	
	for x in range(len(myPacsCodes)):
		G = Graphs[x]
		p = myPacsCodes[x]
		# iterate through data frame from infile
		ilocs = range(len(df))
		for i in ilocs:
			r = df.iloc[i]
			# print type(r)
			pacs = r['pacs']['pacscode']
			if len(years):
				hist = r['history']
				if 'received' in hist.keys():
					year = int(hist['received'].split("-")[0])
					if year not in years:
						break
			if p == [-1] or pacsMatch(pacs,p):
				authorInfo = processAuthorLine(r)
				for au in authorInfo:
					if au not in G.nodes():
						#print au
						G.add_node(au,{'numPapers':0})
						
				for au in authorInfo:
					for a in authorInfo:
						if a != au:
							if a in G.neighbors(au):
								G[au][a]['weight'] += 1
							else:
								G.add_edge(au,a, weight=1) 
				
				for au in authorInfo:
					G.node[au]['numPapers'] += 1
	
	#for node in G.nodes():
	#	 if G.node[node]['numPapers'] > 50:
	#		 print node, G.node[node]['numPapers']		
				
	#return G, articleDict
	return Graphs
	

def processAuthorLine(line):
	#articleInfo = {field:line[field] for field in reqFields} # get all information
	authgrp = line['authgrp'] # since we're outputting a graph with authors as nodes
	# print authgrp
	authorList = processAuthors(authgrp)
	return authorList
	

def processAuthors(authgrp):
	from collections import OrderedDict
	authorList = []
	if type(authgrp) is OrderedDict:
		if 'author' in authgrp.keys():
			author = authgrp['author']
		else:
			author = authgrp
		if type(author) is OrderedDict:
			if 'surname' in author.keys():
				try:
					gname = author['givenname']
				except:
					gname = "-"
				try:
					mname = author['middlename']
					if type(mname) is list:
						mname = tuple(mname)
				except:
					mname = "-"
				try:
					suff = author['suffix']
				except:
					suff = "-"
				name = (gname,mname,author['surname'],suff)
				authorList.append(name)
		else:
			for a in author:
				alist = processAuthors(a)
				for al in alist:
					authorList.append(al)
	else:
		#print authgrp
		for a in authgrp:
			alist = processAuthors(a)
			for al in alist:
				authorList.append(al)
	return authorList
	

def pacsMatch(paperPacs, pacsList):
	#print paperPacs
	for pp in paperPacs:
		try:
			p = pp.split(".")[0]
			if int(p) in pacsList:
				return 1
		except:
			pass
	return 0
	

def addCoAuthorGraphs(Graphs):
	import networkx as nx
	resG = nx.Graph()
	for G in Graphs:
		E = G.edges()
		for e in E:
			[n1,n2] = [e[0],e[1]]
			w = G[n1][n2]['weight']
			if e in resG.edges():
				resG[n1][n2]['weight'] += w
			else:
				resG.add_edge(n1,n2,weight = w)
	return resG 
	

def pacsXML(infile, pacsLevel=2):
	'''Usage: G = processXML(infile, reqFields)
		infile is a file name (with path as necessary) and must be an XML file.'''
	# imports
	import pandas as pd
	import xmltodict
	import networkx as nx

	# read and process infile
	f = open(infile,'r')
	d = xmltodict.parse(f)
	df = pd.DataFrame(d['articles']['article'])
	
	df = df.dropna(subset=['pacs'])

	# initialize graph
	G = nx.Graph()	# Undirected for the moment
	
	ilocs = range(len(df))
	for i in ilocs:
		r = df.iloc[i]
		# print type(r)
		properPacs = r['pacs']['pacscode']
		pacsSet = set()
		for p in properPacs:
			try:
				if pacsLevel == 1:
					pacs = (int(p.split(".")[0])/10)*10
				elif pacsLevel == 2:
					pacs = int(p.split(".")[0])
					#print pacs
				else:
					pacs = p
				pacsSet.add(pacs)
			except:
				pass
		pacsList = list(pacsSet)
		#print pacsList
		for x in range(len(pacsList)):
			for y in range(x):
				px = pacsList[x]
				py = pacsList[y]
				if G.has_edge(px,py):
					G[px][py]['weight'] += 1
				else:
					G.add_edge(px,py,weight=1)
			
	#return G, articleDict
	return G
	

def authors2Subjects(infile):
	'''Usage: G = processXML(infile)
		infile is a file name (with path as necessary) and must be an XML file.'''
	# imports
	import pandas as pd
	import xmltodict
	import networkx as nx

	# read and process infile
	f = open(infile,'r')
	d = xmltodict.parse(f)
	df = pd.DataFrame(d['articles']['article'])
	
	df = df.dropna(subset=['pacs'])
	df = df.dropna(subset=['authgrp'])

	# initialize graph
	G = nx.Graph()	# Undirected for the moment
	
	# iterate through data frame from infile
	ilocs = range(len(df))
	for i in ilocs:
		r = df.iloc[i]
		
		pacs = r['pacs']['pacscode']
		for p in pacs:
			if p not in G.nodes():
				G.add_node(p)
				
		authorInfo = processAuthorLine(r)
		for au in authorInfo:
			if au not in G.nodes():
				G.add_node(au)
						
		for au in authorInfo:
			for p in pacs:
				if G.has_edge(au,p):
					G[au][p]['weight'] += 1
				else:
					G.add_edge(au,p,weight=1)
	return G