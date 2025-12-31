import requests
from bs4 import BeautifulSoup
import time
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import config

class DivarScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': config.USER_AGENT,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })

    def search_divar(self, search_term, max_results=config.MAX_RESULTS, city='tehran'):
        """
        Search divar.ir for a given term and return results
        """
        results = []

        try:
            # Use Selenium directly (Divar uses JavaScript)
            results = self._search_with_selenium(search_term, max_results, city)
            print(f"Selenium scraping found {len(results)} results")
        except Exception as e:
            print(f"Selenium scraping failed: {e}")
            try:
                # Fallback to requests if Selenium fails
                results = self._search_with_requests(search_term, max_results, city)
                print(f"Requests scraping found {len(results)} results")
            except Exception as e2:
                print(f"Requests scraping also failed: {e2}")
                return []

        return results[:max_results]

    def _search_with_requests(self, search_term, max_results, city='tehran'):
        """
        Search using requests library
        """
        search_url = f"{config.DIVAR_BASE_URL}/s/{city}?q={search_term}"

        response = self.session.get(search_url, timeout=config.REQUEST_TIMEOUT)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')

        results = []
        # Find advertisement containers - try different selectors
        ads = soup.find_all('a', class_=re.compile(r'kt-post-card|post-card'))
        if not ads:
            # Fallback to div containers
            ads = soup.find_all('div', class_=re.compile(r'post-card|kt-post-card'))
            print(f"Using div selector, found {len(ads)} elements")
        else:
            print(f"Using link selector, found {len(ads)} elements")

        for ad in ads:
            if len(results) >= max_results:
                break

            ad_data = self._extract_ad_data_requests(ad)
            if ad_data:
                results.append(ad_data)

        return results

    def _search_with_selenium(self, search_term, max_results, city='tehran'):
        """
        Search using Selenium for dynamic content
        """
        chrome_options = Options()

        # Add headless mode if configured
        if config.CHROME_HEADLESS:
            chrome_options.add_argument("--headless")

        # Add configured Chrome options
        for option in config.CHROME_OPTIONS:
            chrome_options.add_argument(option.strip())

        # Set user agent
        chrome_options.add_argument(f"user-agent={config.USER_AGENT}")

        driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)

        try:
            search_url = f"{config.DIVAR_BASE_URL}/s/{city}?q={search_term}"
            driver.get(search_url)

            # Wait for content to load
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'a[href*="/v/"]'))
            )

            # Scroll to load more results
            for _ in range(3):  # Scroll 3 times to load more
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)

            soup = BeautifulSoup(driver.page_source, 'html.parser')
            results = []

            # Find advertisement links
            ads = soup.find_all('a', href=re.compile(r'/v/'))

            for ad in ads:
                if len(results) >= max_results:
                    break

                ad_data = self._extract_ad_data_selenium(ad, driver)
                if ad_data:
                    results.append(ad_data)

            return results

        finally:
            driver.quit()

    def _extract_ad_data_requests(self, ad_element):
        """
        Extract data from a single advertisement element using requests
        """
        try:
            # Extract title/name
            title_elem = ad_element.find('h2') or ad_element.find(class_=re.compile(r'title|kt-post-card__title'))
            title = title_elem.get_text(strip=True) if title_elem else ""

            # Skip if no title
            if not title or title.lower() in ['no title', 'بدون عنوان', '']:
                return None

            # Extract description
            desc_elem = ad_element.find('p') or ad_element.find(class_=re.compile(r'description|kt-post-card__description'))
            description = desc_elem.get_text(strip=True) if desc_elem else "No Description"

            # Extract price if available
            price_elem = ad_element.find(class_=re.compile(r'price|kt-post-card__price'))
            price = price_elem.get_text(strip=True) if price_elem else "No Price"

            # Extract link to get phone number
            if ad_element.name == 'a' and ad_element.get('href'):
                # If ad_element is already a link
                ad_url = ad_element['href']
                if not ad_url.startswith('http'):
                    ad_url = config.DIVAR_BASE_URL + ad_url
                phone_number = self._get_phone_number(ad_url)
            else:
                # Find link within the element
                link_elem = ad_element.find('a', href=True)
                phone_number = "در حال استخراج..."

                ad_url = ""
                if link_elem:
                    ad_url = link_elem['href']
                    if not ad_url.startswith('http'):
                        ad_url = config.DIVAR_BASE_URL + ad_url

                    # Try to get phone number immediately
                    phone_number = self._get_phone_number(ad_url)

            return {
                'title': title,
                'description': description,
                'price': price,
                'phone_number': phone_number,
                'url': ad_url
            }

        except Exception as e:
            print(f"Error extracting ad data: {e}")
            return None

    def _extract_ad_data_selenium(self, ad_element, driver):
        """
        Extract data from a single advertisement link using Selenium
        """
        try:
            # ad_element is now a link <a>
            ad_url = ad_element.get('href')
            if not ad_url:
                return None

            if not ad_url.startswith('http'):
                ad_url = config.DIVAR_BASE_URL + ad_url

            # Extract title from link text
            title = ad_element.get_text(strip=True)
            if not title:
                return None

            # Get description and price from the element content
            description = ""
            price = "No Price"

            # Try to get more details by clicking or parsing the element
            try:
                # Look for price in the element
                price_elem = ad_element.find_next_sibling() or ad_element.find_parent().find(class_=re.compile(r'price|amount'))
                if price_elem:
                    price = price_elem.get_text(strip=True)
            except:
                pass

            # Try to get phone number
            phone_number = self._get_phone_number(ad_url)

            return {
                'title': title,
                'description': description,
                'price': price,
                'phone_number': phone_number,
                'url': ad_url
            }

        except Exception as e:
            print(f"Error extracting Selenium ad data: {e}")
            return None

    def _get_phone_number(self, ad_url):
        """
        Get phone number from individual advertisement page
        """
        try:
            response = self.session.get(ad_url, timeout=config.REQUEST_TIMEOUT)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # Look for phone number patterns
            phone_patterns = [
                r'(\+98|0)?9\d{9}',  # Iranian mobile numbers
                r'0\d{2,3}-\d{7,8}',  # Landline numbers
            ]

            text_content = soup.get_text()

            for pattern in phone_patterns:
                matches = re.findall(pattern, text_content)
                if matches:
                    # Clean and format the phone number
                    phone = matches[0]
                    if phone.startswith('+98'):
                        phone = '0' + phone[3:]
                    return phone

            # Try to find phone in specific elements
            phone_elem = soup.find(class_=re.compile(r'phone|contact|kt-contact'))
            if phone_elem:
                phone_text = phone_elem.get_text(strip=True)
                # Extract phone number from text
                for pattern in phone_patterns:
                    match = re.search(pattern, phone_text)
                    if match:
                        phone = match.group()
                        if phone.startswith('+98'):
                            phone = '0' + phone[3:]
                        return phone

            return "Not Available"

        except Exception as e:
            print(f"Error getting phone number from {ad_url}: {e}")
            return "Not Available"
