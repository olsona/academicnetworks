"""
Functions to build a graph

"""

from . import arxiv


def get_authors_dict_of_dict(df):
    """
    Builds an adjacency list as a dict of dicts from a `df` containing
    arxiv data.

    """
    authors = {}
    for index, row in df.iterrows():
        # `a` is the list of authors for this row (paper)
        a = arxiv.get_authors(row)
        if a:  # `a` can be None, in which case we don't do anything
            lead = a[0]
            if lead not in authors:
                authors[lead] = {}
                for follow in a[1:]:
                    authors[lead][follow] = {'weight': 1}
            else:
                for follow in a[1:]:
                    if follow not in authors[lead]:
                        authors[lead][follow] = {'weight': 1}
                    else:
                        authors[lead][follow]['weight'] += 1
    return authors
