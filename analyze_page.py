import re
from operator import itemgetter

import requests
import validators
from bs4 import BeautifulSoup
from collections import Counter


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


def analyze_brands(page_content):
    soup = BeautifulSoup(page_content, 'html.parser')

    text_elements = soup.find_all(text=True)
    text = ' '.join(text_elements)

    brand_pattern = r"\b[A-Z][a-z]+\b"
    brand_mentions = re.findall(brand_pattern, text)

    brand_counts = Counter(brand_mentions)
    sorted_brand_counts = sorted(brand_counts.items(), key=itemgetter(1), reverse=True)

    return sorted_brand_counts
