import re
from urlparse import urljoin

from lxml.html import fromstring
from scrapelib import Scraper, FileCache
import unicodecsv

BASE_URL = 'https://en.wikipedia.org/'
WOMEN_LIST = 'https://en.wikipedia.org/wiki/List_of_elected_or_appointed_female_heads_of_state'
CSV_PATH = 'women.csv'

s = Scraper(requests_per_minute=60)
s.cache_storage = FileCache('wikipedia_cache')
s.cache_write_only = False

def write_corpus():
    response = s.urlopen(WOMEN_LIST)
    doc = fromstring(response)
    table = doc.find_class('wikitable')[0]
    writer = unicodecsv.writer(open('women.csv', 'w'))
    writer.writerow(['name', 'wiki_url'])
    for row in table.findall('tr'):
        write_row(row, writer)


def write_row(row, writer):
    tds = row.findall('td')
    try:
        name_cell = tds[0]
        name = tds[0].text_content()

        # there are italics in this table we have to account for
        italics = name_cell.find('i')
        if italics is not None:
            anchor = italics.find('a')
        else:
            anchor = name_cell.find('a')

        href = anchor.attrib['href']

        writer.writerow([name, urljoin(BASE_URL, href)])

    except:
        pass


if __name__ == '__main__':
    write_corpus()