"""
Functions to build a graph

"""

import networkx as nx

from . import arxiv


def get_adjacency_and_weights(df, what='authors', author_initials_only=False,
                              subset_categories=None):
    """
    Returns a tuple of two things:

    (1) an adjacency list as a dict of dicts from a ``df`` containing
    arxiv data, and

    (2) a dict of node weiths with nodes as keys and weights as values

    Args:

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
                    result[lead][follow] = {'total': 1}
            else:
                for follow in items[1:]:
                    if follow not in result[lead]:
                        result[lead][follow] = {'total': 1}
                    else:
                        result[lead][follow]['total'] += 1
    return (result, weights)


def create_graph(df, what):
    adjacency, weights = get_adjacency_and_weights(df, what=what)
    G = nx.from_dict_of_dicts(adjacency)
    nx.set_node_attributes(G, 'total', weights)
    return G


def create_graphs(df, what='authors', year_range=None, window=5):
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
            graphs[year] = create_graph(graph_df, what)
        return graphs
    else:
        return create_graph(df, what)
