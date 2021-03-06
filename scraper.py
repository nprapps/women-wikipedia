import codecs
import csv
import re
from urlparse import urljoin

from lxml.html import fromstring
from scrapelib import Scraper, FileCache
from slugify import slugify
import unicodecsv

BASE_URL = 'https://en.wikipedia.org/'
BASE_LIST = 'http://en.wikipedia.org/wiki/List_of_former_members_of_the_United_States_House_of_Representatives'
CSV_PATH = 'all_representatives.csv'
LETTERS = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','Y','Z']

s = Scraper(requests_per_minute=60)
s.cache_storage = FileCache('wikipedia_cache')
s.cache_write_only = False


def write_corpus(list):
    response = s.urlopen(list)
    doc = fromstring(response)
    table = doc.find_class('wikitable')[0]
    writer = unicodecsv.writer(open('tmp/%s' % CSV_PATH, 'w'))
    writer.writerow(['first_name', 'last_name', 'wiki_url'])
    for row in table.findall('tr'):
        write_row(row, writer)


def write_row(row, writer):
    tds = row.findall('td')
    try:
        name_cell = tds[0]
        name_anchor = name_cell.findall('a')[0]
        name = name_anchor.text_content()

        # split first name and last name. not worrying about middles
        name_splits = name.split(' ')
        first_name = name.split(' ')[0]

        last_name = name.split(' ')[len(name_splits) - 1]
        # ugh, Jr., etc.
        if last_name == 'Jr.' or last_name == 'Sr.':
            last_name = name.split(' ')[len(name_splits) - 2].split(',')[0]

        # # there are italics in this table we have to account for
        # italics = span.find('i')
        # if italics is not None:
        #     anchor = italics.find('a')
        # else:
        #     anchor = span.find('span').find('a')

        href = name_anchor.attrib['href']
        writer.writerow([first_name, last_name, urljoin(BASE_URL, href)])

    except:
        pass


def read_csv():
    with open('tmp/%s' % CSV_PATH, 'rb') as f:
        reader = csv.DictReader(f, fieldnames=["first_name", "last_name", "wiki_url"])
        for row in reader:
            print row
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

        grep_text('text/%s.txt' % slug, row)


def grep_text(file, row):
    with open(file, 'r') as f:
        searchlines = f.readlines()

    first_name_count = 0
    last_name_count = 0

    for line in searchlines:
        if row['first_name'] in line:
            first_name_count = first_name_count + 1

        if row['last_name'] in line:
            last_name_count = last_name_count + 1

    if last_name_count != 0:
        ratio = (float(first_name_count) / last_name_count)
    else :
        ratio = 0

    print row['first_name'], first_name_count
    print row['last_name'], last_name_count
    print 'ratio', ratio
    print '\n'

    writer = unicodecsv.writer(open('output/%s' % CSV_PATH, 'a'))
    writer.writerow([first_name_count, last_name_count, ratio])


if __name__ == '__main__':
    for letter in LETTERS:
        list = '%s_(%s)' % (BASE_LIST, letter)
        print 'parsing %s' % list
        write_corpus(list)
        read_csv()
