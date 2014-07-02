"""
Scraping and processing arXiv data

"""

import glob
import os

import pandas as pd


class ArxivScraper(object):
    """OAI scraper for arXiv metadata"""
    def __init__(self, metadataPrefix='arXiv',
                 base_url='http://export.arxiv.org/oai2'):
        super(ArxivScraper, self).__init__()
        from sickle import Sickle
        self.sickle = Sickle(base_url)
        self.records = self.sickle.ListRecords(metadataPrefix=metadataPrefix)

    def set_resumption_token(self, token):
        old_token = self.records.resumption_token
        self.records.resumption_token = old_token.split('|')[0] + '|' + token
        print 'New resumption token: {}'.format(self.records.resumption_token)

    def scrape(self, output_dir='arxiv'):
        df = None
        repeater = 0
        for r in self.records:
            if r.deleted:
                continue  # Skip deleted records
            if df is None:
                df = pd.DataFrame(pd.Series(r.metadata)).T
            else:
                df = df.append(pd.Series(r.metadata), ignore_index=True)
            repeater += 1
            if repeater % 1000 == 0:
                df.index = range(repeater - 1000, repeater)
                save_path = os.path.join(output_dir,
                                         '{:0>5d}.csv'.format(repeater / 1000))
                df.to_csv(save_path, encoding='utf-8')
                df = None


def clean_arxiv_data(in_dir, out_dir,
                     years=range(90, 100) + range(0, 14)):
    """
    Clean arXiv data downloaded with the OAI scraper

    Concatenates all CSV files found in ``in_dir``,
    then saves data as yearly CSV files to ``out_dir``

    ``years``: list of years for which to save data, as short (YY)
    integers. Defaults to (19)90 through (20)13.

    """
    files = glob.glob(os.path.join(in_dir, '*'))

    # Concatenate all files into one dataframe
    df = pd.read_csv(files[0], index_col=0, encoding='utf-8')

    for f in files[1:]:
        df = pd.concat([df, pd.read_csv(f, index_col=0,
                                        encoding='utf-8')], ignore_index=True)

    # Clean columns that are list-strings with single entries
    for c in ['abstract', 'comments', 'created', 'doi', 'id', 'journal-ref',
              'license', 'msc-class', 'report-no', 'suffix', 'title',
              'updated']:
        df[c] = df[c].map(list_cleaner())

    df.categories = df.categories.map(list_cleaner(' '))

    for c in ['keyname', 'forenames']:
        df[c] = df[c].map(list_cleaner(', ', remove_quotes=True))

    df = df.drop(['author', 'authors'], axis=1)

    df = df.set_index('id')

    # Just to make sure it's nicely sorted
    df = df.sort_index(ascending=True)

    # Make simplified idstring for choosing years
    # id new: 0710.3056 --> stays same
    # id old: physics/0401059 --> 0401059
    df['idstring'] = df.index.map(lambda x: x.split('/')[-1])

    # Write a file per year
    for y in years:
        if y > 80:
            baseyear = 1900
        else:
            baseyear = 2000
        fname = 'arxiv-{:0>2d}.csv'.format(y + baseyear)
        df_write = df[df.idstring.str.startswith('{:0>2d}'.format(y))]
        csv_path = os.path.join(out_dir, fname)
        df_write.drop(['idstring'], axis=1).to_csv(csv_path,
                                                   encoding='utf-8')
        csv_path = os.path.join(out_dir, 's-' + fname)
        df_write.drop(['idstring', 'abstract', 'comments'],
                      axis=1).to_csv(csv_path, encoding='utf-8')


##
# Helper functions for clean_arxiv_data
##

def list_cleaner(listify=False, remove_quotes=False):
    def _cleaner(s):
        try:
            cleaned = s.strip("['").strip("']")
        except AttributeError:  # if it's e.g. a float / np.nan
            return s
        if listify:
            # Split along whatever passed in
            cleaned = '|'.join(cleaned.split(listify))
        if remove_quotes:
            cleaned = cleaned.replace("'", '')
            cleaned = cleaned.replace('"', '')
        return cleaned
    return _cleaner
