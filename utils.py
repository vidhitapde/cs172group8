import os
import json
from pathlib import Path
from urllib.parse import urlparse, urlunparse,urljoin
from bs4 import BeautifulSoup


encoding = "utf-8"

# title
def extract_title(soup):
    title_tag = soup.find("title")
    title = title_tag.text.strip()
    exists = bool(title)
    if not exists:
        return "No Title Found"
    return title

#extract heading
def extract_headings(soup):
    find_headings_content = soup.find("div", {"id": "mw-content-text"})
    headings = []
    target_tags = ['h1','h2','h3']
    for tag in find_headings_content.find_all(target_tags):
       headings.append(tag.get_text(strip=True))
    return "\n".join(headings)

def extract_text_content(soup): 
   find_text_content = soup.find("div", {"id": "mw-content-text"})
   targeted_tags = [ 'p', 'li']
   text_content = []
   for tag in find_text_content.find_all(targeted_tags):
       text_content.append(tag.get_text(strip=True))
   return "\n".join(text_content)
  

def last_edited_date(soup):
    last_modified_date = soup.find(id="footer-info-lastmod")
    if last_modified_date:
         return last_modified_date.get_text(strip=True)
    return "No Date Found"



def parse_folder(folderpath):
   output_data = {}
   for filename in os.listdir(folderpath):
    if filename.endswith(".html"):
        file_path = os.path.join(folderpath,filename)
        with open(file_path, "r", encoding=encoding) as f:
            soup = BeautifulSoup(f.read(), "html.parser")
            title = extract_title(soup)
            headings = extract_headings(soup)
            text_content = extract_text_content(soup)
            last_modified_date = last_edited_date(soup)
            output_data[filename] = {
                "title": title,
                "headings": headings,
                "text_content": text_content,
                "last_edited": last_modified_date,
            
            }
   return output_data
   
def load_json_file(filename):
   file_path = Path(filename)
   if not file_path.is_file():
       return {}   
   try:
       with open(file_path, "r", encoding=encoding) as f:
           return json.load(f)
   except json.JSONDecodeError:
       return {}


def save_json_file(data, file):
   os.makedirs(os.path.dirname(file), exist_ok=True)
   with open(file, "w", encoding=encoding) as f:
       json.dump(data, f, ensure_ascii=False)


def normalize_url(url) -> str:
    """Strips parameters and fragments from the URL and handles case sensitivity."""
    parsed_url = urlparse(url)
    return urlunparse(parsed_url._replace(scheme=parsed_url.scheme.lower(),fragment="", query=""))