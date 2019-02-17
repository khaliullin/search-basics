import psycopg2 as psycopg2
from lxml import html
import requests

conn = psycopg2.connect(database='search', user='postgres', password='postgres')
cur = conn.cursor()

cur.execute("INSERT INTO students (name, surname, mygroup) VALUES (%s, %s, %s) RETURNING id", ("Сагит", "Халиуллин", "11-501"))
student_id = cur.fetchone()[0]

pages = ['https://habr.com/ru/users/ragequit/posts/', 'https://habr.com/ru/users/ragequit/posts/page2/']
posts = []

# collect all links on posts to one list
for link in pages:
    page = requests.get(link)
    tree = html.fromstring(page.content)
    posts.extend(tree.xpath('//a[@class="post__title_link"]/@href'))

# getting content of each post
for post in posts[:30]:
    page = requests.get(post)
    tree = html.fromstring(page.content)

    title = tree.xpath('//span[@class="post__title-text"]/text()')[0]
    print(title)

    tags = tree.xpath('//dd[@class="post__tags-list"]//li/a/text()')
    tags = '; '.join(tags)
    print(tags)

    content = tree.xpath("//div[@class='post__text post__text-html js-mediator-article']")[0].text_content().strip()
    print(content[:50] + '\n\n')

    cur.execute("INSERT INTO articles (title, keywords, content, url, student_id) VALUES (%s, %s, %s, %s, %s)", (title, tags, content, post, student_id))

conn.commit()
