import codecs
import csv
import re
from urlparse import urljoin

from lxml.html import fromstring
from scrapelib import Scraper, FileCache
from slugify import slugify
import unicodecsv

BASE_URL = 'https://en.wikipedia.org/'
WOMEN_LIST = 'http://en.wikipedia.org/wiki/List_of_female_governors_in_the_United_States'
CSV_PATH = 'women.csv'

s = Scraper(requests_per_minute=60)
s.cache_storage = FileCache('wikipedia_cache')
s.cache_write_only = False


def write_corpus():
    response = s.urlopen(WOMEN_LIST)
    doc = fromstring(response)
    table = doc.find_class('wikitable')[0]
    writer = unicodecsv.writer(open(CSV_PATH, 'w'))
    writer.writerow(['first_name', 'last_name', 'wiki_url'])
    for row in table.findall('tr'):
        write_row(row, writer)

def write_row(row, writer):
    tds = row.findall('td')
    try:
        name_cell = tds[1]
        name = tds[1].text_content()

        first_name = name.split(' ', 1)[0]
        last_name = name.split(' ', 1)[1]

        # there are italics in this table we have to account for
        italics = name_cell.find('i')
        if italics is not None:
            anchor = italics.find('a')
        else:
            anchor = name_cell.find('a')

        href = anchor.attrib['href']

        writer.writerow([first_name, last_name, urljoin(BASE_URL, href)])

    except:
        pass


def read_csv():
    with open(CSV_PATH, 'rb') as f:
        reader = csv.DictReader(f, fieldnames=["first_name", "last_name", "wiki_url"])
        for row in reader:
            parse_wiki(row)


def parse_wiki(row):
    # header
    if row['first_name'] != 'first_name':
        full_name = '%s %s' % (row['first_name'], row['last_name'])
        slug = slugify(full_name)

    # header
    if row['wiki_url'] != 'wiki_url':
        response = s.urlopen(row['wiki_url'])
        doc = fromstring(response)
        text_div = doc.get_element_by_id('mw-content-text')

        paragraphs = text_div.findall('p')
        text = ''
        for graph in paragraphs:
            text += '\n %s' % graph.text_content()

        f = codecs.open('text/%s.txt' % slug, 'w', encoding='utf-8')
        f.write(text)
        f.close()


if __name__ == '__main__':
    write_corpus()
    read_csv()
