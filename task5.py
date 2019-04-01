import math
import operator
from collections import defaultdict

import psycopg2

from task3_2 import prepare_words

conn = psycopg2.connect(database='search', user='postgres', password='postgres')
cur = conn.cursor()

tf_storage = defaultdict(float)
idf_storage = defaultdict(float)


def calculate_idf():
    cur.execute('select count(1) from articles')
    articles_count = cur.fetchone()[0]
    cur.execute('select * from article_term')
    article_terms = cur.fetchall()
    for article_term in article_terms:
        article_id = article_term[0]
        term_id = article_term[1]

        cur.execute("select count(article_id) from article_term where term_id = %s", (term_id,))
        articles_with_term_count = cur.fetchone()[0]

        idf = math.log(articles_count / articles_with_term_count)
        cur.execute('insert into article_term_idf(article_id, term_id, idf) VALUES (%s, %s, %s)',
                    (article_id, term_id, idf))
        conn.commit()


def count_cos_measure(v1, v2):
    pairs = zip(v1, v2)
    num = sum(pair[0] * pair[1] for pair in pairs)
    den = math.sqrt(sum(el * el for el in v1)) * math.sqrt(sum(el * el for el in v2))
    return num/den if den != 0 else 0


def get_query_vector(words):
    # getting vector of idf for query
    words_vec = []
    for word in words:
        cur.execute('select distinct idf from article_term_idf where term_id = '
                    '(select term_id from terms_list where term_text = %s)', (word,))
        idf = cur.fetchone()
        words_vec.append(idf[0] if idf else 0)
    return words_vec


def search_cos_idf(words_vec, words, articles=None):
    if not articles:
        # searching in all articles if not given
        cur.execute('select id from articles')
        articles = [article[0] for article in cur.fetchall()]

    result = defaultdict(float)

    for article in articles:
        articles_vec = []
        for wv in zip(words, words_vec):
            if wv[1] == 0:
                # if idf for word in DB is zero it is zero for article anyway
                articles_vec.append(0)
            else:
                cur.execute('select term_id from terms_list where term_text = %s', (wv[0],))
                term_id = cur.fetchone()[0]  # dangerous, but we checked entry before
                cur.execute('select idf from article_term_idf where term_id = %s and article_id = %s', (term_id, article))
                idf = cur.fetchone()
                articles_vec.append(idf[0] if idf else 0)

        cur.execute('select url from articles where id = %s', (article,))
        url = cur.fetchone()[0]

        result[url] = count_cos_measure(words_vec, articles_vec)

    result = sorted(result.items(), key=operator.itemgetter(1), reverse=True)

    return result


if __name__ == '__main__':
    # run once if db is empty
    calculate_idf()

    query = 'Безопасность конфиденциальных данных сотрудников'
    words = prepare_words(query)
    query_vector = get_query_vector(words)
    res = search_cos_idf(query_vector, words)
    print(res[:10])
