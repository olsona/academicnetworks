"""
Functions to process and analyze arXiv data

"""


import glob

import pandas as pd


def read_all_arxiv_files(glob_pattern='arxiv/s-*.csv'):
    files = glob.glob(glob_pattern)
    df = pd.read_csv(files[0], index_col=0, encoding='utf-8')
    for f in files[1:]:
        df = pd.concat([df, pd.read_csv(f, index_col=0,
                        encoding='utf-8')])
    return df


def unified_name(name, initials_only=True):
    """
    Clean up a `name` string. If `initials_only` is False, full forenames
    will be used.

    """
    if len(name) <= 1:
        return name
    try:
        if initials_only:
            l = [i[0] for i in name.rstrip(' .').split(' ')]
        else:
            l = [i for i in name.rstrip(' .').split(' ')]
    except IndexError:
        return name
    initials = []
    for i in l:
        try:
            initials.append(i.strip('-').strip('.'))
        except IndexError:
            pass
    return ''.join(initials)


def get_authors(row):
    """Get all authors for a given row (paper)"""
    try:
        #forenames = [unified_name(i) for i in row.forenames.split('|')]
        forenames = [unified_name(i, initials_only=False)
                     for i in row.forenames.split('|')]
        lastnames = row.keyname.split('|')
    except AttributeError:  # if a paper has no authors?
        return None  # TODO should log this

    authors = [', '.join(i) for i in zip(lastnames, forenames)]
    return authors


def get_author_series(df):
    """
    Return a pandas Series with author names as the index, containing
    total papers per author

    """
    author_counter = {}

    for index, row in df.iterrows():
        # Make unified initials
    #     make_ui = lambda x: ''.join([i.strip('-').strip('.')[0]
    #                                  for i in x.rstrip(' .').split(' ')])
        authors = get_authors(row)
        if authors:
            for a in authors:
                if a in author_counter:
                    author_counter[a] += 1
                else:
                    author_counter[a] = 1

    return pd.Series(author_counter)


def get_all_authors(df):
    """Returns the set of all authors found in `df`."""
    authors = set()
    for index, row in df.iterrows():
        a = get_authors(row)
        if a:
            for i in a:
                authors.add(i)
    return authors
