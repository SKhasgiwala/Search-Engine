from pymongo import MongoClient
import sys


class DBRepository:
    def __init__(self):
        client = MongoClient('localhost', 27017)
        db = client['tls']
        self.collection = db['index']
        self.bulk_op = self.collection.initialize_ordered_bulk_op()

    def insert_new_word(self, word, count, path):
        w = {
            'word': word,
            'idf': 0,
            'documents': [{
                'docName': path,
                'tf': 1,
                'pos': [count],
                'weight': 0,
            }],
        }
        self.collection.insert(w)

    def insert_new_doc(self, word, count, path):
        a = {
            'docName': path,
            'tf': 1,
            'pos': [count],
            'weight': 0,
        }
        self.collection.update({"word": word}, {"$push": {'documents': a}})

    def insert_new_position(self, word, count, path):
        self.bulk_op.find({'word': word, 'documents.docName': path}).update({"$push": {"documents.$.pos": count}})
        self.bulk_op.find({'word': word, 'documents.docName': path}).update({"$inc": {"documents.$.tf": 1}})

    def is_word_present(self, word):
        return self.collection.find_one({'word': word}) is not None

    def is_doc_present(self, word, path):
        return self.collection.find_one({'word': word, 'documents.docName': path}) is not None

    def get_words(self):
        return self.collection.distinct("word")

    def execute_bulk_update(self):
        self.bulk_op.execute()

    def get_documents_for_words(self, words):
        result = {}
        cur = self.collection.find({"word": {"$in": words}}, no_cursor_timeout=True)
        for doc in cur:
            result[doc['word']] = doc
        return result

    def bulk_update_records(self, records):
        for k, v in records.iteritems():
            self.bulk_op.find({'word': k}).upsert().replace_one(v)
        self.bulk_op.execute()

    def search_single_query(self, user_query):
        list_of_pages = []
        dict_search_single = self.collection.find_one({'word': user_query})
        # print(dict_search_single)
        if dict_search_single is not None:
            # new_list = sorted(dict_search_single['documents'], key=lambda k: k['weight'], reverse=True)
            for x in dict_search_single['documents']:
                list_of_pages.append(x['docName'])
            return list_of_pages
        else:
            return 0

    def search_double_query(self, user_query):
        result_documents = []
        for item in user_query:
            single_query_result = self.search_single_query(item)
            if single_query_result == 0:
                return 0, 0
            else:
                curr_doc_set = set(single_query_result)
                result_documents.append(curr_doc_set)
        union = set.union(*result_documents)
        intersection = set.intersection(*result_documents)
        # print(len(intersection))
        return intersection, (union - intersection)

    
    def get_proximity(self, docs, user_query):
        doc_cursor = [[] for i in range(len(user_query))]
        # print(doc_cursor)
        for j, word in enumerate(user_query):
            doc_cursor[j] = self.collection.aggregate([
                { '$match': {"word": word, "documents.docName": {"$in": docs}}},
                { '$project': {
                    "documents": {'$filter': {
                        "input": '$documents',
                        "as": 'documents',
                        "cond": {'$in': ['$$documents.docName', docs]}
                    }}
                }}
            ])

        final = {}
        for doc in doc_cursor[0]:
            # print(doc)
            for item in doc['documents']:
                final[item['docName']] = {}
                final[item['docName']]['pos_w1'] = item['pos']
                final[item['docName']]['weight_w1'] = item['weight']
        # print('\n\n')
        for doc in doc_cursor[1]:
            # print(doc)
            for item in doc['documents']:
                final[item['docName']]['pos_w2'] = item['pos']
                final[item['docName']]['weight_w2'] = item['weight']
        # print final
        return final


    def position_for_one_word(self, docs, user_query):
        doc_cursor = self.collection.aggregate([
            { '$match': {"word": user_query, "documents.docName": {"$in": docs}}},
            { '$project': {
                "documents": {'$filter': {
                    "input": '$documents',
                    "as": 'documents',
                    "cond": {'$in': ['$$documents.docName', docs]}
                }}
            }}
        ])

        final = {}
        for doc in doc_cursor:
            # print "Inside cursor"
            # print(doc)
            for item in doc['documents']:
                final[item['docName']] = {}
                final[item['docName']]['pos_w1'] = min(item['pos'])
        return final


    # def position_for_two_word_unique_doc(self, docs, user_query):
    #     doc_cursor = [[] for i in range(len(user_query))]
    #     # print(doc_cursor)
    #     for j, word in enumerate(user_query):
    #         doc_cursor[j] = self.collection.aggregate([
    #             { '$match': {"word": word, "documents.docName": {"$in": docs}}},
    #             { '$project': {
    #                 "documents": {'$filter': {
    #                     "input": '$documents',
    #                     "as": 'documents',
    #                     "cond": {'$in': ['$$documents.docName', docs]}
    #                 }}
    #             }}
    #         ])

    #     final = {}
    #     for doc in doc_cursor[0]:
    #         for item in doc['documents']:
    #             final[item['docName']] = {}
    #             if item['pos']:
    #                 final[item['docName']]['pos'] = min(item['pos'])
    #     for doc in doc_cursor[1]:
    #         for item in doc['documents']:
    #             if item['pos'] is not None:
    #                 final[item['docName']]['pos'] = min(item['pos'])
    #     return final


    def add_idf_update(self, word, idf, documents):
        self.bulk_op.find({'word': word}).update({"$set": {"idf": idf, "documents": documents}})

    def execute_bulk_op(self):
        self.bulk_op.execute()

    def get_all_records(self):
        return self.collection.find()
