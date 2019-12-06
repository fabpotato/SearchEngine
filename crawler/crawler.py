import requests
from urllib.parse import urlparse
from pymongo import MongoClient
import nltk
from bs4 import BeautifulSoup


client = MongoClient("localhost", 27017)
db = client["test"]
col = db["Index"]


def _split_to_word(text):
    return [a.lower() for a in nltk.word_tokenize(text)]

def _get_page(url):
    try:
        r = requests.get(url)
        if r.status_code == 200:
            return r.text
    except:
        return None

def _extract_url_links(html):
    soup = BeautifulSoup(html, "html.parser")
    return [a["href"] for a in soup.find_all('a', href = True)]

def add_to_index(keyword, url):
    entry = col.find_one({'keyword': keyword})
    if entry:
        if url not in entry['url']:
            entry['url'].append(url)
            col.save(entry)
        return
    col.insert({'keyword': keyword, 'url': [url]})

def add_page_to_index(url, html):
    # import ipdb; ipdb.set_trace()
    try:
        body_soup = BeautifulSoup(html, "html.parser").find('body')
    except:
        body_soup = None
    if body_soup:
        for child_tag in body_soup.findChildren():
            if child_tag.name == 'script':
                continue
            child_text = child_tag.text
            for line in child_text.split('\n'):
                line = line.rstrip().lstrip()
                for word in _split_to_word(line):
                    add_to_index(word, url)

def crawl_web(seed, max_depth):
    print("#################################")
    print("#  Let it simmer for 5 minutes. #")
    print("#################################")
    up = urlparse(seed)
    base_url = up.scheme + "://" + up.hostname
    to_crawl = {seed}
    crawled = []
    next_depth = []
    depth = 0
    while to_crawl and depth <= max_depth:
        page_url = to_crawl.pop()
        if page_url[0] == "/":
            page_url = base_url + page_url
        if page_url not in crawled:
            print (page_url)
            html = _get_page(page_url)
            if not html:
                continue
            add_page_to_index(page_url, html)
            to_crawl = to_crawl.union(_extract_url_links(html))
            crawled.append(page_url)
        if not to_crawl:
            to_crawl, next_depth = next_depth, []
            depth += 1

crawl_web("https://en.wikipedia.org/wiki/Main_Page",2)
