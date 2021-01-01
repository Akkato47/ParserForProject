import requests  # pip install requests
from bs4 import BeautifulSoup  # pip install beautifulsoup4
import constants
import csv

URL = constants.URL
HOST = constants.HOST
FILE = constants.FILE_SORT_BY_PROJECTS

print('Выберите ваш профиль:'
      '\n Инженерный класс - 32'
      '\n Медицинские классы - 33'
      '\n Курчатовский проект - 34'
      '\n Академический класс - 35'
      '\n Кадетский класс - 36'
      '\n Педагогический класс - 37')
portalID = list(map(str, input().split()))
print('Начинаю фильрацию по проектам.')
for prtID in portalID:
    URL = URL + '&portalIds=' + prtID


def get_html(url, params=None):
    req = requests.get(url, params=params)  # Получаем запрос с url
    return req


# def get_filters(html):
#     soup = BeautifulSoup(html, 'html.parser')
#     filters = soup.find_all('label', class_='el-checkbox grid-x small-12')
#     col_it = []
#     for i in filters:
#         col_it.append(i.find('span', class_='el-checkbox__label').get_text(strip=True))
#         col_it.append(i.find('input', class_='el-checkbox__original').get('value'))
#     return col_it


def get_pages_count(html):  # Получаем кол-во страниц по ссылке URL
    soup = BeautifulSoup(html, 'html.parser')
    pagination = soup.find_all('li', class_="number")
    if pagination:
        return int(pagination[-1].get_text())
    else:
        return 1


def get_content(html):  # Получаем содержимое страницы по ссылке
    soup = BeautifulSoup(html, 'html.parser')  # Запускаем парсер в файл html в среде радоты html
    items = soup.find_all('section', class_="event-card small-12 grid-x")  # Ищем все теги по классу

    events = []
    for item in items:
        events.append({
            'title': item.find('div', class_="event-card__content-description-title").get_text(strip=True),
            'Leading': item.find('div', class_="event-card__content-description-agent").get_text(strip=True),
            'link': HOST + item.find('a', target="_blank").get('href'),
            'time': item.find('div', class_="event-card__date-time").get_text(strip=True),
            'day': item.find('div', class_="event-card__date-day").get_text(strip=True),
            'date': item.find('div', class_="event-card__date-date").get_text(strip=True),
            'date_of_end_reg': item.find('div', class_="event-card__content-status").get_text(strip=True),
            'places': item.find('span', class_="event-card__content-image-extramural").get_text(strip=True).replace
            ('/', '|')
        })
    return events


def save(items, path):  # Создаем и сохраняем файл с частично отсортированным контентом
    with open(path, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file, delimiter=';', quoting=csv.QUOTE_ALL)
        writer.writerow(['Title', 'Leading', 'link', 'time', 'day', 'date', 'EndReg', 'places'])
        for item in items:
            writer.writerow([item['title'], item['Leading'], item['link'], item['time'], item['day'], item['date'],
                             item['date_of_end_reg'], item['places']])


def parse():
    html = get_html(URL)
    if html.status_code == 200:
        events = []
        pages_count = get_pages_count(html.text)
        for page in range(1, pages_count + 1):
            print(f'Загрузка {page} из {pages_count}...')
            html = get_html(URL, params={'pageNumber': page})
            events.extend(get_content(html.text))
        save(events, FILE)
        print(f'Получено {len(events)} событий')
    else:
        print('Error 404: Страница не найдена')


parse()
