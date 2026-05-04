import requests
from bs4 import BeautifulSoup
import sys
import os
import time
from collections import deque
from urllib.parse import urljoin, urlparse, urlunparse
import re
import urllib.robotparser
import threading
import queue
from utils import normalize_url, save_json_file, extract_text_content, parse_folder

encoding = "utf-8"
headers = {'User-Agent': 'CS172_CATEGORY1Scraper/0.0 (email@email.com)'}
robot_parser_list = {}
visited_lock = threading.Lock()  
robot_lock = threading.Lock()

def get_base_url(url):
    parsed_url = urlparse(url)
    return f"{parsed_url.scheme}://{parsed_url.netloc}"

def robot_txt_parser(url):
    base_url = get_base_url(url)
    with robot_lock:
        if base_url in robot_parser_list:
            return robot_parser_list[base_url]
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
frontier = queue.Queue()
for url in open(seed_urls).read().splitlines():
    frontier.put((url, 0))
visited = set()
pages_crawled = 0

def worker():
    global pages_crawled
    while True:
        try:
            website, curr_hop = frontier.get(timeout=3)
        except queue.Empty:
            break

        final_website = normalize_url(website)

        with visited_lock:
            if pages_crawled >= max_pages:
                frontier.task_done()
                continue
            if final_website in visited or curr_hop > max_hops:
                frontier.task_done()
                continue
            visited.add(final_website)
            pages_crawled += 1

        #check robot.txt
        if not rp_can_fetch(final_website):
            print(f"Skipping {final_website}, restricted by robots.txt.")
            frontier.task_done()
            continue
        page = requests.get(final_website, headers=headers)
        html_file = page.text

        soup = BeautifulSoup(page.content, "html.parser")
        title = soup.title.string
        # clean title to replace all non word, space, or hyphen chars with underscore
        clean_title = re.sub(r'[^\w]', '_', title)
        clean_title = re.sub(r'_+', '_', clean_title)  # remove multiple underscores in a row

        file_path = os.path.join(output_dir, f"{clean_title}.html")

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(html_file)            

        for link in soup.find_all('a', href=True):
            # skip images
            if link.find('img'):
                continue

            href = link.get('href')

            # only add links to other wikipedia articles
            if href.startswith('/wiki') and ':' not in href:
                full_url = urljoin("https://en.wikipedia.org", href)
                normalized_full_url = normalize_url(full_url)
                with visited_lock:
                    if normalized_full_url not in visited:
                        frontier.put((normalized_full_url, curr_hop+1))
        time.sleep(1)
        frontier.task_done()

num_threads = 5
threads = []
for i in range(num_threads):
    t = threading.Thread(target=worker)
    t.start()
    threads.append(t)

frontier.join()
for t in threads:
    t.join()


data = parse_folder(output_dir)
save_json_file(data, os.path.join(output_dir, "outputs.json"))
