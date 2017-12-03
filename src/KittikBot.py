import telegram
import logging
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import urllib.request
import re
import time
import datetime

bot_token = '483459683:AAF3At_DQ4jCRX27KKb-eX4eWfYVmE0NcV8'

bot = telegram.Bot(token=bot_token)
updater = Updater(token=bot_token)
dispatcher = updater.dispatcher


my_Dictionary = {'Макс': 'Zalupa',
                 'Денис': 'Krasavchik',
                 'Сеня': 'Ты чё самый умный?',
                 'Вова': 'А ты точно стипендиат?'}


"""
For Mensa Command
"""

regexs = [('Linie 1', r'Linie 1(.*?)Linie 2'),
          ('Linie 2', r'Linie 2(.*?)Linie 3'),
          ('Linie 3', r'Linie 3(.*?)Linie 4/5'),
          ('Linie 4/5', r'Linie 4/5(.*?)Schnitzelbar'),
          ('Schnitzelbar', r'Schnitzelbar(.*?)L6')]

emojis = {'Cow Face': '\U0001F42E',
          'Pig Face': '\U0001F437',
          'Fish': '\U0001F41F',
          'Carrot': '\U0001F955',
          'Wheat': '\U0001F33E'}


def start_parsing():
    url = 'http://www.sw-ka.de/de/essen/'
    values = {'s': 'basics',
                'submit': 'search'}

    data = urllib.parse.urlencode(values)
    data = data.encode('utf-8')
    req = urllib.request.Request(url, data)
    resp = urllib.request.urlopen(url)
    resp_data = resp.read()
    table = re.findall(r'<div id=\"fragment-c1-1\" (.*?)>(.*?)<div id=\"fragment-c1-2\" (.*?)>', str(resp_data))

    return table


def line():
    return '--- --- --- --- ---\n'


def passing_umlauts(item):
    item = re.sub(r'<(.*?)>', '', str(item))
    item = re.sub(r'\\\\\\\\xc3\\\\\\\\xa4', 'ä', str(item))
    item = re.sub(r'\\\\\\\\xc3\\\\\\\\xbc', 'ü', str(item))
    item = re.sub(r'\\\\\\\\xc3\\\\\\\\xb6', 'ö', str(item))
    item = re.sub(r'\\\\\\\\xc3\\\\\\\\x9f', 'ß', str(item))
    return item


def passing_euro(item):
    item = re.sub(r'<(.*?)>', '', str(item))  #Remove all remaining <tags>
    item = re.sub(r'(&euro;)', '€', str(item))
    return item


def passing_emoji(dish):
    has_wheat_emoji = re.search(r'src=\"/layout/icons/vegan_2.gif\"', dish)  # WHEAT
    if has_wheat_emoji is not None:
        return str(emojis.get('Wheat'))

    has_carrot_emoji = re.search(r'src=\"/layout/icons/vegetarian_2.gif\"', dish)  # CARROT
    if has_carrot_emoji is not None:
        return str(emojis.get('Carrot'))

    has_pig_emoji = re.search(r'src=\"/layout/icons/s_2.gif\"', dish)  # PIG
    if has_pig_emoji is not None:
        return str(emojis.get('Pig Face'))

    has_cow_emoji = re.search(r'src=\"/layout/icons/(r_2|ra_2).gif\"', dish)  # COW
    if has_cow_emoji is not None:
        return str(emojis.get('Cow Face'))

    has_fish_emoji = re.search(r'src=\"/layout/icons/m_2.gif\"', dish)  # FISH
    if has_fish_emoji is not None:
        return str(emojis.get('Fish'))

    return ''


def generate_lines():

    today = datetime.datetime.today().weekday()

    if today >= 5:
        return 'К сожалению, менза не работает по выходным \U0001F63F' #Sad kitten face

    table = start_parsing()

    result = ''
    for regex in regexs:
        result += regex[0] + '\n'
        canteen_line = re.findall(regex[1], str(table))

        #Wenn die Linie geschlossen ist
        closed = re.search(r'Geschlossen', str(canteen_line))
        if closed is not None:
            result += 'К сожалению сегодня закрыта\n'
            result += line()
            continue

        #THIS WORKS
        #dishes = re.findall(r'<span class=\"bg\">(.*?)</span>', str(canteen_line))
        dishes = re.findall(r'<td class=\"mtd-icon\">(.*?)</span>', str(canteen_line))
        prices = re.findall(r'<span class="bgp price_1">(.*?)</span>', str(canteen_line))

        for i in range(dishes.__len__()):
            #THIS WORKS
            #dishes[i] = passing_umlauts(dishes[i])
            #prices[i] = passing_euro(prices[i])
            if prices[i].__len__() == 0:
                result += passing_umlauts(dishes[i]) + '\n'
            else:
                result += passing_emoji(dishes[i]) + passing_umlauts(dishes[i]) + ': ' + passing_euro(prices[i]) + '\n'

        result += line()

    return result


"""

"""


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)


def start(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text="Я китик")


def zhopa(bot, update):
    if update.message.text in my_Dictionary:
        bot.send_message(chat_id=update.message.chat_id, text=my_Dictionary.get(update.message.text))
    else:
        bot.send_message(chat_id=update.message.chat_id, text=update.message.text)


def mensa(bot, update):
    answer = generate_lines()
    bot.send_message(chat_id=update.message.chat_id, text = answer)


def test(bot, update):
    answer = str(update.message.from_user.first_name) + ', пошёл нахуй '
    bot.send_message(chat_id=update.message.chat_id, text=answer)


def print_periodical(bot, update, args):
    if args.__len__() == 1:
        bot.send_message(chat_id=update.message.chat_id, text=args[0])
        return

    number_of_plus = int(args[0])
    if number_of_plus > 25:
        bot.send_message(chat_id=update.message.chat_id, text='Угомонись, нахуя так много то?')
        return

    if number_of_plus < 0:
        bot.send_message(chat_id=update.message.chat_id, text='Мне че бля, в обратную сторону писать?')
        return

    sended_message = bot.send_message(chat_id=update.message.chat_id, text=args[1])

    for i in range(2, number_of_plus + 1):
        time.sleep(0.5)
        bot.edit_message_text(chat_id=sended_message.chat.id, message_id=sended_message.message_id, text=args[1] * i)


def plus_test(bot, update, args):
    args.append('+')
    print(args)
    print_periodical(bot, update, args)


def plus(bot, update, args):
    args.append('+')
    print_periodical(bot, update, args)


def bold_plus(bot, update, args):
    args.append('\U00002795')  #PLUS emoji
    print_periodical(bot, update, args)


def minus(bot, update, args):
    args.append('-')
    print_periodical(bot, update, args)


def mega_plus(bot, update):
    answer = '\U00002B1C\U00002B1C\U00002B1B\U00002B1C\U00002B1C\n' \
             '\U00002B1C\U00002B1C\U00002B1B\U00002B1C\U00002B1C\n' \
             '\U00002B1B\U00002B1B\U00002B1B\U00002B1B\U00002B1B\n' \
             '\U00002B1C\U00002B1C\U00002B1B\U00002B1C\U00002B1C\n' \
             '\U00002B1C\U00002B1C\U00002B1B\U00002B1C\U00002B1C\n'
    bot.send_message(chat_id=update.message.chat_id, text=answer)


def mega_minus(bot, update):
    answer = '\U00002B1C\U00002B1C\U00002B1C\U00002B1C\U00002B1C\n' \
             '\U00002B1C\U00002B1C\U00002B1C\U00002B1C\U00002B1C\n' \
             '\U00002B1B\U00002B1B\U00002B1B\U00002B1B\U00002B1B\n' \
             '\U00002B1C\U00002B1C\U00002B1C\U00002B1C\U00002B1C\n' \
             '\U00002B1C\U00002B1C\U00002B1C\U00002B1C\U00002B1C\n'
    bot.send_message(chat_id=update.message.chat_id, text=answer)


start_handler = CommandHandler('start', start)
message_handler = MessageHandler(Filters.text, zhopa)
mensa_handler = CommandHandler('mensa', mensa)
test_handler = CommandHandler('test', test)
plus_handler = CommandHandler('plus', plus, pass_args=True)
bold_plus_handler = CommandHandler('zhirniyPlus', bold_plus, pass_args=True)
minus_handler = CommandHandler('minus', minus, pass_args=True)
mega_plus_handler = CommandHandler('plusara', mega_plus)
mega_minus_handler = CommandHandler('minusara', mega_minus)

dispatcher.add_handler(message_handler)
dispatcher.add_handler(start_handler)
dispatcher.add_handler(mensa_handler)
dispatcher.add_handler(test_handler)
dispatcher.add_handler(plus_handler)
dispatcher.add_handler(minus_handler)
dispatcher.add_handler(bold_plus_handler)
dispatcher.add_handler(mega_plus_handler)
dispatcher.add_handler(mega_minus_handler)


updater.start_polling()
