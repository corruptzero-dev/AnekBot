
#__________Создаем бд и таблицу с анекдотами.
#_______Наполняем таблицу с помощью парсинга сайта.

import requests, bs4  #Для парсинга сайта
import sqlite3  #Для хранения анекдотов
import re   #Для обработки текста анекдотов
import random   #Рандом
import telebot  #Телеграм-бот
import os.path  #Для chat_id

link_parts = ['luchshie-anekdoti','random','lenta','anekdoti_cherniy-yumor','sandbox-top','anekdoti_raznie']
rndm_link = random.randint(0,len(link_parts)-1)
conn = sqlite3.connect('anekBot.db')   
cur = conn.cursor()
cur.executescript("""create table if not exists anekdotes(
        id int auto_increment primary key, anekText longtext
    );""")
idx=0

quantity = 100  #Сюда вводите сколько анекдотов нужно подгрузить.
print(f"Выбираем анекдоты из раздела {link_parts[rndm_link]}")
for _ in range(quantity):
    idx=idx+1
    site=requests.get(f'http://anekdotme.ru/{link_parts[rndm_link]}')
    siteParsed=bs4.BeautifulSoup(site.text, "html.parser")
    rawText=siteParsed.select('.anekdot_text')
    for text in rawText:        
        strText=(text.getText().strip())
        regex = re.compile('[^a-zA-Zа-яА-я .,!]')
        strText=regex.sub('', strText)
        cur.execute(f"INSERT INTO anekdotes (anekText) VALUES ('{strText}')")
        conn.commit()
    print(f"Анекдот #{idx} был добавлен в базу.")
print('_'*20)
print(f"{idx} анекдотов было добавлено в базу.")

conn.close()


#__________Скрипт для бота.__________

token = '' #Ваш токен здесь.

bot = telebot.TeleBot(token)

chat_id = 0            #Id чата с ботом

global host, host_chat_id
if os.path.isfile("host_data.txt"): 
  with open('host_data.txt') as f:
    lines = f.readlines()
    host = lines[0].strip()
    chat_id = int(lines[1].strip())
else:
  host = input('Пожалуйста введите Ваш ник в телеграме.\nЭто важно и делается один раз.: ') 
  f = open("host_data.txt", "w")
  f.write(host)
  f.close()
  
def randomAnek():
  conn = sqlite3.connect('anekBot.db')
  cursor = conn.cursor()
  c = cursor.execute('SELECT COUNT( DISTINCT anekText ) FROM anekdotes')
  cn = cursor.fetchone()
  cnt = cn[0]
  randAnekRow = random.randint(1,cnt)
  cursor.execute(f'SELECT * FROM anekdotes WHERE rowid='+str(randAnekRow))
  row = cursor.fetchone()
  randAnek = str(row[1])
  conn.close()
  return randAnek


print('Бот был запущен.')
@bot.message_handler(commands=['start'])
def start_func(message):
  bot.send_message(message.chat.id, 'здарова, напиши "Анек", чтобы получить несмешной анекдот.')

@bot.message_handler(content_types=['text'])

def anek_handler(message):
  with open('host_data.txt') as f:
    lines = f.readlines()
    if len(lines) == 2:
      chat_id = lines[1].strip()
      f.close()
    if len(lines) == 1:
      if message.from_user.first_name == host and host_cnt == 0:
        chat_id = message.chat.id
        print(f'Был получен Ваш chat_id: {chat_id}')
        f = open("host_data.txt", "a")
        f.write(f'\n{str(chat_id)}')
        f.close()
  if message.text.lower() == 'анек':
    bot.send_message(message.chat.id, randomAnek())
  else:
    bot.send_message(message.chat.id, 'я только знаю команды "/start" и "анек".')
  if message.from_user.first_name != host:
    print(f'{message.from_user.first_name} (@{message.from_user.username}) написал боту {message.text}')
    bot.send_message(int(chat_id), f'{message.from_user.first_name} (@{message.from_user.username}) написал боту {message.text}')
  else:
    print('Вы написали боту.')

bot.polling()
