#!/usr/bin/env python3
from scraper import DivarScraper
from excel_generator import ExcelGenerator

def test_full_flow():
    search_term = 'سمند سورن پلاس'
    print(f'Testing full flow for: {search_term}')

    # Step 1: Scrape data
    scraper = DivarScraper()
    raw_results = scraper.search_divar(search_term, max_results=10)
    print(f'Step 1 - Scraped {len(raw_results)} raw results')

    for i, result in enumerate(raw_results[:3]):  # Show first 3
        print(f'  {i+1}. {result.get("title", "No title")}')

    # Step 2: Filter data
    generator = ExcelGenerator()
    filtered_results = generator._filter_and_clean_data(raw_results)
    print(f'Step 2 - Filtered to {len(filtered_results)} results')

    # Step 3: Create Excel
    if filtered_results:
        excel_file = generator.create_excel(search_term, filtered_results)
        print(f'Step 3 - Excel created: {excel_file}')

        if excel_file:
            print('✅ Success: Excel file created successfully!')
        else:
            print('❌ Failed: Excel creation returned None')
    else:
        print('❌ Failed: No data after filtering')

if __name__ == '__main__':
    test_full_flow()
