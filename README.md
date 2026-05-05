# cs172group8


## **Instructions to Deploy the System**
- In order to successfully run our crawler, we have implemented a crawler.sh executable script.
- This successfully checks the inputted parameters and runs our scrape.py file with the inputted arguments. 

Make sure to have the proper Python libraries and dependencies installed (i.e. Beautiful Soup, Requests)

- **Run**:  pip install beautifulsoup4 in your terminal
- **Run**:  python3 -m pip install requests

Run the following command in your terminal to execute the crawler. 

- **Run**: **chmod +x crawler.sh**
- **Run**: **./crawler.sh <seed_file> <max-pages> <max_hops> <output_folder> <time_limit>**

This command allows the crawler to begin crawling.

_Input Arguments:_
- <seed_file>: .txt file containing the seed URL(s)
- <max_pages>: integer value of maximum amount of pages to crawl
- <max_hops>: integer value of maximum amount of hops from seed url
- <output_folder>: folder name where all HTML files will get saved
- [time_limit]: (in seconds) maximum runtime

**Output**:
- After the command is ran, you will see your HTML files being populated under the <output_folder> folder within your file directory. 
- <output.json> file contains a dictionary of key information about each html file that was generated (title, text content, headings, and last modified date).
