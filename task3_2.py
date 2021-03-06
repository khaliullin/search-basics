import psycopg2
import string

from stop_words import get_stop_words

from snowball import Stemmer


def intersection(lst1, lst2):
    if len(lst1) == 0:
        return lst2
    if len(lst2) == 0:
        return lst1
    return [value for value in lst1 if value in lst2]


# expanding default punctuation
punctuation = string.punctuation + r"—«»№–"


def prepare_words(sentence):
    words = sentence.strip().lower().split()
    # removing punctuation, such as "foo," or "bar!"
    words = [''.join(c for c in w if c not in punctuation) for w in words]

    stop_words = get_stop_words('ru')

    clear_words = []
    for word in words:
        if word not in stop_words:
            clear_words.append(word)

    snb = Stemmer()
    porter_stemed = set()
    for word in clear_words:
        porter_stemed.add(snb.stem(word))

    return porter_stemed


def search(sentence):
    conn = psycopg2.connect(database='search', user='postgres', password='postgres')
    cur = conn.cursor()

    words = prepare_words(sentence)
    articles = dict()
    for word in words:
        cur.execute("""SELECT distinct article_id from article_term where term_id = 
        (select term_id from terms_list where terms_list.term_text = %s)""", (word,))

        # list of sets with article ids
        arts = cur.fetchall()

        # list of article ids
        clear_arts = []
        for art in arts:
            clear_arts.append(art[0])
        articles[word] = clear_arts

    sorted_words = sorted(articles.items(), key=lambda kv: len(kv[1]), reverse=True)

    result_articles = []
    for word, articles in sorted_words:
        if len(articles) > 0:
            result_articles = intersection(result_articles, articles)

    article_urls = []
    for article_id in result_articles:
        cur.execute('select url from articles where id = %s', (article_id,))
        urls_tuple = cur.fetchall()
        for el in urls_tuple:
            article_urls.append(el[0])
    return article_urls


if __name__ == '__main__':
    # sentence = input()
    sentence = 'поиск работы в it-компании'
    print(search(sentence))
