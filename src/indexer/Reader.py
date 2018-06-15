import os

from Indexer import Indexer
import idf

for dirpath, dirs, files in os.walk("webpages/"):
    for filename in files:
        fname = os.path.join(dirpath, filename).encode('utf8')
        Indexer(fname).tokenize()

idf.insert_idf()
