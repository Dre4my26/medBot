import telebot
from telebot import types
import json
from razdel import tokenize
import random
import requests
from bs4 import BeautifulSoup

if __name__ == "__main__":
    TOKEN = str(input('Введите токен для бота:'))

bot = telebot.TeleBot(TOKEN)
print('Токен принят!')
f = open('diseases.json', encoding='utf-8')
diseases_json = json.load(f)
print('JSON-файл обработан успешно!')

print('Бот запущен и работает...')


@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("👋 Поздороваться")
    markup.add(btn1)
    bot.send_message(message.from_user.id, "👋 Привет! Я твой бот-помощник для диагнозирования детских "
                                           "заболеваний по симптомам!", reply_markup=markup)


@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    if message.text == '👋 Поздороваться':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)  # создание новых кнопок
        btn1 = types.KeyboardButton('Диагностика')
        btn2 = types.KeyboardButton('Список команд')
        btn3 = types.KeyboardButton('Случайное заболевание')
        markup.add(btn1, btn2, btn3)
        bot.send_message(message.from_user.id, '❓ Задайте интересующий вас вопрос', reply_markup=markup)  # ответ бота

    elif message.text == 'Диагностика':
        bot.send_message(message.from_user.id, 'Моя база заболеваний пока достаточно скромная, я могу определить: \n'
                                               '- Ветрянку, \n'
                                               '- Скарлатину, \n'
                                               '- Краснуху, \n'
                                               '- Ангину, \n'
                                               '- Грипп и ОРВИ', parse_mode='markdown')
        user_symptoms = bot.send_message(message.from_user.id,
                                         'Введите список симптомов для диагностики *через пробел или запятые*',
                                         parse_mode='markdown')
        bot.register_next_step_handler(user_symptoms, diagnostics)

    elif message.text == 'Список команд':
        bot.send_message(message.from_user.id,
                         'Для простого управления ботом пользуйтесь кнопками снизу экрана.'
                         '\n Список доступных команд:\n'
                         '- Диагностика - Вы присылаете боту список симптомов Вашего ребенка, а бот подсказывает Вам,'
                         'что за болезни это могут быть \n'
                         '- Список команд - вывод списка команд, которые доступны для бота \n'
                         '- Случайное заболевание - вывод названия и общей информации о случайном заболевании',
                         parse_mode='Markdown')

    elif message.text == 'Случайное заболевание':
        bot.send_message(message.from_user.id,
                         'Случайное заболевание взято с ' +
                         '[сайта](https://www.smdoctor.ru/disease/)',
                         parse_mode='Markdown')
        bot.send_message(message.from_user.id, random_disease())


def diagnostics(user_message):
    bot.reply_to(user_message, text='Идет обработка, подождите, пожалуйста...')
    if ',' in [user_message]:
        user_tokens = tokenization(user_message)
        user_diseases = diagnose(user_tokens)
    else:
        user_diseases = diagnose(user_message)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)  # создание новых кнопок
    btn1 = types.KeyboardButton('Диагностика')
    btn2 = types.KeyboardButton('Список команд')
    btn3 = types.KeyboardButton('Случайное заболевание')
    markup.add(btn1, btn2, btn3)
    if user_diseases is not None:
        bot.send_message(user_message.from_user.id,
                         'Вот список болезней, которые могут быть у ребенка: ' + ', '.join(user_diseases.split()),
                         reply_markup=markup)
    else:
        bot.send_message(user_message.from_user.id,
                         'Простите, по Вашим симптомам ничего не найдено 😢',
                         reply_markup=markup)


def diagnose(user_symptoms) -> str:
    # print(user_symptoms)
    user_symptoms = user_symptoms.text  # преобразование JSON, которым является message, в текст сообщения пользователя
    possible_user_diseases = []
    user_symptoms = user_symptoms.lower()
    print('Пользовательские симптомы: ---------', user_symptoms)
    for user_symptom in user_symptoms.split(' '):
        for disease in diseases_json.keys():
            for symptom_sentence in diseases_json[disease]:
                for symptom_tokenized in [symptom_sentence.split(' ')]:
                    if symptom_tokenized[0].lower() == user_symptom:
                        print('одинаковые симтомы:', symptom_tokenized, user_symptom)
                        if disease not in possible_user_diseases:
                            possible_user_diseases.append(disease)
    print(' '.join(possible_user_diseases))

    if not possible_user_diseases:
        return None

    return ' '.join(possible_user_diseases)


def tokenization(msg: str) -> list:
    tokens = list(tokenize(msg))
    return [_.text for _ in tokens]


def random_disease() -> str:
    intro_message = 'Ошибка...'
    user_random_number = random.randint(0, 342)
    smdoctor_child_diseases_webpage = requests.get('https://www.smdoctor.ru/disease/')

    soup = BeautifulSoup(smdoctor_child_diseases_webpage.text, 'html.parser')
    html_diseases = soup.find('div', class_='b-diseases-list__items')
    diseases = html_diseases.find_all('a')
    print(diseases)
    print(len(diseases))
    user_random_disease = diseases[user_random_number]
    user_random_disease_url = 'https://www.smdoctor.ru' + user_random_disease['href']
    print(user_random_number, user_random_disease.text, user_random_disease_url)
    random_disease_webpage = requests.get(user_random_disease_url)
    disease_soup = BeautifulSoup(random_disease_webpage.text, 'html.parser')
    disease_intro = disease_soup.find('div', class_='b-inner-intro__text text')
    disease_name = user_random_disease.text
    for ptag in disease_intro.find_all('p'):
        intro_message = ' '.join(ptag)

    return disease_name + '\n' + intro_message


bot.polling(none_stop=True, interval=0)  # обязательная для работы бота часть
