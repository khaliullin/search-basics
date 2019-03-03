import psycopg2

conn = psycopg2.connect(database='search', user='postgres', password='postgres')
cur = conn.cursor()

cur.execute('SELECT term from words_porter')
words = cur.fetchall()

words = [word[0] for word in words]
words = sorted(set(words))
print(words)

for w in words:
    cur.execute(
        """INSERT into terms_list(term_text) values (%s) 
        ON CONFLICT (term_text) DO UPDATE set term_text = %s returning term_id""", (w, w))
    word_id = cur.fetchone()[0]

    cur.execute('SELECT articles_id from words_porter WHERE term = %s', (w,))
    articles = cur.fetchall()

    for article in articles:
        cur.execute('INSERT into article_term(article_id, term_id) values (%s, %s)', (article[0], word_id))
    conn.commit()
