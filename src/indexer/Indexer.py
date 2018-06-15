import nltk
import re

from repository.DBRepository import DBRepository
from utilities import path_correction, is_ascii, lemmatisation, extract_body

docCount = 0


class Indexer:
    def __init__(self, path):
        self.path = path
        self.corrected_path = path_correction(path)
        self.db = DBRepository()
        self.stop_words = set(nltk.corpus.stopwords.words('english'))
        self.wnl = nltk.WordNetLemmatizer()

    def process_existing_word(self, records, word, path, count):
        for item in records[word]["documents"]:
            if item["docName"] == path:
                item["pos"].append(count)
                item["tf"] += 1
                return records
        new_doc = {"docName": path, "tf": 1, "pos": [count], "weight": 0}
        records[word]["documents"].append(new_doc)
        return records

    def process_new_word(self, records, word, path, count):
        new_doc = {"docName": path, "tf": 1, "pos": [count], "weight": 0}
        new_record = {"word": word, "documents": [new_doc]}
        records[word] = new_record
        return records

    def compute_word_frequencies(self, tokens):
        count = 0
        bulk_update = False
        processed_words, unique_words = self.process_words(tokens)

        records = self.db.get_documents_for_words(unique_words)

        for word in processed_words:
            count += 1
            if is_ascii(word) and word not in self.stop_words and len(word) > 1:
                bulk_update = True
                if word in records:
                    records = self.process_existing_word(records, word, self.corrected_path, count)
                else:
                    records = self.process_new_word(records, word, self.corrected_path, count)
        if bulk_update:
            self.db.bulk_update_records(records)

    def process_words(self, tokens):
        processed_words = []
        unique_words = []
        for word in tokens:
            if not re.match('[~!`@#$%^&*()-_+{}".,:;?\']+$', word):
                if is_ascii(word) and word not in self.stop_words and len(word) > 1:
                    processed_word = self.wnl.lemmatize(word, lemmatisation(word))
                    if processed_word not in unique_words:
                        unique_words.append(processed_word)
                else:
                    processed_word = word
                processed_words.append(processed_word)
        return processed_words, unique_words

    def tokenize(self):
        if 'bookkeeping' not in self.path:
            global docCount
            docCount = docCount + 1
            print "COUNT: " + str(docCount)
            print "PATH: " + str(self.path)
            fp = open(self.path, "r")
            string = fp.read()
            fp.close()
            re.sub(r'[^\x00-\x7f]', r'', string)
            string = str(extract_body(string))
            string = string.lower()
            tokenized_string = nltk.tokenize.word_tokenize(string.decode('utf-8'), 'english', preserve_line=False)
            self.compute_word_frequencies(tokenized_string)
