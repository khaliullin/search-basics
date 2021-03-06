import string

import psycopg2
from pymystem3 import Mystem
from stop_words import get_stop_words

from snowball import Stemmer

conn = psycopg2.connect(database='search', user='postgres', password='postgres')
cur = conn.cursor()

cur.execute('SELECT id, content from articles')
rows = cur.fetchall()

# expanding default punctuation
punctuation = string.punctuation + r"—«»№–"

for row in rows:
    article_id = row[0]
    content = row[1].lower()

    words = content.split()

    # removing punctuation, such as "foo," or "bar!"
    words = [''.join(c for c in w if c not in punctuation) for w in words]

    # removing empty words from list
    words = [w for w in words if w]

    # getting stop words from stopwords-ru.json
    stop_words = get_stop_words('ru')

    # removing stop words
    clear_words = []
    for word in words:
        if word not in stop_words:
            clear_words.append(word)

    m = Mystem()
    my_stemed = []
    for word in clear_words:
        my_stemed.append(m.lemmatize(word)[0])

    for word in my_stemed:
        cur.execute('INSERT INTO words_mystem(term, articles_id) VALUES (%s, %s)', (word, article_id))
    conn.commit()

    snb = Stemmer()
    porter_stemed = []
    for word in clear_words:
        porter_stemed.append(snb.stem(word))

    for word in porter_stemed:
        cur.execute('INSERT INTO  words_porter(term, articles_id) VALUES (%s, %s)', (word, article_id))
    conn.commit()
