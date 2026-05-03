import sys
import json
import time
import requests
import os

from collections import deque
from urllib.parse import urljoin
from bs4 import BeautifulSoup

# Dynamically find the parent directory (cs172_project) and add it to the path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)
from utils import load_json_file, save_json_file, normalize_url

ENCODING = "utf-8"
HEADERS = {"User-Agent": "CS172_CATEGORY1Scraper/0.0 (your_actual@ucr.edu)"}

class WikiCrawler:
    def __init__(
        self,
        seed_urls: str,
        max_depth=5,
        time_limit_sec=1800,
        max_size_MB=120,
        output_file="./data/pop.json",
    ):
        self.seed_urls = seed_urls.split()
        self.max_depth = max_depth
        self.time_limit_sec = time_limit_sec
        self.max_size_bytes = max_size_MB * 1024 * 1024
        self.output_file = output_file

        self.visited_urls_file = "../visited_urls.json"
        self.exisiting_visited_urls = load_json_file(self.visited_urls_file)
        self.current_session_visited_urls = set()
        self.scraped_data = load_json_file(output_file)
        self.url_frontier = deque([(url, 0) for url in self.seed_urls])

        self.crawler_start_time = time.time()
        self.pages_crawled_this_session = 0
        
        # Calculate initial size if file already exists
        self.current_size_bytes = 0
        if os.path.exists(self.output_file):
            self.current_size_bytes = os.path.getsize(self.output_file)
    
    @staticmethod
    def extract_text_content(soup):
        # Tags we actually care about
        target_tags = ['h1', 'h2', 'h3', 'p', 'li']
        text_content = []
        
        for tag in soup.find_all(target_tags):
            text_content.append(tag.get_text(strip=True))

        return "\n".join(text_content)
    
    @staticmethod
    def extract_links(soup, base_url):
        links = set()
        
        # # Only grab links from the actual article text
        # content_div = soup.find(id="mw-content-text")
        # if not content_div:
        #     return links
        
        allowed_domains = ['en.wikipedia.org']
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']
            if href.startswith('/wiki/') and ':' not in href: # Prevents Special:, Talk:, Category:
                full_url = urljoin(base_url, href)
                if any(domain in full_url for domain in allowed_domains):
                    links.add(full_url)
        return links
    
    def check_limits(self):
        if time.time() - self.crawler_start_time > self.time_limit_sec:
            print(f"\n[STOP] Time limit of {self.time_limit_sec} seconds reached.")
            return True
            
        if self.current_size_bytes >= self.max_size_bytes:
            print(f"\n[STOP] Size limit of {self.max_size_bytes / (1024*1024):.2f} MB reached.")
            return True
            
        return False

    def crawl(self, url, depth):
        normalized_url = normalize_url(url)
        if normalized_url in self.exisiting_visited_urls or normalized_url in self.current_session_visited_urls:
            return False
        
        try:
            response = requests.get(normalized_url, headers=HEADERS,timeout=5, allow_redirects=True)
            response.raise_for_status()
            final_url = normalize_url(response.url)
            
            if final_url in self.exisiting_visited_urls or final_url in self.current_session_visited_urls:
                return False

            time.sleep(2)
            
            soup = BeautifulSoup(response.content, 'html.parser')
            text_content = WikiCrawler.extract_text_content(soup)
            
            self.current_session_visited_urls.add(final_url)
            page_data = {
                "url": final_url,
                "content": text_content
            }
            self.scraped_data[final_url] = page_data
            self.current_size_bytes += len(json.dumps(page_data).encode(ENCODING))
            
            if depth < self.max_depth:
                new_links = WikiCrawler.extract_links(soup, final_url)
                for new_url in new_links:
                    normalized_new_url = normalize_url(new_url)
                    if normalized_new_url not in self.exisiting_visited_urls:
                        self.url_frontier.append((normalized_new_url, depth + 1))
                        
            return True
        except requests.exceptions.RequestException as err:
            print(f"Skipping {url} due to error: {err}")
            return False
        finally:
            pass

    def run(self):
        try:
            while self.url_frontier:
                if self.check_limits():
                    break
                url, depth = self.url_frontier.popleft()
                if self.crawl(url, depth):
                    self.pages_crawled_this_session += 1
                    print(f"Depth {depth} | Crawled: {url} | Size: {self.current_size_bytes / (1024*1024):.2f} MB")
                    
                if self.pages_crawled_this_session > 0 and self.pages_crawled_this_session % 50 == 0:
                    print("Autosaving progress...")
                    save_json_file(self.scraped_data, self.output_file)

        finally:
            print("\nSaving data and wrapping up...")
            new_visited = {h: self.scraped_data[h]["url"] for h in self.current_session_visited_urls if h in self.scraped_data}
            self.exisiting_visited_urls.update(new_visited)
            save_json_file(self.exisiting_visited_urls, self.visited_urls_file)
            save_json_file(self.scraped_data, self.output_file)
            print(f"Final session stats: {len(self.current_session_visited_urls)} pages crawled.")


if __name__ == "__main__":
    if len(sys.argv) < 6:
        print("Usage: python scrape.py <seed_urls> <max_depth> <time_limit_sec> <max_size_mb> <output_file>")
        sys.exit(1)
    seed_urls = sys.argv[1]
    max_depth = int(sys.argv[2])
    time_limit_sec = int(sys.argv[3])
    max_size_MB = int(sys.argv[4])
    output_file = sys.argv[5]

    crawler = WikiCrawler(seed_urls, max_depth, time_limit_sec, max_size_MB, output_file)
    crawler.run()
