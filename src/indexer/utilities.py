import json

from nltk.corpus import wordnet
import nltk
from bs4 import BeautifulSoup


def path_correction(path):
    return path.replace('webpages\\', '').replace('\\', '/').replace('webpages/', '')


def is_ascii(word):
    return all(ord(c) < 128 for c in word)


def lemmatisation(word):
    w_syn = wordnet.synsets(word)

    position = nltk.Counter()
    position["n"] = len([item for item in w_syn if item.pos() == "n"])
    position["v"] = len([item for item in w_syn if item.pos() == "v"])
    position["a"] = len([item for item in w_syn if item.pos() == "a"])
    position["r"] = len([item for item in w_syn if item.pos() == "r"])

    result = position.most_common(3)

    return result[0][0]


def extract_body(text):
    soup = BeautifulSoup(text, 'html.parser')
    body_text = str(soup.body)
    body_text = body_text.replace('<body>', '').replace('</body>', '')
    return body_text


f = open('webpages/bookkeeping.json','r')
bookKeeper = json.load(f)
print('bookKeeper imported')


def url_matchmaking(file_path):
    if file_path in bookKeeper:
        url = bookKeeper[file_path]
        return url
    else:
        return
