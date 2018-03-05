#!/usr/bin/python

from bs4 import BeautifulSoup
from urllib2 import urlopen, Request
import threading

class Result:

    def __init__(self, title, datetime, price, key):
        self.title = title
        self.datetime = datetime
        self.price = price
        self.key = key

    def __repr__(self):
        return u'Datetime: {0} --- Title: {1} --- Price: {2}'.format(self.datetime, self.title, self.price).encode('utf8', 'replace')

class SeenSet:
# Very basic wrapper of a set to allow threads to track which results have been seen

    def __init__(self):
        self.seen_set = set()
        self.lock = threading.Lock()

    def add(self, result):
        self.seen_set.add(result.key)

    def contains(self, result):
        return result.key in self.seen_set

    def get_lock(self):
        return self.lock


def get_craigslist_ads(location_code, search_code):
    url_base = "https://" + location_code + ".craigslist.org/search/" + search_code
    return get_result_list(url_base)

def get_result_list(url_base):
    top_soup = get_soup(url_base)
    highest_first_page_index = int(top_soup.find("span", class_="rangeTo").text)
    total_count = int(top_soup.find("span", class_="totalcount").text)
    number_of_pages = get_number_of_pages(highest_first_page_index, total_count)
    result_list = []
    seen_set = SeenSet()
    threads = []

    for page in xrange(number_of_pages):
        s = page*highest_first_page_index
        url = url_base + "?s=" + str(s)
        thread = threading.Thread(target=thread_action, args=(url, result_list, seen_set))
        threads.append(thread)
        thread.start()
    for thread in threads:
        thread.join()

    return result_list

def thread_action(url, result_list, seen_set):
    soup = get_soup(url)
    for entry in soup.find_all("li", class_="result-row"):
        result = get_result_from_entry(entry)
        if result is not None:
            seen_set.get_lock().acquire()
            if not seen_set.contains(result):
                result_list.append(result)
                seen_set.add(result)
            seen_set.get_lock().release()

def get_result_from_entry(entry):
    try:
        title = entry.p.a.text
        datetime = entry.p.time.get("datetime")
        price = price_string_to_price(entry.find("span", class_="result-price").text)
        key = toSetKey(title, price)
        return Result(title, datetime, price, key)
    except:
        return None

def price_string_to_price(price_string):
    return int(price_string[1:])

def toSetKey(title, price):
    return title + str(price)

def get_number_of_pages(highest_first_page_index, total_count):
    if highest_first_page_index == 0:
        return 0
    extra = 1 if total_count%highest_first_page_index > 0 else 0
    return total_count/highest_first_page_index + extra

def get_soup(url):
    req = Request(url, headers={'User-Agent' : "Magic Browser"})
    html = urlopen(req).read()
    soup = BeautifulSoup(html,"lxml")
    return soup

