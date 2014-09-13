"""
Functions to process and analyze arXiv data

"""


import glob
import os

import numpy as np
import pandas as pd


def read_all_arxiv_files(glob_pattern='arxiv/s-*.csv'):
    files = glob.glob(glob_pattern)
    df = pd.read_csv(files[0], index_col=0, encoding='utf-8')
    for f in files[1:]:
        df = pd.concat([df, pd.read_csv(f, index_col=0,
                        encoding='utf-8')])
    df['year'] = df.index.map(year_extractor)
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


def get_authors(row, initials_only=False, subset_categories=None):
    """Get all authors for a given row (paper)"""
    if subset_categories:
        cats = get_categories(row, subset_categories)
        subset = [c for c in cats if c in subset_categories]
        if len(subset) == 0:
            authors = None
    else:
        try:
            forenames = [unified_name(i, initials_only=initials_only)
                         for i in row.forenames.split('|')]
            lastnames = row.keyname.split('|')
            authors = [', '.join(i) for i in zip(lastnames, forenames)]
        except AttributeError:  # if a paper has no authors?
            authors = None  # TODO should log this
    return authors


def get_categories(row, subset_categories=None):
    """Get all categories for a given row (paper)"""
    try:
        cats = row.categories.split('|')
        if subset_categories:
            cats = [c for c in cats if c in subset_categories]
    except AttributeError:
        return None  # TODO should log this
    return cats


def get_author_series(df, initials_only=False, extended_info=False):
    """
    Return a pandas Series with author names as the index, containing
    total papers per author

    If ``extended_info`` is True, returns a pandas DataFrame instead
    with the following additional columns:
        * published: papers that were published (have a DOI)
        * mean_sub_time: mean time from record creation in arXiv
          till publication in a journal
        * 2013 IPP, 2013 SJR, 2013 SNIP: mean 2013 impact factors from
          journals of all papers published by the author

    """
    author_counter = {}
    published = {}
    sub_time = {}
    ipp_curr = {}
    sjr_curr = {}
    snip_curr = {}
    ipp_pub = {}
    sjr_pub = {}
    snip_pub = {}

    CURR = '2013'

    def _increase(d, a):
        if a in d:
            d[a] += 1
        else:
            d[a] = 1

    def _add(d, s, what):
        if a in d:
            d[a].append(what)
        else:
            d[a] = [what]

    for index, row in df.iterrows():
        authors = get_authors(row, initials_only=initials_only)
        if authors:
            for a in authors:
                _increase(author_counter, a)
            if extended_info:
                for a in authors:
                    if not pd.isnull(row['doi']):
                        _increase(published, a)
                    _add(sub_time, a, row['till_published'])
                    _add(ipp_curr, a, row[CURR + ' IPP'])
                    _add(sjr_curr, a, row[CURR + ' SJR'])
                    _add(snip_curr, a, row[CURR + ' SNIP'])
                    _add(ipp_pub, a, row['Publication IPP'])
                    _add(sjr_pub, a, row['Publication SJR'])
                    _add(snip_pub, a, row['Publication SNIP'])


    count = pd.Series(author_counter)

    if extended_info:
        result = pd.DataFrame({'total': count})
        result['published'] = pd.Series(published)
        result['published'] = result['published'].fillna(0)
        result['till_published'] = pd.Series(sub_time).map(np.nanmean)
        result[CURR + ' IPP'] = pd.Series(ipp_curr).map(np.nanmean)
        result[CURR + ' SJR'] = pd.Series(sjr_curr).map(np.nanmean)
        result[CURR + ' SNIP'] = pd.Series(snip_curr).map(np.nanmean)
        result['Publication IPP'] = pd.Series(ipp_pub).map(np.nanmean)
        result['Publication SJR'] = pd.Series(sjr_pub).map(np.nanmean)
        result['Publication SNIP'] = pd.Series(snip_pub).map(np.nanmean)
    else:
        result = count

    return result


def get_all_authors(df, initials_only=False):
    """Returns the set of all authors found in `df`."""
    authors = set()
    for index, row in df.iterrows():
        a = get_authors(row, initials_only=initials_only)
        if a:
            for i in a:
                authors.add(i)
    return authors


def get_arxiv_categories():
    path = os.path.join(os.path.dirname(__file__),
                        'arxiv-categories.csv')
    return pd.read_csv(path, index_col=0)


def year_extractor(identifier):
    identifier = str(identifier)
    if '.' in identifier:
        year = int(identifier[0:2])
    else:
        year = int(identifier.split('/')[1][0:2])
    if year > 80:
        year = year + 1900
    else:
        year = year + 2000
    return year
