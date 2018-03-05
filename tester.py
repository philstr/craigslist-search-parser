#!/usr/bin/python

import craigslist

TEST_LOCATION_CODE = "boston"
TEST_SEARCH_CODE = "bka"

# Sample usage
def basic_case():
	for result in craigslist.get_craigslist_ads(TEST_LOCATION_CODE, TEST_SEARCH_CODE):
		print result

if __name__ == '__main__':
	basic_case()