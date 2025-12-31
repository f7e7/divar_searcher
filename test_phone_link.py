#!/usr/bin/env python3
from excel_generator import ExcelGenerator

def test_phone_link_logic():
    # Test data with missing phone numbers
    test_data = [
        {
            'title': 'آگهی با شماره تلفن',
            'description': 'تست',
            'price': '۱۰۰۰۰۰',
            'phone_number': '09123456789',
            'url': 'https://divar.ir/v/test1'
        },
        {
            'title': 'آگهی بدون شماره',
            'description': 'تست',
            'price': '۲۰۰۰۰۰',
            'phone_number': 'Not Available',
            'url': 'https://divar.ir/v/test2'
        },
        {
            'title': 'آگهی خالی',
            'description': 'تست',
            'price': '۳۰۰۰۰۰',
            'phone_number': '',
            'url': 'https://divar.ir/v/test3'
        }
    ]

    generator = ExcelGenerator()
    filtered = generator._filter_and_clean_data(test_data)

    print('Test Results:')
    for item in filtered:
        print(f"Title: {item['title']}")
        print(f"Phone/Link: {item['phone_number']}")
        print('---')

    # Create test Excel file
    if filtered:
        excel_file = generator.create_excel('test_phone_link', filtered)
        print(f'Created test file: {excel_file}')

if __name__ == '__main__':
    test_phone_link_logic()
