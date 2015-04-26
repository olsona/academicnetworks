"""
Functions to process and analyze arXiv data

"""
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals


import logging
import glob
import os
import uuid

import numpy as np
import pandas as pd


def read_all_arxiv_files(glob_pattern='arxiv/s-*.csv'):
    files = glob.glob(glob_pattern)
    dfs = []
    for f in files:
        logging.debug('Processing file: {}'.format(f))
        df = pd.read_csv(f,
                         # Force strings so that str('01') doesn't become int(1)
                         dtype={'id': object},
                         encoding='utf-8')
        df = df.set_index('id')
        df['year'] = df.index.map(year_extractor)
        dfs.append(df)

    df = pd.concat(dfs)
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


def get_authors(row, initials_only=False, subset_categories=None,
                unify_names=False):
    """Get all authors for a given row (paper)"""
    ino = initials_only
    if subset_categories:
        cats = get_categories(row, subset_categories)
        subset = [c for c in cats if c in subset_categories]
        if len(subset) == 0:
            authors = None
    else:
        try:
            if unify_names:
                forenames = [unified_name(i, initials_only=ino).replace(',', '')
                             for i in row.forenames.split('|')]
            else:
                forenames = [i.replace(',', '')
                             for i in row.forenames.split('|')]
            lastnames = [i.replace(',', '')
                         for i in row.keyname.split('|')]
            authors = [', '.join(i)  #.replace(',,', ',')
                       for i in zip(lastnames, forenames)]
        except AttributeError:  # if a paper has no authors?
            authors = None  # TODO should log this
    return authors


def get_categories(row, subset_categories=None, toplevel=False):
    """Get all categories for a given row (paper)"""
    try:
        cats = row.categories.split('|')
        if subset_categories:
            cats = [c for c in cats if c in subset_categories]
        if toplevel:
            cats = [c.split('.')[0] for c in cats]
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

    CURR = '2013'  # 'Current' year for IPP, SJR and SNIP metadata

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


def _add_paper(author_counter, author, item):
        if author in author_counter:
            if item in author_counter[author]:
                author_counter[author][item] += 1
            else:
                author_counter[author][item] = 1
        else:
            author_counter[author] = {item: 1}


def get_author_year_data(df):
    """
    Return a pandas dataframe of paper counts, with dimensions:
        1) author names (raw from arxiv)
        2) years

    Each (name, year) coordinate is either an integer (number of papers
    published by name in year) or NaN.

    """
    author_counter = {}  # Contains a dict per author with (cat, year) keys

    for index, row in df.iterrows():
        authors = get_authors(row, initials_only=False)
        y = row['year']
        if authors:
            for a in authors:
                _add_paper(author_counter, a, y)

    return author_counter


def get_author_metadata(df):
    """
    Return a pandas dataframe with author name strings as index, and
    author categories, coauthors, and total publication counts.

    """
    author_cats = {}
    author_count = {}
    author_coauthors = {}

    for index, row in df.iterrows():
        authors = get_authors(row, initials_only=False)
        fields = row['categories'].split('|')
        if authors:
            for a in authors:
                # Cats
                for f in fields:
                    _add_paper(author_cats, a, f)
                # Total publications
                if a in author_count:
                    author_count[a] += 1
                else:
                    author_count[a] = 1
                # Coauthors
                if a in author_coauthors:
                    author_coauthors[a] |= set(authors)
                else:
                    author_coauthors[a] = set(authors)

    author_md = pd.DataFrame({'count': pd.Series(author_count),
                              'categories': pd.Series(author_cats),
                              'coauthors': pd.Series(author_coauthors)})

    return author_md


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
    assert isinstance(identifier, basestring), 'ID must be string'
    # if not isinstance(identifier, basestring):
    #     identifier = str(identifier)
    #     logging.debug('Forced id `{}` to string'.format(identifier))
    if '.' in identifier:
        year = int(identifier[0:2])
    else:
        year = int(identifier.split('/')[1][0:2])
    if year > 80:
        year = year + 1900
    else:
        year = year + 2000
    return year


def get_uuid():
    """Generate a random unique identifier"""
    return str(uuid.uuid4())


def get_name_with_initials_only(name):
    n, f = name.split(',')
    return ', '.join((n, f.strip()[0]))


def get_initials(name):
    return ''.join([i[0:1] for i in name.split(',')[1].strip().split(' ')])


def get_name_matches(author_md):
    """Warning: modifies author_md in-place! But also returns name_matches."""
    # Get "Forename, Initial" set of all names
    name_match_keys = set(get_name_with_initials_only(i)
                          for i in author_md.name.tolist())

    name_match_keys = sorted(list(name_match_keys))

    # Go through the match keys and get a list of dataframes grouping
    # potentially matching names
    name_matches = []

    i = 0
    while i < len(author_md):
        this_name = get_name_with_initials_only(author_md.iloc[i].name)
        # Look 200 names ahead, this covers also prolific Chinese names
        comparison_df = author_md.iloc[i:i+200]
        match_df = comparison_df[comparison_df.name.str.startswith(this_name)]
        if len(match_df) > 1:
            name_matches.append(match_df)
            # Can skip the rest of this match df and move
            # on the the next surname, initial
            i += len(match_df)
        else:
            # There are no potential matches, i.e. only the
            # "Forename, Initial" variant of the name exists
            # We can therefore generate a UUID for the name and add it to
            # the name's metadata, and be done with this name
            this_name_id = match_df.ix[0, 'name']
            author_md.at[this_name_id, 'uuid'] = get_uuid()
            i += 1

    return name_matches


def process_match(match, author_md, cab_threshold=0.5):
    """Try to find author names that point to the same person"""

    # lastname_set = lambda x: set(i.split(',')[0] for i in x)
    lastname_set = lambda x: set(get_name_with_initials_only(i) for i in x)

    debug_str = '{} match for {} and {} on {}.'
    initial_name = True

    while len(match) > 0:
        start_name = match.ix[0]
        # Check: if the start_name is a single initial and has too many
        # publcations, we can only assume that it's several people already,
        # and we don't want to further aggregate it, so we skip the entire
        # block inside the `if` statement in that case
        matches = [start_name.name]  # Add the start_name, it "matches itself"
        # allowed papers for a single initial start_name depend on the number
        # of names in this match set
        allowed_papers = max(10, len(match))
        if (initial_name and
                len(start_name.name.split(',')[1].strip().replace('.', '')) == 1
                and len(match) <= allowed_papers):
            author_md.loc[matches, 'flag'] = 1  # Flag as potential problem
        else:
            cat_a = set(start_name.categories.keys())
            coauthors_a = lastname_set(start_name['coauthors'])
            initials_a = get_initials(start_name.name)

            for index, m in match.ix[1:].iterrows():
                this_coauthors = lastname_set(m['coauthors'])
                this_cat = set(m.categories.keys())
                # Check whether the names are potential matches, by comparing
                # the initials
                this_initials = get_initials(m.name)
                compare_len = max(len(this_initials), len(initials_a))
                initials_match = (this_initials[0:compare_len]
                                  == initials_a[0:compare_len])
                firstname_a = start_name.name.split(',')[1].strip('.')
                firstname_b = m.name.split(',')[1].strip('.')
                firstnames_contain = (firstname_a.startswith(firstname_b)
                                      or firstname_b.startswith(firstname_a))
                if initials_match and firstnames_contain:
                    # First, match by coauthors
                    m_coauthors = (coauthors_a & this_coauthors)
                    if len(m_coauthors) > 1:
                        matches.append(m.name)
                        logging.debug(debug_str.format('Coauthor',
                                                       start_name.name,
                                                       m.name, m_coauthors))
                        # Update the comparison sets
                        coauthors_a = coauthors_a | this_coauthors
                        cat_a = cat_a | this_cat
                    else:
                        # If no coauthor matches, look at categories
                        m_cats = cat_a & this_cat
                        cab = len(m_cats) * max(1.0 / len(cat_a),
                                                1.0 / len(this_cat))
                        if cab >= cab_threshold:
                            matches.append(m.name)
                            logging.debug(debug_str.format('Category',
                                                           start_name.name,
                                                           m.name, m_cats))
                            # Update the comparison sets
                            coauthors_a = coauthors_a | this_coauthors
                            cat_a = cat_a | this_cat

        # Update author metadata with a new UUID
        # NB if neither a coauthor nor a category match was found,
        # `matches` will still be just the start_name,
        # so it will get a UUID by itself
        author_md.loc[matches, 'uuid'] = get_uuid()

        # Remove matches from match dataframe
        match = match.drop(matches, axis=0)
        initial_name = False
