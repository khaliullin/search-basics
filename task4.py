import math
from collections import defaultdict

import psycopg2

conn = psycopg2.connect(database='search', user='postgres', password='postgres')
cur = conn.cursor()

tf_storage = defaultdict(float)
idf_storage = defaultdict(float)


def calculate():
    cur.execute('select distinct id from articles')
    documents = [doc[0] for doc in cur.fetchall()]
    docs_len = len(documents)

    cur.execute('select distinct term from words_porter')
    words = cur.fetchall()

    for word in words:
        word = word[0]

        cur.execute('select articles_id from words_porter where term = %s', (word, ))
        usages = [usage[0] for usage in cur.fetchall()]

        for usage in set(usages):
            num = usages.count(usage)
            cur.execute('select count(1) term from words_porter where articles_id = %s', (usage,))
            den = cur.fetchone()[0]

            tf_storage[(word, usage)] = num/den

        for doc in documents:
            if doc not in usages:
                tf_storage[(word, doc)] = 0

        cur.execute('select count(distinct articles_id) from words_porter where term = %s', (word,))
        den = math.fabs(cur.fetchone()[0])

        idf_storage[word] = math.log(docs_len/den)

    for key in tf_storage:
        word = key[0]
        art_id = key[1]
        value = tf_storage[key]
        cur.execute('select term_id from terms_list where term_text = %s', (word,))
        term_id = cur.fetchone()[0]
        cur.execute('update article_term set "tf-idf" = %s where article_id = %s and term_id = %s', (value * idf_storage[word], art_id, term_id))
        conn.commit()


if __name__ == '__main__':
    calculate()
