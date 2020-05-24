import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from telebot import types
from time import sleep
import sqlite3

# chrome = UserAgent().chrome
chrome = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'

url_last = 'https://habr.com/ru/hub/python/'

name_class = ['content-list__item', 'content-list__item_post', 'shortcuts_item', 'focus']
name_link_class = 'post__title_link'
session = requests.session()


def get_items(URL):
    """
    :param URL: ссылка на страницу с хабра
    :return: возвращает список (заголовок, ссылка) или ничего
    """
    all_items = []
    try:
        req = session.get(URL, headers={'User-Agent': chrome})
        soup = BeautifulSoup(req.content, 'lxml')
        content = soup.find_all('li', attrs={'class': name_class})
        for i in content:
            try:
                item = i.find('a', attrs={'class': name_link_class})
                title = item.text
                href = item.attrs['href']
                content = (title, href)

                all_items.append(content)
            except:
                continue
        return all_items
    except:
        return None


def get_last_post():
    last_item = get_items(url_last)
    last_item = last_item[0]
    return f'[{last_item[0]}]({last_item[1]})'


def get_all_posts():
    count = 0
    base = sqlite3.connect('posts')
    all_items = []
    cur = base.cursor()
    while True:
        count += 1
        url = f'https://habr.com/ru/hub/python/page{count}/'
        items = get_items(url)
        if items:
            for item in items:
                all_items.append(item)
                title, link = item
                print(f'Записано - {title}')
            print(f'Страница {count} записана. Записей на странице {len(items)}')
            sleep(1)
        else:
            break
    print(len(all_items))
    print('Все страницы запарсены!')
    all_items = all_items[::-1]
    for post in all_items:
        title, link = post
        try:
            command = f"""INSERT INTO posts(TITLE, LINK) VALUES ("{title}", '{link}')"""
            cur.execute(command)
        except:
            command = f"""INSERT INTO posts(TITLE, LINK) VALUES ('{title}', '{link}')"""
            cur.execute(command)
        base.commit()
    cur.close()
    base.close()


def last_in_base():
    base = sqlite3.connect('posts')
    cur = base.cursor()
    cur.execute('SELECT * FROM posts ORDER BY ID DESC LIMIT 1')
    last_title = cur.fetchall()[0][1]
    return last_title


def get_new_posts(old_title):
    new_posts = []
    count = 0
    FLAG = True
    while FLAG:
        count += 1
        url = f'https://habr.com/ru/hub/python/page{count}/'
        page_posts = get_items(url)
        if page_posts:
            for post in page_posts:
                if post[0] == old_title:
                    FLAG = False
                    break
                else:
                    new_posts.append(post)
        sleep(1)
    return new_posts


def write_in_base(data):
    if len(data) != 0:
        base = sqlite3.connect('posts')
        cur = base.cursor()
        all_new = data[::-1]
        for post in all_new:
            title, link = post
            try:
                command = f"""INSERT INTO posts(TITLE, LINK) VALUES ("{title}", '{link}')"""
                cur.execute(command)
            except:
                command = f"""INSERT INTO posts(TITLE, LINK) VALUES ('{title}', '{link}')"""
                cur.execute(command)
            base.commit()
        cur.close()
        base.close()
    else:
        pass


def all_from_base():
    base = sqlite3.connect('posts')
    cur = base.cursor()
    cur.execute('SELECT * FROM posts ORDER BY ID')
    result = cur.fetchall()
    return result

def main():
    pass

if __name__ == '__main__':
    main()