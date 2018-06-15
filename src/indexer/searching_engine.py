import os
import platform
import sys
import re
import time
import nltk
from clint.textui import colored, puts, indent
from repository.DBRepository import DBRepository
from utilities import is_ascii, lemmatisation, url_matchmaking, extract_body
from googlesearch.googlesearch import GoogleSearch
import NDCG as NDCG


def output_string(outputString, snippet_list=[]):
    if snippet_list:
        with indent(2):
            for item, snippet in zip(outputString, snippet_list):
                puts(colored.cyan('|'))
                puts(colored.cyan('\__>   ') + colored.clean(item))
                puts(colored.cyan('\__>   ') + colored.clean(snippet))
                puts(colored.cyan('|'))
    else:
        with indent(2):
            for item in outputString:
                puts(colored.cyan('|'))
                puts(colored.cyan('\__>   ') + colored.clean(item))
                puts(colored.cyan('|'))


def clear_screen():
    os_name = platform.system()
    if os_name == 'Windows':
        os.system('cls')
    else:
        os.system('clear')


def space(num=1):
    for _ in range(num):
        print('\n')


def exit_progress_bar():
    progress_list = ["|>          |", "|=>         |", "|==>        |", "|===>       |", "|====>      |",
                     "|=====>     |", "|======>    |", "|=======>   |", "|========>  |", "|=========> |",
                     "|==========>|"]

    for i in range(11):
        clear_screen()
        print('Have a Great Day Ahead!!!')
        space(2)
        print("Exiting " + progress_list[i])
        time.sleep(0.1)
    clear_screen()
    sys.exit()


def query_preprocessor(user_query):
    re.sub(r'[^\x00-\x7f]', r'', user_query)
    tokenized_string = nltk.tokenize.word_tokenize(user_query.lower().decode('utf-8'), 'english', preserve_line=False)
    wnl = nltk.WordNetLemmatizer()
    stop_words = set(nltk.corpus.stopwords.words('english'))
    user_query = []
    for token in tokenized_string:
        if not re.match('[~!`@#$%^&*()-_+{}".,:;?\']+$', token):
            if is_ascii(token) and token not in stop_words:
                user_query.append(wnl.lemmatize(token, lemmatisation(token)))
    return user_query


def exit_choice(flag):
    while flag:
        continue_searching = raw_input(
            colored.clean('Search again? ') + '[' + colored.cyan('Y') + '/' + colored.green('N') + ']: ')
        if continue_searching.lower() == 'y':
            flag = True
            break
        elif continue_searching.lower() == 'n':
            flag = False
            exit_progress_bar()
            break
        else:
            flag = True
            print('Wrong input. Please try again.')
            space()


def final_list_creation(common_docs, unique_docs, max_list_size):
    # final_list = common_docs.union(unique_docs)
    final_list = common_docs
    new_final_list = set()
    if len(final_list) <= max_list_size:
        new_final_list = list(final_list)
    else:
        new_final_list = list(final_list)[:max_list_size]

    url_list = []
    for each_doc in new_final_list:
        url_list.append(url_matchmaking(each_doc))

    return new_final_list, url_list


def proximity_weights(prox):
    if prox > 50:
        return 1
    elif prox > 40:
        return 2
    elif prox > 30:
        return 4
    elif prox > 20:
        return 6
    elif prox > 10:
        return 8
    else:
        return 10


def final_score(docs, doc_dict):
    for doc in docs:
        proximity = doc_dict[doc]['min_distance']
        weight_w1 = doc_dict[doc]['weight_w1']
        weight_w2 = doc_dict[doc]['weight_w2']
        weight = weight_w1 + weight_w2
        prox_score = proximity_weights(proximity)
        final_score = prox_score*weight
        # print(final_score, prox_score, weight)
        doc_dict[doc]['final_score'] = final_score
    return doc_dict

    
def proximity(docs, doc_dict):
    for doc in docs:
        positions_in_doc1 = doc_dict[doc]['pos_w1']
        positions_in_doc2 = doc_dict[doc]['pos_w2']
        min_dist = 99999
        first_pos = 0
        second_pos = 0
        for f in positions_in_doc1:
            for s in positions_in_doc2:
                if abs(f - s) < min_dist:
                    min_dist = abs(f - s)
                    if s > f:
                        first_pos = f
                        second_pos = s
                    else:
                        first_pos = s
                        second_pos = f
        doc_dict[doc]['min_distance'] = min_dist
        doc_dict[doc]['first_position'] = first_pos
        doc_dict[doc]['second_position'] = second_pos
        # print(doc)
        # print(doc_dict[doc])
    doc_dict = final_score(docs, doc_dict)
    return doc_dict

def google_search(user_query):
    query = ''
    for word in user_query:
        query += word
        query += ' '
    query += " site:ics.uci.edu"
    print("    " + query)
    response = GoogleSearch().search(query, num_results=5, prefetch_pages=False)
    google_results = []
    for result in response.results:
        google_results.append(result.url)
    return google_results


def get_snippet(path, user_query):
    f = open("webpages/" + path)
    string = f.read()
    nltk.re.sub(r'[^\x00-\x7f]', r'', string)
    nltk.re.sub(r'[^[~!`@#$%&*()-_+{}".,:;?\']+$]', r'', string)
    string = str(extract_body(string))
    words = nltk.tokenize.word_tokenize(string.decode('utf-8'), 'english', preserve_line=True)
    str1 = ''
    if len(user_query) == 2:
        if (user_query[0] in words) and (user_query[1] in words):
            index1 = words.index(user_query[0])
            index2 = words.index(user_query[1])
            list1 = words[index1-2:index1+2]
            list2 = words[index2-2:index2+2]
            concat = ['...']
            final_list = list1 + concat + list2
            str1 = ' '.join(str(e.encode('utf-8')) for e in final_list)
        elif user_query[0] in words:
            index1 = words.index(user_query[0])
            list1 = words[index1-9:index1+9]
            final_list = list1
            str1 = ' '.join(str(e.encode('utf-8')) for e in final_list)
        elif user_query[1] in words:
            index1 = words.index(user_query[1])
            list1 = words[index1-9:index1+9]
            final_list = list1
            str1 = ' '.join(str(e.encode('utf-8')) for e in final_list)
        else:
            str1 = ' '
    else:
        if user_query[0] in words:
            index1 = words.index(user_query[0])
            if index1>10:
                list1 = words[index1-10:index1+10]
                final_list = list1
                str1 = ' '.join(str(e.encode('utf-8')) for e in final_list)
            else:
                list1 = words[index1-index1:index1+15]
                final_list = list1
                str1 = ' '.join(str(e.encode('utf-8')) for e in final_list)
        else:
            str1 = ' '

    return str1


def main():
    try:
        db = DBRepository()
        flag = True
        while flag:
            while True:
                clear_screen()
                puts(colored.green('SEARCHING ENGINE') + colored.clean('\n -by Three Legged Spider'))
                space(1)
                raw_user_query = raw_input(colored.yellow("Enter your query: "))
                if len(raw_user_query) >= 1:
                    break
                else:
                    print('Enter valid query')
                    time.sleep(0.5)
                    continue

            user_query = query_preprocessor(raw_user_query)
            # print(user_query)
            common_docs, unique_docs = db.search_double_query(user_query)

            # print(common_docs)
            # space(3)
            # print(unique_docs)
            if common_docs == 0:
                space(1)
                print('No results found')
                space(2)
                exit_choice(flag)
            elif common_docs != 0:
                # print(common_docs)
                proximity_dict = {}
                if len(user_query)>1:
                    proximity_dict = db.get_proximity(list(common_docs), user_query)
                    # print(docs_dict)

                    proximity_dict = proximity(list(common_docs), proximity_dict)
                    sorted(proximity_dict, key=lambda x: (proximity_dict[x]['final_score']), reverse = True)

                    common_docs = set(proximity_dict.keys())
                
                final_document_list, final_url_list = final_list_creation(common_docs, unique_docs, 5)

                if len(user_query)==1:
                    position_dict = db.position_for_one_word(list(final_document_list), user_query[0]) 
                else:
                    unique_doc_positions1 = db.position_for_one_word(list(final_document_list), user_query[0])
                    unique_doc_positions2 = db.position_for_one_word(list(final_document_list), user_query[1])
                
                text_snippet = []

                for doc in list(final_document_list):
                    text_snippet.append(get_snippet(doc, user_query))

                # if len(user_query)==1:
                #     for doc in list(final_document_list):
                #         text_snippet.append(get_snippet(doc, position_dict[doc]['pos_w1']))
                # else:
                #     for doc in list(final_document_list):
                #         # space()
                #         # print(doc)
                #         if doc in common_docs:
                #             # print('in common')
                #             print(min(proximity_dict[doc]['pos_w1']), min(proximity_dict[doc]['pos_w2']))
                #             text_snippet.append(get_snippet(doc, min(proximity_dict[doc]['pos_w1']), \
                #                 min(proximity_dict[doc]['pos_w2'])))
                #         elif doc in unique_docs:
                #             # print('in unique')

                #             if doc in unique_doc_positions1.keys():
                #                 print(unique_doc_positions1[doc]['pos_w1'])
                #                 a = get_snippet(doc, unique_doc_positions1[doc]['pos_w1'])
                #                 text_snippet.append(a)
                #             elif doc in unique_doc_positions2.keys():
                #                 print(unique_doc_positions2[doc]['pos_w1'])
                #                 a = get_snippet(doc, unique_doc_positions2[doc]['pos_w1'])
                #                 text_snippet.append(a)
                #             else:
                #                 print('Something is wrong')

                print(colored.cyan('Google Results: '))
                output_string(google_search(user_query))
                space(1)
                print(colored.cyan("Search Results:"))
                output_string(final_url_list, text_snippet)
                # output_string(final_url_list)
                space(1)

                # weight_list = db.weigths_of_the_output(final_document_list, user_query)
                # print(weight_list)

                ground_truth = [int(x) for x in raw_input(
                    'List of relevance score for each result by Google seperated by space: ').split()]
                relevance_score = [int(x) for x in raw_input(
                    'List of relevance score for each results seperated by space: ').split()]

                N_list = NDCG.ndcg_at_k(relevance_score, 5)
                N_list_with_ground_truth = NDCG.ndcg_score(ground_truth, relevance_score, k=5)

                space(1)
                print('NDCG without Ground Truth: ' + str(N_list))
                print('NDCG with Ground Truth: ' + str(N_list_with_ground_truth))
                
                space(1)
                exit_choice(flag)

    except (KeyboardInterrupt, SystemExit):
        print('Exit by User')
        # exit_progress_bar()
        

if __name__ == '__main__':
    main()