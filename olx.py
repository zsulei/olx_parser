from bs4 import BeautifulSoup
import requests
import csv
import telebot
from telebot import types, util
from myData import token


main_url = 'https://www.olx.kz/alma-ata/q-'


def write_csv(result):
    with open('file.csv', 'w', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Наименование', 'Цена', 'Описание', 'Адресс'])
        for item in result:
            writer.writerow(
                (
                item['name'],
                item['price'],
                item['address'],
                item['url'],
                )
            )

def clean(text):
    return text.replace('\t', '').replace('\n', '').strip()


def get_page_data(page_url):
    r = requests.get(page_url)
    soup = BeautifulSoup(r.content, 'lxml')
    table = soup.find('div', {'class': 'css-oukcj3'})
    rows = table.find_all('div', {'class': 'css-1sw7q4x'})
    result = []

    for row in rows:
        name = clean(row.find('h6').text)
        url = 'http://olx.kz' + row.find('a', {'class': 'css-rc5s2u'}).get('href')

        try:
            price = clean(row.find('p', {'class': 'css-10b0gli er34gjf0'}).text)
        except:
            price = 'Не указано'
        try:
            address = row.find('p', {'class': 'css-veheph er34gjf0'}).text
        except:
             address = 'Не указан'
        item = {'name': name, 'url': url, 'price': price,'address': address}
        result.append(item)
    return result


def main(main_url, message):
    r = requests.get(main_url + message.text + '/')
    soup = BeautifulSoup(r.content, 'lxml')
    result = []
    try:
        paginator = soup.find('div', {'class': 'listing-grid-container css-d4ctjd'})
        paginator = paginator.find('div', {'class': 'css-4mw0p4'})
        paginator = paginator.find('ul', {'data-testid': 'pagination-list'})
        paginator = int(paginator.text.split('...')[-1])
        bot.send_message(message.from_user.id, 'Количество страниц :' + str(paginator))
    except:
        paginator = soup.find('div', {'class': 'listing-grid-container css-d4ctjd'})
        paginator = paginator.find('div', {'class': 'css-4mw0p4'})
        paginator = paginator.find('ul', {'data-testid': 'pagination-list'})
        paginator = int(paginator.text[-1])
        bot.send_message(message.from_user.id, 'Количество страниц: ' + str(paginator) + '\nПримерное время ожиданя: ' + str(paginator * 4.8))

    
    for i in range(1, paginator + 1):

        page_url = main_url + message.text + '/' + '?page=' + str(i)
        result+=get_page_data(page_url)
    write_csv(result)
    


bot = telebot.TeleBot(token)

@bot.message_handler(commands=['start'])
def start(message):
    
    try:
        name = message.from_user.first_name
    except Exception as ex:
        name = message.from_user.username

    text = f'Привет, {name}!\nВведи свой запрос, и как информация будет готова, бот отправит тебе полученные данные'
    bot.send_message(message.from_user.id, text)


@bot.message_handler(content_types=['text'])
def get_text_message(message):

    main(main_url, message)

    file = open('C:/Users/2021/PycharmProjects/requests/file.csv', 'rb')
    bot.send_document(message.from_user.id, file)
        


        
bot.polling(non_stop=True, interval=0)
  