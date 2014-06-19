def processXML(infile, reqFields):
    '''Usage: G = processXML(infile, reqFields)
        infile is a file name (with path as necessary) and must be an XML file.
        reqfields is a list of strings identifying required fields (e.g., ['title','@doi','title'].  'authgrp' should not be included.
        reqfields should not include things like 'aff'.
        Note that only fields in reqfields will be represented in the final graph.'''
    # imports
    import pandas as pd
    import xmltodict
    import networkx as nx
    import collections

    # read and process infile
    f = open(infile,'r')
    d = xmltodict.parse(f)
    k1 = d.keys()
    k2 = d[k1].keys()
    df = pd.DataFrame(d[k1][k2])
    
    # remove rows without required fields
    for rf in reqFields:
        df = df.dropna(subset=[rf])

    # initialize graph
    G = nx.Graph()  # Undirected for the moment

    # iterate through data frame from infile, with all reqfields
    for r in df.iterrows():
        authorInfo, articleInfo = processLine(r, reqFields)
        for i in authorInfo:
            au = i[0]
            af = i[1]
            if au in G.nodes(): # author is already present
                pass
            else: # author is not present, and needs to be added
                pass

def processLine(line, reqFields):
    import collections
    articleInfo = {field:line[field] for field in reqFields} # get all information
    authaff = line['authgrp'] # since we're outputting a graph with authors as nodes
    authorInfo = []
    for aff in authaff:
        auths = aff[u'author']
        myaff = aff[u'aff']
        print myaff
        print type(auths)
        if type(auths) is list:
            for author in auths:
                name = (author['givenname'][0],author['middlename'][0],author['surname']) #first initials only
                authorInfo.append([name, myaff])
        else:
            name = (auths['givenname'][0],auths['middlename'][0],auths['surname'])
            authorInfo.append([name,myaff])

    return authorInfo, articleInfo
