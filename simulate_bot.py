#!/usr/bin/env python3
from scraper import DivarScraper
from excel_generator import ExcelGenerator

def simulate_bot_process():
    search_term = 'سمند سورن پلاس'
    print(f'Searching for: {search_term}')

    scraper = DivarScraper()
    results = scraper.search_divar(search_term)
    print(f'Found {len(results)} results from scraper')

    if results:
        generator = ExcelGenerator()
        excel_file = generator.create_excel(search_term, results)
        print(f'Excel file created: {excel_file}')

        # Check if file exists and has data
        import os
        if os.path.exists(excel_file):
            import openpyxl
            wb = openpyxl.load_workbook(excel_file)
            ws = wb.active
            print(f'File has {ws.max_row - 1} data rows')
            print('SUCCESS: File created with data!')
        else:
            print('ERROR: File was not created!')
    else:
        print('ERROR: No results found!')

if __name__ == '__main__':
    simulate_bot_process()
