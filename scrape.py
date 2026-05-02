import requests
from bs4 import BeautifulSoup
import sys
import os
import time
from collections import deque
from urllib.parse import urljoin
import re

headers = {'User-Agent': 'CS172_CATEGORY1Scraper/0.0 (email@email.com)'}

seed_urls = sys.argv[1]
max_pages = int(sys.argv[2])
max_hops = int(sys.argv[3])
output_dir = sys.argv[4]

# create output directory if it does not exist
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# store url and level
frontier = deque([(url, 0) for url in open(seed_urls).read().splitlines()])
visited = set()
pages_crawled = 0

while frontier and pages_crawled < max_pages:
    website, curr_hop = frontier.popleft()

    if website in visited or curr_hop > max_hops:
        continue

    page = requests.get(website, headers=headers)
    html_file = page.text

    soup = BeautifulSoup(page.content, "html.parser")
    title = soup.title.string
    # clean title to replace all non word, space, or hyphen chars with underscore
    clean_title = re.sub(r'[^\w\s-]', '_', title)

    file_path = os.path.join(output_dir, f"{clean_title}.html")

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(html_file)

    visited.add(website)
    pages_crawled += 1

    for link in soup.find_all('a', href=True):
        # skip images
        if link.find('img'):
            continue

        href = link.get('href')

        # only add links to other wikipedia articles
        if href.startswith('/wiki') and ':' not in href:
            full_url = urljoin("https://en.wikipedia.org", href)
            if full_url not in visited:
                frontier.append((full_url, curr_hop+1))

    time.sleep(1)