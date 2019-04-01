import operator
from collections import defaultdict

import numpy as np
import psycopg2

from scipy.linalg import svd
from sklearn.feature_extraction.text import CountVectorizer

from task3_2 import prepare_words
from task5 import count_cos_measure

RANK = 5

conn = psycopg2.connect(database='search', user='postgres', password='postgres')
cur = conn.cursor()


def get_matrices(docs, query):
    """
    :param docs: list with ids of articles
    :param query: prepared list of terms from query
    :return: term-document matrix (matrix A), query vector (array q^T)
    """
    cv = CountVectorizer(tokenizer=lambda doc: doc, lowercase=False)
    words_in_docs = []
    # words_in_docs = [['tom', 'want', 'apple', 'tom'], ['tom', 'love', 'pear']]
    for doc in docs:
        cur.execute('select term from words_porter where articles_id = %s', (doc,))
        words = [word[0] for word in cur.fetchall()]
        words_in_docs.append(words)

    tdm = cv.fit_transform(words_in_docs).toarray().transpose()
    q_t = cv.transform([query]).toarray()  # already transposed
    return tdm, q_t


def rank_docs(q, v, docs):
    result = defaultdict(float)
    q = np.diagonal(q)
    for i, doc in enumerate(docs):
        cur.execute('select url from articles where id = %s', (doc,))
        url = cur.fetchone()[0]

        similarity = count_cos_measure(q, v[i])
        result[url] = similarity
    return result


def count_lsi(query, docs):
    """
    Realisation of Latent Semantic Indexing algorithm
    https://apluswebservices.com/wp-content/uploads/2012/05/latent-semantic-indexing-fast-track-tutorial.pdf
    :param query: list of prepared terms from search query
    :param documents: list of article ids
    :return: dict of
    """
    a_matrix, query_vector = get_matrices(docs, query)

    # decomposing matrices
    u, s, vt = svd(a_matrix, full_matrices=False)

    # rank approximation
    u_k = u[:, :RANK]
    s_k = np.diag(s[:RANK,])
    v_k = vt.transpose()[:, :RANK]

    # calculating new query vector coordinates
    m1 = np.matmul(query_vector, u_k)
    q = m1 * np.linalg.inv(s_k)

    doc_ranks = rank_docs(q, v_k, documents)

    doc_ranks = sorted(doc_ranks.items(), key=operator.itemgetter(1), reverse=True)
    return doc_ranks


if __name__ == '__main__':
    query = 'солдаты на спецтехнике потратили 62 дня'
    cur.execute('select id from articles')
    documents = [doc[0] for doc in cur.fetchall()]

    query = prepare_words(query)
    result = count_lsi(query, documents)

    print(result[:10])
