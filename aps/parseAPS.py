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


def getAuthors(row, initials_only=False, pacsList=None):
    authgrp = row['authgrp'] 
    if pacsList:
        numGood = 0
        paperPacs = row['pacs']['pacscode']
        for pp in paperPacs:
            if pp in pacsList:
                numGood += 1
        if numGood:
            authorList = processAuthors(authgrp, initials_only)
        else:
            authorList = []
    else:
        authorList = processAuthors(authgrp, initials_only)
    return authorList
    

def processAuthors(authgrp, initials_only=False):
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
                    if initials_only:
                        gname = gname[0]
                else:
                    gname = "-"
                if 'middlename' in author.keys():
                    mname = author['middlename']
                    if type(mname) is list and not initials_only:
                        mname = tuple(mname)
                    elif initials_only:
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
    

def getPACS(row, pacsList=None):
    paperPacs = row['pacs']['pacscode']
    if pacsList:
        goodList = []
        for pp in paperPacs:
            if pp in pacsList:
                goodList.append(pp)
        return goodList
    else:
        return pac


def getYear(row):
    hist = r['history']
    if type(hist) is OrderedDict:
        if 'received' in hist.keys() :                
            year = int(hist['received'].split("-")[0])            
            return year
        else:
            year = int(hist['published'].split("-")[0])
            return year
    else:
        return 0