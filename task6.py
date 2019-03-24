import math
import operator
from collections import defaultdict

import psycopg2

from task3_2 import prepare_words

conn = psycopg2.connect(database='search', user='postgres', password='postgres')
cur = conn.cursor()

K1 = 1.2
B = 0.75


def count_avgdl():
    cur.execute('select id from articles')
    articles = [article[0] for article in cur.fetchall()]
    words_in_articles = 0
    for article in articles:
        cur.execute('select count(1) from words_porter where articles_id = %s', (article,))
        words_in_articles += cur.fetchone()[0]
    return words_in_articles/len(articles)


def get_num_of_docs():
    cur.execute('select count(1) from articles')
    return cur.fetchone()[0]


avgdl = count_avgdl()
num_of_docs = get_num_of_docs()


def score(doc, query):
    """
    BM25 ranging function
    :param doc: id of document
    :param query: list of lemmatized tokens from query
    :return: score for query and one document
    """
    result = 0

    cur.execute('select count(1) from words_porter where articles_id = %s', (doc,))
    doc_len = cur.fetchone()[0]

    for term in query:
        nom = (freq(term, doc) * (K1 + 1))
        den = (freq(term, doc) * K1 * (1 - B + B * doc_len / avgdl))
        result += idf(term) * (nom / den) if den != 0 else 0

    return result


def freq(term, doc):
    """
    Frequency of term in document (TF)
    :return:
    """
    cur.execute('select count(1) from words_porter where articles_id = %s and term = %s', (doc, term))
    num_of_term_in_doc = cur.fetchone()[0]

    cur.execute('select count(1) from words_porter where articles_id = %s', (doc,))
    doc_len = cur.fetchone()[0]

    return num_of_term_in_doc / doc_len if doc_len != 0 else 0


def idf(t):
    """
    :param t: query term
    :return: weight of the query term. Returns 0 if result is negative.
    """
    cur.execute('select count(distinct articles_id) from words_porter where term = %s', (t,))
    num_of_docs_with_term = cur.fetchone()[0]
    res = math.log((num_of_docs - num_of_docs_with_term + 0.5) / (num_of_docs_with_term + 0.5))

    return res if res > 0 else 0


def search(query):
    words = prepare_words(query)
    cur.execute('select id from articles')
    articles = [article[0] for article in cur.fetchall()]

    result = defaultdict(float)
    for article in articles:
        s = score(article, words)
        cur.execute('select url from articles where id = %s', (article,))
        url = cur.fetchone()[0]
        result[url] = s
    result = sorted(result.items(), key=operator.itemgetter(1), reverse=True)
    return result


if __name__ == '__main__':
    results = search('Согласно уточнениям к документу 2012 года')
    print(results[:10])
