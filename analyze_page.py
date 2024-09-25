import re
from operator import itemgetter
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import requests
import validators
from bs4 import BeautifulSoup
from collections import Counter
from selenium import webdriver

# creates selenium service
service = Service(ChromeDriverManager().install())


def analyze_page_with_selenium(my_ulr: str):
    driver = webdriver.Chrome(service=service)

    try:

        # all code for work
        driver.get(my_ulr)
        page_content = driver.page_source
        print(f'\n\n page content from SELENIUM: \n \n {page_content}')


    except Exception as ex:
        print(ex)
    finally:
        driver.close()
        driver.quit()


def get_page_content(url):
    if not validators.url(url):
        raise ValueError("this is an invalid URL")

    try:
        response = requests.get(url, allow_redirects=True)
        response.raise_for_status()

        if response.status_code == 200:
            print(f'full text of response: {response.text}')
            return response.text
        else:
            return None
    except requests.exceptions.RequestException as e:
        print(f'Error fetching the page: {e}')
        return None


def analyze_brands_with_bs4(page_content):
    soup = BeautifulSoup(page_content, 'html.parser')

    text_elements = soup.find_all(text=True)
    text = ' '.join(text_elements)

    brand_pattern = r"\b[A-Z][a-z]+\b"
    brand_mentions = re.findall(brand_pattern, text)

    brand_counts = Counter(brand_mentions)
    sorted_brand_counts = sorted(brand_counts.items(), key=itemgetter(1), reverse=True)

    return sorted_brand_counts
