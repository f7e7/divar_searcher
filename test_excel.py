#!/usr/bin/env python3
from excel_generator import ExcelGenerator

def test_excel_filtering():
    # Test with actual scraper data
    test_data = [
        {'title': 'سمند سورن پلاس', 'description': '', 'price': 'No Price', 'phone_number': 'Not Available', 'url': 'https://divar.ir/v/test1'},
        {'title': 'کارشناسی ماشین', 'description': '', 'price': 'No Price', 'phone_number': 'Not Available', 'url': 'https://divar.ir/v/test2'},
        {'title': 'سورن پلاس', 'description': '', 'price': 'No Price', 'phone_number': 'Not Available', 'url': 'https://divar.ir/v/test3'},
        {'title': 'سمند سورن پلاس دوگانه', 'description': '', 'price': 'No Price', 'phone_number': 'Not Available', 'url': 'https://divar.ir/v/test4'},
        {'title': 'سورن پلاس صفرتک', 'description': '', 'price': 'No Price', 'phone_number': 'Not Available', 'url': 'https://divar.ir/v/test5'}
    ]

    print('Original data:', len(test_data), 'items')
    generator = ExcelGenerator()
    filtered = generator._filter_and_clean_data(test_data)
    print('Filtered data:', len(filtered), 'items')

    for item in filtered:
        print('- Title:', item['title'])
        print('  Phone:', item['phone_number'])
        print()

    # Create test Excel file
    if filtered:
        filename = generator.create_excel('test_search', filtered)
        print(f'Created test Excel file: {filename}')
    else:
        print('No data to create Excel file')

if __name__ == '__main__':
    test_excel_filtering()
