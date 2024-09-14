from logic import DB_Manager
from config import *
from telebot import TeleBot
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telebot import types

bot = TeleBot(TOKEN)


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    flowers = manager.get_flowers()
    user_id = call.message.chat.id
    users_flowers = manager.get_users_flowers(user_id)
    for i, flower in enumerate(flowers):
        if call.data == flower and call.data not in users_flowers:
            manager.add_flower(user_id, i+1, 1)
            bot.send_message(call.message.chat.id, f"Растение под названием {call.data} добавлено в ваш сад.")
        elif call.data == flower and call.data in users_flowers:
            info = manager.get_info_flower(user_id, call.data)[0]
            flower_index = flowers.index(call.data) + 1
            status = manager.get_status(user_id, flower_index)[0]
            if status == 3:
                img = manager.get_img(flower_index)[0]
                with open(f'images/{img}', 'rb') as photo:
                    bot.send_photo(user_id, photo)
            bot.send_message(call.message.chat.id, f'''
Растение: {info[0]}

Описание: {info[1]}

Воды: {info[2]}

Статус: {info[3]}
''')
    
    if "Полить" in call.data:
        res = call.data.split()
        water_count = manager.get_water(user_id, res[1])[0]
        water_count += 1
        flower_index = flowers.index(res[1]) + 1
        manager.water(water_count, user_id, flower_index)
        status = manager.get_status(user_id, flower_index)[0]
        if status == 3:
            bot.send_message(call.message.chat.id, f"Ваше растение {res[1]} достигло максимального размера!")
        elif water_count > 2 and status < 2:
            manager.up_status(status+1, user_id, flower_index)
            bot.send_message(call.message.chat.id, f"Ваше растение {res[1]} подросло!")
        elif water_count > 4 and status < 3:
            manager.up_status(status+1, user_id, flower_index)
            img = manager.get_img(flower_index)[0]
            with open(f'images/{img}', 'rb') as photo:
                bot.send_photo(user_id, photo, caption=f"Ваше растение {res[1]} расцвело!")
        else:
            bot.send_message(call.message.chat.id, f"Вы полили растение {res[1]}.")
        
    elif "Удалить" in call.data:
        res = call.data.split()
        flower_index = flowers.index(res[1]) + 1
        manager.delete_flower(user_id, flower_index)
        bot.send_message(call.message.chat.id, f"Растение {res[1]} удалено из вашего сада.")
    



@bot.message_handler(commands=['start'])
def handle_start(message):
    user_id = message.chat.id
    if user_id in manager.get_users():
        bot.reply_to(message, "Вы уже зарегистрированы!")
    else:
        manager.add_user(user_id, message.from_user.username)
        bot.reply_to(message, "Добро пожаловать!")
        
    keyboard = ReplyKeyboardMarkup()
    keyboard.row_width = 1
    new_flower = KeyboardButton(text="Получить новое растение")
    garden = KeyboardButton(text="Просмотреть свои растения")
    water = KeyboardButton(text="Полить растения")
    delete = KeyboardButton(text="Удалить растение")
    keyboard.add(new_flower, garden, water, delete)
    bot.send_message(message.chat.id, "Выберите команду", reply_markup=keyboard)



@bot.message_handler(func=lambda message: message.text == 'Получить новое растение')
def new_flower(message):
    flowers = manager.get_flowers()
    keyboard = []
    user_id = message.chat.id
    users_flowers = manager.get_users_flowers(user_id)

    for i in flowers:
        if f"{i}" not in users_flowers:
            keyboard.append([InlineKeyboardButton(i, callback_data=i)])
    if keyboard == []:
        bot.send_message(message.chat.id, text="Вы уже получили все растения!")
    else:
        reply_markup = InlineKeyboardMarkup(keyboard, row_width= 5)
        bot.send_message(message.chat.id, text="Выбери новое растение", reply_markup=reply_markup)

@bot.message_handler(func=lambda message: message.text == "Просмотреть свои растения")
def my_flowers(message):
    flowers = manager.get_flowers()
    user_id = message.chat.id
    users_flowers = manager.get_users_flowers(user_id)
    if users_flowers == []:
        bot.send_message(message.chat.id, text="У тебя ещё нет растений!")
    else:
        keyboard = []
        user_id = message.chat.id
        users_flowers = manager.get_users_flowers(user_id)
        for i in flowers:
            if f"{i}" in users_flowers:
                keyboard.append([InlineKeyboardButton(i, callback_data=i)])
        reply_markup = InlineKeyboardMarkup(keyboard, row_width= 5)
        bot.send_message(message.chat.id, text="Выбери своё растение, о котором хочешь узнать больше", reply_markup=reply_markup)

@bot.message_handler(func=lambda message: message.text == "Полить растения")
def water_flowers(message):
    flowers = manager.get_flowers()
    keyboard = []
    user_id = message.chat.id
    users_flowers = manager.get_users_flowers(user_id)
    for i in flowers:
        if f"{i}" in users_flowers:
            keyboard.append([InlineKeyboardButton(f"Полить {i}", callback_data=f"Полить {i}")])
    reply_markup = InlineKeyboardMarkup(keyboard, row_width= 5)
    bot.send_message(message.chat.id, text="Выбери своё растение, которое хочешь полить", reply_markup=reply_markup)

@bot.message_handler(func=lambda message: message.text == "Удалить растение")
def delete(message):
    flowers = manager.get_flowers()
    keyboard = []
    user_id = message.chat.id
    users_flowers = manager.get_users_flowers(user_id)
    for i in flowers:
        if f"{i}" in users_flowers:
            keyboard.append([InlineKeyboardButton(f"Удалить {i}", callback_data=f"Удалить {i}")])
    reply_markup = InlineKeyboardMarkup(keyboard, row_width= 5)
    bot.send_message(message.chat.id, text="Выбери растение, которое хочешь удалить", reply_markup=reply_markup)

if __name__ == '__main__':
    manager = DB_Manager(DATABASE)
    bot.infinity_polling()