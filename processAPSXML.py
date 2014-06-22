def processXML(infile, pacsCode=-1):
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
    
    # remove rows without required fields
    #for rf in reqFields:
    #    df = df.dropna(subset=[rf])
    
    df = df.dropna(subset=['pacs'])
    df = df.dropna(subset=['authgrp'])

    # initialize graph
    G = nx.Graph()  # Undirected for the moment

    # make list of acceptable PACS codes
    if pacsCode == -1:
        pacsList = range(0,100)
    elif pacsCode % 10 == 0:
        pacsList = range(pacsCode,pacsCode+10)
    else:
        pacsList = [pacsCode]
    
    print pacsList
    
    # iterate through data frame from infile
    ilocs = range(len(df))
    for i in ilocs:
        r = df.iloc[i]
        # print type(r)
        pacs = r['pacs']['pacscode']
        if pacsCode == -1 or pacsMatch(pacs,pacsList):
            authorInfo = processLine(r)
            for au in authorInfo:
                if au in G.nodes(): # author is already present
                    for a in authorInfo:
                        if a != au:
                            if a in G.neighbors(au):
                                G[au][a]['weight'] += 1
                            else:
                                G.add_edge(au,a, weight=1) 
                else: # author is not present, and needs to be added
                    G.add_node(au)
                    # add coauthors
                    for a in authorInfo:
                        if a != au:
                            G.add_edge(au,a, weight=1) 
                            # Each author node has an attribute called 'Coauthors':
                            # 'Coauthors' is a dictionary storing the names of all
                            # coauthors as keys, and number of cowritten papers as
                            # an attribute
                
    #return G, articleDict
    return G
    

def processLine(line):
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
                    gname = author['givenname'][0]
                except:
                    gname = "-"
                try:
                    mname = author['middlename'][0]
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