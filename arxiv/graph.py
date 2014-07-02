"""
Functions to build a graph

"""

import networkx as nx

from . import arxiv


def get_adjacency_and_weights(df, what='authors', author_initials_only=False,
                              subset_categories=None):
    """
    Returns a tuple of two things:

    (1) an adjacency list as a dict of dicts from the dataframe ``df``
    containing arxiv data, in the form (assuming 'name1' authored one
    paper with 'name2' and two papers with 'name3':

    {'name1': {'name2': 1, 'name3': 2}}

    (2) a dict of node weights with nodes as keys and weights as values
    (the node weights are the total publications for the given author
    or category)

    Arguments:

    ``what`` : 'authors' or 'categories'.

    ``author_initials_only`` : use initials only to identify authors.

    ``subset_categories`` : iterable of categories, if given, only
        those categories are used to build the adjacency list.

    """
    result = {}
    weights = {}
    for index, row in df.iterrows():
        if what == 'authors':
            items = arxiv.get_authors(row, author_initials_only,
                                      subset_categories)
        elif what == 'categories':
            items = arxiv.get_categories(row, subset_categories)
        if items:  # Skip this row if items is None
            # Add to node weights dict (`weights`)
            for i in items:
                if i in weights:
                    weights[i] += 1
                else:
                    weights[i] = 1
            # Add to adjacency list (`result`)
            lead = items[0]
            if lead not in result:
                result[lead] = {}
                for follow in items[1:]:
                    result[lead][follow] = {'weight': 1}
            else:
                for follow in items[1:]:
                    if follow not in result[lead]:
                        result[lead][follow] = {'weight': 1}
                    else:
                        result[lead][follow]['weight'] += 1
    return (result, weights)


def get_adjacency_and_weights_bipartite(df, author_initials_only=False,
                                        subset_categories=None):
    result = {}
    weights = {}
    authorlist = []
    for index, row in df.iterrows():
        auths = arxiv.get_authors(row, author_initials_only,
                                  subset_categories)
        cats = arxiv.get_categories(row, subset_categories)
        if auths and cats:  # Skip this row if items is None
            # Add to node weights dict (`weights`)
            for a in auths:
                if a in weights:
                    weights[a] += 1
                else:
                    weights[a] = 1
                    authorlist.append(a)
            for c in cats:
                if c in weights:
                    weights[c] += 1
                else:
                    weights[c] = 1
            # Add to adjacency list (`result`)
            for a in auths:
                if a not in result:
                    result[a] = {}
                    for c in cats:
                        result[a][c] = {'weight': 1}
            else:
                for c in cats:
                    if c not in result[a]:
                        result[a][c] = {'weight': 1}
                    else:
                        result[a][c]['weight'] += 1
    return (result, weights, authorlist)


def create_graph(df, what, initials_only):
    r = get_adjacency_and_weights(df, what=what,
                                  author_initials_only=initials_only)
    adjacency, weights = r
    G = nx.from_dict_of_dicts(adjacency)
    nx.set_node_attributes(G, 'weight', weights)
    return G


def create_graphs(df, what='authors', year_range=None, window=5,
                  initials_only=False):
    """
    Returns either a single graph (if year_range is None) or a dict of graphs
    over the sliding window length of ``window`` years, with start years as
    keys.

    Args:

    ``df``: the dataframe to use as input

    ``what``: 'authors' or 'categories'

    ``year_range``: a range of years as a tuple: ``(first_year, last_year)``

    ``window``: width of the moving window (in years)

    """
    if year_range is not None:
        graphs = {}
        for year in range(year_range[0], year_range[1] - window + 1):
            graph_df = df[(df.year >= year) & (df.year < year + window)]
            graphs[year] = create_graph(graph_df, what, initials_only)
        return graphs
    else:
        return create_graph(df, what)
