import requests
from bs4 import BeautifulSoup
import sys
import os
import time
from collections import deque
from urllib.parse import urljoin, urlparse
import re
import urllib.robotparser

headers = {'User-Agent': 'CS172_CATEGORY1Scraper/0.0 (email@email.com)'}
robot_parser_list = {}

def get_base_url(url):
    parsed_url = urlparse(url)
    return f"{parsed_url.scheme}://{parsed_url.netloc}"

def robot_txt_parser(url):
    base_url = get_base_url(url)
    if base_url not in robot_parser_list:
        rp = urllib.robotparser.RobotFileParser()
        robot_url = urljoin(base_url, "/robots.txt")
        rp.set_url(robot_url)

        try: 
            response = requests.get(robot_url, headers=headers,timeout=5, allow_redirects=True)
            response.raise_for_status()
            rp.parse(response.text.splitlines())
        except Exception as e:
            print(f"Error reading robots.txt from {robot_url}: {e}")
        robot_parser_list[base_url] = rp
    return robot_parser_list[base_url]

def rp_can_fetch(url):
    rp = robot_txt_parser(url)
    return rp.can_fetch(headers["User-Agent"], url)

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

    #check robot.txt
    if not rp_can_fetch(website):
        print(f"Skipping {website}, restricted by robots.txt.")
        continue


    page = requests.get(website, headers=headers)
    html_file = page.text

    soup = BeautifulSoup(page.content, "html.parser")
    title = soup.title.string
    # clean title to replace all non word, space, or hyphen chars with underscore
    clean_title = re.sub(r'[^\w]', '_', title)
    clean_title = re.sub(r'_+', '_', clean_title)  # remove multiple underscores in a row

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