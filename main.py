import telebot
from telebot import types

import time
import os
from prettytable import PrettyTable

from config import TOKEN_API
from DB import users_db, admin_users, products_db


bot = telebot.TeleBot(TOKEN_API, threaded=False)

users_db.users_table_create()
products_db.product_table_create()


def create_file_text_table(message, table):
    data_list = [list(data) for data in table]

    th = ["№", "Название", "Вкус", "Объем", "Тип", "Страна", "Количество", "Цена"]
    td = data_list

    columns = len(th)

    table = PrettyTable(th)

    td_data = td[:]
    while td_data:
        table.add_rows(td_data[:columns])
        td_data = td_data[columns:]

    with open("table.txt", "w") as file:
        file.write(str(table))

    bot.send_document(message.chat.id, open("table.txt", "r"))

    os.remove("table.txt")


@bot.message_handler(commands=["start"])
def start_command(message):
    if users_db.user_check_in_db(message.from_user.id):
        user = (message.from_user.id,
                message.from_user.first_name,
                admin_users.user_check_on_admin(message.from_user.id))
        users_db.user_add_in_db(user)
    return menu_command(message)


@bot.message_handler(commands=["menu"])
def menu_command(message):
    if admin_users.user_check_on_admin(message.from_user.id) == "admin":
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        markup.row('➕\nДобавить', '✖\nУдалить', '♾\nИзменить')
        markup.row('📋 Показать товар в наличии')
        markup.row('👤 О нас')
        return bot.send_message(message.chat.id, "<b>Меню 📜</b>", parse_mode="HTML", reply_markup=markup)
    else:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        markup.row('📋 Показать товар в наличии')
        markup.row('👤 О нас')
        return bot.send_message(message.chat.id, "<b>Меню 📜</b>", parse_mode="HTML", reply_markup=markup)


@bot.message_handler(commands=["input"])
#New command input
def new_input_command(message):
    bot.send_message(message.chat.id, "<b>Введите данные о товаре, который хотите добавить</b>\n<em>Пример ввода выведен ниже, можете нажать и скопировать его</em>", parse_mode="HTML")
    bot.send_message(message.chat.id, "<b><em><code>название|вкус|объем|тип|страна|количество|цена</code></em></b>",
                     parse_mode="HTML")
    return bot.register_next_step_handler(message, new_validation_check)


def new_validation_check(message):
    new_product_list = message.text.replace(" ", "").upper().split("|")

    if str.isdigit(new_product_list[0]) or str.isdigit(new_product_list[1]) or str.isdigit(new_product_list[3]) or str.isdigit(new_product_list[4]):
        bot.send_message(message.chat.id, "<em>Название, вкус, тип или же страна</em>, <b>НЕ ЯВЛЯЮТСЯ ТЕКСТОМ!</b> ❌", parse_mode="HTML")
        return menu_command(message)

    if False in (new_product_list[5].isdigit(), new_product_list[6].isdigit()):
        bot.send_message(message.chat.id, "<em>Количество или же цена</em>, <b>НЕ ЯВЛЯЮТСЯ ЧИСЛАМИ!</b> ❌", parse_mode="HTML")
        return menu_command(message)

    return new_product_list_push(message, new_product_list)


def new_product_list_push(message, new_product_list):
    if products_db.products_check_in_db(new_product_list):
        products_db.products_add_in_db(new_product_list)
        bot.send_message(message.chat.id, "<b>Товар сохранен</b> ✅", parse_mode="HTML")
        return menu_command(message)
    else:
        bot.send_message(message.chat.id, "<em>Такой товар уже имеется в базе, если хотите изменить его параметры, нажмите на -></em><b>/♾ Редактировать товар</b> ❌")
        return menu_command(message)


@bot.message_handler(commands=["delete"])
def delete_command(message):
    if products_db.select_all_in_table():
        bot.send_message(message.chat.id, "<b><em>Склад пуст</em></b> 😅", parse_mode="HTML")
        return menu_command(message)
    else:
        create_file_text_table(message, products_db.select_all_in_table())
        bot.send_message(message.chat.id, "Введите номер товара, который хотите удалить: ")
        return bot.register_next_step_handler(message, answer_delete)


def answer_delete(message):
    if message.text.isdigit():
        products_db.delete_row(message.text)
        bot.send_message(message.chat.id, "<b>Товар успешно удален</b> ✅", parse_mode="HTML")
        return menu_command(message)
    else:
        bot.send_message(message.chat.id, "<b>Это не совсем текст, попробуйте еще</b> ❌", parse_mode="HTML")
        return menu_command(message)


@bot.message_handler(commands=["edit"])
def edit_command(message):
    if products_db.select_all_in_table():
        bot.send_message(message.chat.id, "<b><em>Склад пуст</em></b> 😅", parse_mode="HTML")
        return menu_command(message)
    else:
        markup = types.InlineKeyboardMarkup()

        button_price = types.InlineKeyboardButton("Цену", callback_data="price")
        button_amount = types.InlineKeyboardButton("Количество", callback_data="amount")
        markup.add(button_price, button_amount)

        bot.send_message(message.chat.id, "Что вы хотите поменять?", reply_markup=markup)


def answer_edit_row(message, value):
    if products_db.select_all_in_table():
        bot.send_message(message.chat.id, "<b><em>Склад пуст</em></b> 😅", parse_mode="HTML")
        return menu_command(message)
    else:
        create_file_text_table(message, products_db.select_all_in_table())
        bot.send_message(message.chat.id, "Введите номер товара, который хотите редактивроать: ")
        return bot.register_next_step_handler(message, answer_edit, value)


def answer_edit(message, value):
    if message.text.isdigit():
        row_id = message.text
        bot.send_message(message.chat.id, "На какое число, мне сменить предыдущеее значение: ")
        return bot.register_next_step_handler(message, answer_edit_number, value, row_id)
    else:
        bot.send_message(message.chat.id, "<b>Это не совсем текст, попробуйте еще</b> ❌", parse_mode="HTML")
        return answer_edit_row(message, value)


def answer_edit_number(message, value, row_id):
    if message.text.isdigit():
        number = message.text
        return edit_successfully(message, value, row_id, number)
    else:
        bot.send_message(message.chat.id, "<b>Это не совсем текст, попробуйте еще</b> ❌", parse_mode="HTML")
        return answer_edit(message, value)


def edit_successfully(message, value, row_id, number):
    products_db.update_row(value=value, row_id=row_id, number=number)
    return bot.send_message(message.chat.id, "<b>Товар успешно отредактирован</b> ✅", parse_mode="HTML")


@bot.message_handler(commands=["output"])
def output_command(message):
    return create_file_text_table(message, products_db.select_all_in_table())


def search_command(message):
    bot.send_message(message.chat.id, "<b>Введите название товара: </b>", parse_mode="HTML")
    return bot.register_next_step_handler(message, answer_search)


def answer_search(message):
    if products_db.select_name_in_table(message.text) is True:
        bot.send_message(message.chat.id, "<b><em>В дынный момент, такого товара нет в наличии</em></b> 😅",
                         parse_mode="HTML")
        return menu_command(message)
    else:
        return create_file_text_table(message, products_db.select_name_in_table(message.text))


@bot.message_handler(commands=["about"])
def about_command(message):
    return bot.send_message(message.chat.id, "<b>О нас</b>: <em>Мы - небольшой склад, торгующий напитками по магазинам Дагестана, а также за его пределами.\n\n</em><b>Наш Адрес</b>: <em>Миатлинская 101 А\n\n</em><b>Наши контакты</b>: <em>Махач Алдамович \t---\t <code>+7 988 781-84-39</code></em>", parse_mode='HTML')


@bot.callback_query_handler(func=lambda call: True)
def callback_command(call):
    if call.data == "menu_inl":
        menu_command(call.message)
    elif call.data == "price" or call.data == "amount":
        value = call.data
        answer_edit_row(call.message, value)


@bot.message_handler(content_types=["text"])
def reply_text(message):
    if message.text == "➕\nДобавить":
        new_input_command(message)
    elif message.text == "✖\nУдалить":
        delete_command(message)
    elif message.text == "♾\nИзменить":
        edit_command(message)
    elif message.text == "📋 Показать товар в наличии":
        if products_db.select_all_in_table():
            bot.send_message(message.chat.id, "<b><em>Склад пуст</em></b> 😅", parse_mode="HTML")
            return menu_command(message)
        else:
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)

            markup.row("🔎 Поиск", "📄 Показать весь ассортимент")
            markup.row("⬅ Назад в меню")

            bot.send_message(message.chat.id, "<b>Что дальше?</b>", parse_mode="HTML", reply_markup=markup)
    elif message.text == "🔎 Поиск":
        if products_db.select_all_in_table():
            bot.send_message(message.chat.id, "<b><em>Склад пуст</em></b> 😅", parse_mode="HTML")
            return menu_command(message)
        else:
            search_command(message)
    elif message.text == "📄 Показать весь ассортимент":
        if products_db.select_all_in_table():
            bot.send_message(message.chat.id, "<b><em>Склад пуст</em></b> 😅", parse_mode="HTML")
            return menu_command(message)
        else:
            output_command(message)
    elif message.text == "⬅ Назад в меню":
        menu_command(message)
    elif message.text == "👤 О нас":
        about_command(message)

    else:
        markup = types.InlineKeyboardMarkup()

        button_menu = types.InlineKeyboardButton("Вернуться в меню", callback_data="menu_inl")
        markup.add(button_menu)

        bot.send_message(message.chat.id, "<em>Я вас не понимаю, нажмите на кнопку ниже, чтобы вернуться в <b>меню</b></em>", parse_mode="HTML", reply_markup=markup)


while True:
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        print(e)
        time.sleep(15)
