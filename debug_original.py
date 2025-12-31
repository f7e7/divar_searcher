#!/usr/bin/env python3
from scraper import DivarScraper
from excel_generator import ExcelGenerator

def debug_original_issue():
    search_term = 'سمند سورن پلاس'
    print(f'Debugging original issue for: {search_term}')

    # Scrape data
    scraper = DivarScraper()
    raw_results = scraper.search_divar(search_term, max_results=20)  # More results
    print(f'Raw results: {len(raw_results)}')

    # Show all results before filtering
    print('All raw results:')
    for i, result in enumerate(raw_results):
        title = result.get('title', '').strip()
        url = result.get('url', '').strip()
        phone = result.get('phone_number', '')
        print(f'{i+1}. Title: "{title}" | URL: {url} | Phone: {phone}')

    # Apply filtering
    generator = ExcelGenerator()
    filtered_results = generator._filter_and_clean_data(raw_results)
    print(f'After filtering: {len(filtered_results)} results')

    # Show what got filtered
    print('Filtering analysis:')
    removed_count = 0
    for result in raw_results:
        title = result.get('title', '').strip()
        url = result.get('url', '').strip()

        reasons = []
        if not title:
            reasons.append('no title')
        elif title.lower() in ['no title', 'بدون عنوان', '']:
            reasons.append('invalid title')
        if not url:
            reasons.append('no url')

        if reasons:
            print(f'REMOVED: "{title}" - Reasons: {", ".join(reasons)}')
            removed_count += 1

    print(f'Total removed: {removed_count}')
    print(f'Total kept: {len(filtered_results)}')

if __name__ == '__main__':
    debug_original_issue()
