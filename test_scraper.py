#!/usr/bin/env python3
from scraper import DivarScraper
import config

def test_scraper():
    search_term = 'سمند سورن پلاس'
    print(f'Testing scraper with search term: {search_term}')

    scraper = DivarScraper()
    results = scraper.search_divar(search_term, max_results=5)

    print(f'Found {len(results)} results')

    for i, result in enumerate(results):
        print(f'{i+1}. Title: {result.get("title", "No title")}')
        print(f'   URL: {result.get("url", "No URL")}')
        print(f'   Price: {result.get("price", "No price")}')
        print(f'   Phone: {result.get("phone_number", "No phone")}')
        print()

if __name__ == '__main__':
    test_scraper()