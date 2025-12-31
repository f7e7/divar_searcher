#!/usr/bin/env python3
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import config

def test_selenium():
    print('Testing Selenium...')
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')

    try:
        driver = webdriver.Chrome(options=chrome_options)
        print('Chrome started successfully')

        driver.get('https://divar.ir/s/tehran?q=سمند')
        print('Page loaded')

        # Wait for content to load
        import time
        time.sleep(5)

        # Find posts - try different selectors
        selectors = [
            'a[href*="/v/"]',
            '.kt-post-card__action',
            '[data-testid="post-card"]',
            '.post-card-item'
        ]

        for selector in selectors:
            try:
                posts = driver.find_elements(By.CSS_SELECTOR, selector)
                if posts:
                    print(f'Found {len(posts)} posts with selector: {selector}')
                    for i, post in enumerate(posts[:3]):
                        try:
                            href = post.get_attribute('href') or post.find_element(By.TAG_NAME, 'a').get_attribute('href')
                            text = post.text[:50] if post.text else 'No text'
                            print(f'  {i+1}. {text}... -> {href}')
                        except:
                            print(f'  {i+1}. Could not extract data')
                    break
            except Exception as e:
                print(f'Selector {selector} failed: {e}')
                continue

        driver.quit()
        print('Selenium test completed')

    except Exception as e:
        print(f'Selenium error: {e}')

if __name__ == '__main__':
    test_selenium()
