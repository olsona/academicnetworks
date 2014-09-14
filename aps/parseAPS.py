from collections import OrderedDict

def xml2pickle(infile,outfile):
	'''Takes an APS metadata xml file (infile),
	and writes a Pandas DataFrame to outfile'''
	import pandas as pd
	import xmltodict
	import cPickle as pickle

	# read and process infile
	f = open(infile,'r')
	d = xmltodict.parse(f) #parse xml file as a dictionary
	df = pd.DataFrame(d['articles']['article']) # turns it into a Data Frame
	df = df.dropna(subset=['authgrp','pacs']) # drops useless rows
	pickle.dump(df,open(outfile,'wb')) # saves it


def getAuthors(row, authorInitialsOnly=False, subsetPACS=None, subsetYears=None):
	'''Returns author information for an input row
	If authorInitialsOnly = True, then store first and middle initials instead of full names
	subsetPACS, if not None, is a list of PACS codes that we care about;
		if the row doesn't contain any of the PACS codes we care about, then we return nothing.
	subsetYears, if not None, is a list of years we care about.'''

	authgrp = row['authgrp'] # get author information

	# check to see if we want this row, given subsetPACS and subsetYears
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

	# if the row is good, then we process the authors and return them
	if goodP and goodY:
		authorList = processAuthors(authgrp, authorInitialsOnly)
	else:
		authorList = []
	return authorList


def getAuthorsYears(row, authorInitialsOnly=False, subsetPACS=None):
	'''Like getAuthors, but also returns the year'''

	authgrp = row['authgrp'] # get info
	# check if the row is good accoring to subsetPACS
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

	# if good, return information
	if goodP:
		authorList = processAuthors(authgrp, authorInitialsOnly)
	else:
		authorList = []
	return [year, authorList]


def processAuthors(authgrp, authorInitialsOnly=False):
	'''Process the authgrp value from the DF row.  Massive pain, do not try to read.'''
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
	'''Get a list of PACS codes in a row.
	If subsetPACS is None, return all PACS codes.
		Otherwise, only return those codes in subsetPACS.
	If subsetYears is None, return as usual.
		Otherwise, only return the PACS codes if the year falls within subsetYears.'''
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
	'''Like getPACS, but returns PACS codes and year.'''
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
	'''Converts all codes in a given pacsList to the appropriate level of detail.
	pacsLevel = 1 means that 45.10.Db will go to 40.
	pacsLevel = 2 means that 45.10.Db will go to 45.
	pacsLevel = 3 means that 45.10.Db will stay the same.'''
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
	'''Return the year corresponding to a given row.
	First checks for received date, then for published date, and finally revised date.'''
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
	'''Reverses the order of citing/cited pairs in APS citation data.'''
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
	'''Returns a dictionary where the key is the doi and the value is the articles location in the dataframe.'''
	result = {}
	for index, row in df.iterrows():
		doi = row['doi']
		result[doi] = index
	return result


def entropy(freqDict, log_base=10):
	'''Computes the standard formula for entropy.
	Note that a paper can have more than one subject,
		so the total is not the number of papers,
		but the total number of subject entries.'''
	import math
	total = sum(freqDict.values())
	H = 0.0
	for f in freqDict.values():
		if f > 0:
			p = float(f)/float(total)
			H += p * math.log(p, log_base)
	return H*(-1.0)


def getCommonPACS(pacsFreqDict):
	'''Gets the most common PACS in a frequency dictionary.'''
	best = ''
	num = 0
	for p in pacsFreqDict.keys():
		if pacsFreqDict[p] > num:
			num = pacsFreqDict[p]
			best = p
	return best


def isPACSpresent(pacsFreqDict, pacsList):
	'''Checks to see whether any elements in pacsList is in the pacsFreqDict.'''
	presence = False
	for p in pacsList:
		if p in pacsFreqDict.keys():
			presence = True
			break
	return presence