"""
Functions to build a graph

"""

from . import arxiv


def get_adjacency_list(df, what='authors', author_initials_only=False,
                       subset_categories=None):
    """
    Builds an adjacency list as a dict of dicts from a ``df`` containing
    arxiv data.

    Args:

    ``what`` : 'authors' or 'categories'.

    ``author_initials_only`` : use initials only to identify authors.

    ``subset_categories`` : iterable of categories, if given, only
        those categories are used to build the adjacency list.

    """
    result = {}
    for index, row in df.iterrows():
        if what == 'authors':
            items = arxiv.get_authors(row, author_initials_only,
                                      subset_categories)
        elif what == 'categories':
            items = arxiv.get_categories(row, subset_categories)
        if items:  # Skip this row if items is None
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
    return result
