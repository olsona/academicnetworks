from collections import OrderedDict

def xml2pickle(infile,outfile):
	import pandas as pd
	import xmltodict
	import cPickle as pickle

	# read and process infile
	f = open(infile,'r')
	d = xmltodict.parse(f)
	df = pd.DataFrame(d['articles']['article'])
	df = df.dropna(subset=['authgrp','pacs'])
	pickle.dump(df,open(outfile,'wb'))


def getAuthors(row, authorInitialsOnly=False, subsetPACS=None, subsetYears=None):
	# subsetYears first looks at the received date, and if that data isn't available, then at published date, and then at revised date.
	authgrp = row['authgrp'] 
	goodP = 0
	goodY = 0
	if subsetYears:
		year = getYear(row)
		if year in subsetYears:
			goodY = 1
	else:
		goodY = 1
	if subsetPACS and goodY:
		numGood = 0
		subsetPACS = row['pacs']['pacscode']
		for pp in subsetPACS:
			if pp in subsetPACS:
				numGood += 1
		if numGood:
			goodP = 1
	else:
		goodP = 1
	if goodP and goodY:
		authorList = processAuthors(authgrp, authorInitialsOnly)
	else:
		authorList = []
	return authorList
	
	
def getAuthorsYears(row, authorInitialsOnly=False, subsetPACS=None):
	# subsetYears first looks at the received date, and if that data isn't available, then at published date, and then at revised date.
	authgrp = row['authgrp'] 
	goodP = 0
	year = getYear(row)
	if subsetPACS:
		numGood = 0
		myPACS = convertPACS(row['pacs']['pacscode'])
		for pp in myPACS:
			if pp in subsetPACS:
				numGood += 1
		if numGood > 0:
			goodP = 1
	else:
		goodP = 1
	if goodP:
		authorList = processAuthors(authgrp, authorInitialsOnly)
	else:
		authorList = []
	return [year, authorList]
	

def processAuthors(authgrp, authorInitialsOnly=False):
	from collections import OrderedDict
	authorList = []
	if type(authgrp) is OrderedDict:
		if 'author' in authgrp.keys():
			author = authgrp['author']
		else:
			author = authgrp
		if type(author) is OrderedDict:
			if 'surname' in author.keys():
				if 'givenname' in author.keys():
					gname = author['givenname']
					if authorInitialsOnly:
						gname = gname[0]
				else:
					gname = "-"
				if 'middlename' in author.keys():
					mname = author['middlename']
					if type(mname) is list and not authorInitialsOnly:
						mname = tuple(mname)
					elif authorInitialsOnly:
						mname = mname[0]
				else:
					mname = "-"
				if 'suffix' in author.keys():
					suff = author['suffix']
				else:
					suff = "-"
				name = (gname,mname,author['surname'],suff)
				authorList.append(name)
		else:
			for a in author:
				alist = processAuthors(a)
				for al in alist:
					authorList.append(al)
	else:
		for a in authgrp:
			alist = processAuthors(a)
			for al in alist:
				authorList.append(al)
	return authorList
	

def getPACS(row, subsetPACS=None, subsetYears=None):
	paperPacs = convertPACS(row['pacs']['pacscode'])
	goodY = 0
	if subsetYears:
		year = getYear(row)
		if year in subsetYears:
			goodY = 1
	else:
		goodY = 1
		
	if subsetPACS and goodY:
		goodList = []
		for pp in paperPacs:
			if pp in subsetPACS:
				goodList.append(pp)
	elif goodY:
		goodList = paperPacs
	else:
		goodList = []
		
	return goodList


def getPACSYears(row, subsetPACS=None):
	paperPacs = convertPACS(row['pacs']['pacscode'])
	year = getYear(row)
		
	if subsetPACS:
		goodList = []
		for pp in paperPacs:
			if pp in subsetPACS:
				goodList.append(pp)
	else:
		goodList = paperPacs
	
	return [year, goodList]


def convertPACS(pacsList,pacsLevel=2):
	if type(pacsList) is not list:
		pacsList = [pacsList]
	if pacsLevel == 1:
		newList = []
		for p in pacsList:
			try:
				np = int(p.split(".")[0][-2:1])
				newList.append(np)
			except:
				pass
		return list(set(newList))
	elif pacsLevel == 2:
		newList = []
		for p in pacsList:
			try:
				np = int(p.split(".")[0][-2:2])
				newList.append(np)
			except:
				pass
		return list(set(newList))
	else:
		return pacsList


def getYear(row):
	hist = row['history']
	if type(hist) is OrderedDict:
		if 'received' in hist.keys():			 
			year = int(hist['received']['@date'].split("-")[0])			   
			return year
		elif 'published' in hist.keys():
			year = int(hist['published']['@date'].split("-")[0])
			return year
		else:
			year = int(hist['revised']['@date'].split("-")[0])
			return year
	else:
		return 0


def reverseCitingCited(infile, outfile):
	fIn = open(infile,'r')
	fOut = open(outfile, 'w')
	l = fIn.readline().rstrip()
	while l:
		li = l.split(",")
		fOut.write("{!s},{!s}\n".format(li[1],li[0]))
		l = fIn.readline().rstrip()
	fIn.close()
	fOut.close()


def dois2ilocs(df):
	result = {}
	for index, row in df.iterrows():
		doi = row['doi']
		result[doi] = index
	return result