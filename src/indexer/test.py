# from pymongo import MongoClient
# from googlesearch.googlesearch import GoogleSearch

# def proximity_weights(prox):
#     if prox > 50:
#         return 1
#     elif prox > 40:
#         return 2
#     elif prox > 30:
#         return 4
#     elif prox > 20:
#         return 6
#     elif prox > 10:
#         return 8
#     else:
#         return 10


# def final_score(docs, doc_dict):
#     for doc in docs:
#         proximity = doc_dict[doc]['min_distance']
#         weight_w1 = doc_dict[doc]['weight_w1']
#         weight_w2 = doc_dict[doc]['weight_w2']
#         weight = weight_w1 + weight_w2
#         prox_score = proximity_weights(proximity)
#         final_score = (0.6 * prox_score) + (0.4 * weight)
#         doc_dict[doc]['final_score'] = final_score
#     return doc_dict

    
# def proximity(docs, doc_dict):
#     for doc in docs:
#         positions_in_doc1 = doc_dict[doc]['pos_w1']
#         positions_in_doc2 = doc_dict[doc]['pos_w2']
#         min_dist = 99999
#         first_pos = 0
#         second_pos = 0
#         for f in positions_in_doc1:
#             for s in positions_in_doc2:
#                 if abs(f - s) < min_dist:
#                     min_dist = abs(f - s)
#                     if s > f:
#                         first_pos = f
#                         second_pos = s
#                     else:
#                         first_pos = s
#                         second_pos = f
#         doc_dict[doc]['min_distance'] = min_dist
#         doc_dict[doc]['first_position'] = first_pos
#         doc_dict[doc]['second_position'] = second_pos
#     doc_dict = final_score(docs, doc_dict)
#     return doc_dict





# client = MongoClient('localhost', 27017)
# db = client['tls']
# collection = db['index']

# doc_list = ['14/108', '0/110', '0/188']
# user_query = ['machine', 'learn']


# doc_cursor = [[] for i in range(len(user_query))]

# for j, word in enumerate(user_query):
#     doc_cursor[j] = collection.aggregate([
#         { '$match': {"word": word, "documents.docName": {"$in": doc_list}}},
#         { '$project': {
#             "list": {'$filter': {
#                 "input": '$documents',
#                 "as": 'documents',
#                 "cond": {'$in': ['$$documents.docName', doc_list]}
#             }}
#         }}
#     ])


# final = {}
# for doc in doc_cursor[0]:
#     for item in doc['list']:
#         # print(item['pos'])
#         final[item['docName']] = {}
#         final[item['docName']]['pos_w1'] = item['pos']
#         final[item['docName']]['weight_w1'] = item['weight']

# for doc in doc_cursor[1]:
#     for item in doc['list']:
#         # print(item['pos'])
#         final[item['docName']]['pos_w2'] = item['pos']
#         final[item['docName']]['weight_w2'] = item['weight']


# final = proximity(doc_list, final)

# sorted(final, key=lambda x: (final[x]['final_score']), reverse = True)
# # final = final_score(doc_list, final)

# for doc in doc_list:
#     print(final[doc])

# common_docs = set(final.keys())
# print(common_docs)

# # for j, word in enumerate(user_query):
# #     doc_cursor[j] = collection.aggregate([
# #         {'$match': {
# #             "word": word 
# #         }},
# #         {'$project': {
# #             'list': {
# #                 '$filter': {
# #                     "input": '$documents',
# #                     "as": 'document',
# #                     "cond": {'$in': ['$$document.docName', doc_list]}
# #                 }
# #             }
# #         }}
# #     ])


# response = GoogleSearch().search("mondego site:ics.uci.edu", num_results=5, prefetch_pages=False)
# google_results = []
# for result in response.results:
#     google_results.append(result.url)

# print(google_results)



# import nltk
# from utilities import extract_body


# def get_snippet(self, path, pos1, pos2,):
#     f = open("webpages/" + path)
#     string = f.read()
#     nltk.re.sub(r'[^\x00-\x7f]', r'', string)
#     string = str(extract_body(string))

# #.split()
#     words = nltk.tokenize.word_tokenize(string.decode('utf-8'), 'english', preserve_line=False)
# #str1 = ' '.join(str(e) for e in words)
# #print str1
# #print str1[pos1]
#     if (pos2-pos1)>25:
#             final_list=words[pos1:pos1+25]

#             str1 = ' '.join(str(e) for e in final_list)
#     else:
#         temp=pos2-pos1
#         temp1=25-temp
#         temp2=temp1/2
#         if pos1>25:
#          final_list=words[pos1-temp2:pos2+temp2]

#          str1 = ' '.join(str(e) for e in final_list)
#         else:
#          final_list = words[1:pos2 + temp2]

#          str1 = ' '.join(str(e) for e in final_list)

#     return str1



list1 = [1,2,3,4,5]

if list1.index(3):
    print(1)
if list1.index(8):
    print(2)