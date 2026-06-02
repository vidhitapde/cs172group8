import re
from bs4 import BeautifulSoup
from utils import extract_title, extract_headings, extract_text_content, last_edited_date
import logging, sys
logging.disable(sys.maxsize)

import lucene
import os
from org.apache.lucene.store import MMapDirectory, SimpleFSDirectory, NIOFSDirectory
from java.nio.file import Paths
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.document import Document, Field, FieldType
from org.apache.lucene.queryparser.classic import QueryParser
from org.apache.lucene.index import FieldInfo, IndexWriter, IndexWriterConfig, IndexOptions, DirectoryReader
from org.apache.lucene.search import IndexSearcher, BoostQuery, Query
from org.apache.lucene.search.similarities import BM25Similarity

def create_index(input_dir, dir):
    # count = 0
    if not os.path.exists(dir):
        os.mkdir(dir)
    store = SimpleFSDirectory(Paths.get(dir))
    analyzer = StandardAnalyzer()
    config = IndexWriterConfig(analyzer)
    config.setOpenMode(IndexWriterConfig.OpenMode.CREATE)
    writer = IndexWriter(store, config)
    metaType = FieldType()
    metaType.setStored(True)
    metaType.setTokenized(False)
    contextType = FieldType()
    contextType.setStored(True)
    contextType.setTokenized(True)
    contextType.setIndexOptions(IndexOptions.DOCS_AND_FREQS_AND_POSITIONS)

    for filename in os.listdir(input_dir):
        # count += 1
        if filename.endswith(".html"):
            file_path = os.path.join(input_dir, filename)
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                soup = BeautifulSoup(f.read(), "html.parser")
                title = extract_title(soup)
                headings = extract_headings(soup)
                text_content = extract_text_content(soup)
                last_modified_date = last_edited_date(soup)
                doc = Document()
                doc.add(Field('Title', str(title), metaType))
                doc.add(Field('Heading', str(headings), contextType))
                doc.add(Field('Context', str(text_content), contextType))
                doc.add(Field('Modify date', str(last_modified_date), metaType))
                writer.addDocument(doc)
                # print(count)
    writer.close()


lucene.initVM(vmargs=['-Djava.awt.headless=true'])
create_index('combined_output', 'index')