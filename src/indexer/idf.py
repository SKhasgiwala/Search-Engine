import math

from repository.DBRepository import DBRepository


def insert_idf():
    total = 37497
    db = DBRepository()
    dict_count_idf = db.get_all_records()
    doc_count = 0
    for element in dict_count_idf:
        count = len(element['documents'])  # N
        doc_count += 1
        idf = math.log10(total / count)

        for doc in element['documents']:
            doc['weight'] = (math.log10(doc['tf']) + 1) * idf
        db.add_idf_update(element['word'], idf, element['documents'])

    db.execute_bulk_op()
