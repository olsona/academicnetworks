"""
Functionality to get information from a given DOI

"""

import datetime

import pandas as pd
import requests


class DOIScraper(object):
    def __init__(self):
        super(DOIScraper, self).__init__()
        self.base_url = 'http://api.crossref.org/works/'

    def get_doi(self, doi):
        url = self.base_url + str(doi)
        r = requests.get(url)
        try:
            result = pd.read_json(r.text)
        except ValueError:  # if DOI does not exist
            result = None
        return result


def process_date(df, create_datetime_object=False):
    """Attempts to return `issued` date if available, else None"""
    try:
        found = df.at['issued', 'message']['date-parts'][0]
        if create_datetime_object:
            dates = [1, 1, 1]  # year, month, day
            for i in range(len(found)):
                dates[i] = found[i]
            found = datetime.datetime(*dates)
    except KeyError:
        found = None
    return found
