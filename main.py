import telebot
from telebot import types
from currency_converter import CurrencyConverter  


bot = telebot.TeleBot('7346618112:AAFQyASDWFy-_vZk5sw35ru9K5yHhZc0a0A')
currency = CurrencyConverter()
amount = 0
waiting_for_sum = False #управлениe состоянием пользователя

@bot.message_handler(commands=['start'])
def main(message):
    bot.send_message(message.chat.id, f'Привет, {message.from_user.first_name}, введите сумму')
    global waiting_for_sum
    waiting_for_sum = True
    bot.register_next_step_handler(message, get_sum)

def get_sum(message):
    global amount, waiting_for_sum
    if not waiting_for_sum:
        return  # Если не ожидаем ввода суммы, игнорируем сообщение

    try:
        amount = float(message.text.strip())
    except ValueError:
        bot.send_message(message.chat.id, 'Неверный формат, напишите сумму')
        bot.register_next_step_handler(message, get_sum)
        return

    if amount > 0:
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(
            types.InlineKeyboardButton('USD/EUR', callback_data='usd/eur'),
            types.InlineKeyboardButton('RUB/USD', callback_data='rub/usd'),
            types.InlineKeyboardButton('EUR/USD', callback_data='eur/usd'),
            types.InlineKeyboardButton('RUB/EUR', callback_data='rub/eur'),
            types.InlineKeyboardButton('Другое значение', callback_data='else')
        )
        bot.send_message(message.chat.id, 'Выберите валютную пару', reply_markup=markup)
        waiting_for_sum = False  # Ожидание валютной пары, флаг отключён
    else:
        bot.send_message(message.chat.id, 'Число должно быть больше, чем 0. Напишите сумму')
        bot.register_next_step_handler(message, get_sum)

@bot.callback_query_handler(func=lambda call: True)
def handle_currency_selection(call):
    global amount, waiting_for_sum

    # Проверяем, если пользователь уже ожидает ввода суммы
    if waiting_for_sum:
        return  # Игнорируем нажатия кнопок, если ожидаем ввод суммы

    if call.data != 'else':
        values = call.data.upper().split('/')
        try:
            result = currency.convert(amount, values[0], values[1])
            bot.send_message(call.message.chat.id, f'Получается: {round(result, 2)}. Можете заново вводить сумму.')
            waiting_for_sum = True  # ожидание ввода суммы
            bot.send_message(call.message.chat.id, 'Введите новую сумму')
            bot.register_next_step_handler(call.message, get_sum)
        except Exception as e:
            bot.send_message(call.message.chat.id, f'Ошибка конвертации: {str(e)}')
    else:
        bot.send_message(call.message.chat.id, 'Напишите валютную пару через слэш (например, USD/EUR)')
        bot.register_next_step_handler(call.message, handle_custom_currency)

def handle_custom_currency(message):
    global amount, waiting_for_sum
    if waiting_for_sum:
        return  

    try:
        values = message.text.upper().split('/')
        result = currency.convert(amount, values[0], values[1])
        bot.send_message(message.chat.id, f'Получается: {round(result, 2)}. Можете заново вводить сумму.')
        waiting_for_sum = True  
        bot.send_message(message.chat.id, 'Введите новую сумму')
        bot.register_next_step_handler(message, get_sum)
    except Exception as e:
        bot.send_message(message.chat.id, 'Неверный формат, напишите валютную пару через слэш')
        bot.register_next_step_handler(message, handle_custom_currency)

# Запуск бота
bot.polling(none_stop=True)