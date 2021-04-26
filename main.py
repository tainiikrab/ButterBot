import discord
from discord.ext import commands
from pymorphy2 import MorphAnalyzer
import re
from collections import Counter
import matplotlib.pyplot as plt
import requests
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import wikipedia
import json
import requests
from discord import Embed, Emoji
from discord.ext.commands import Bot
from pprint import pprint
wikipedia.set_lang('ru')
morph = MorphAnalyzer()
client = commands.Bot(command_prefix='!')


@client.event
async def on_connect():
    print('Подключение к серверам Discord...')


@client.event
async def on_disconnect():
    print('Переподключение...')


@client.event
async def on_ready():
    print('{0.user} начал работу'.format(client))


@client.command()
async def get_info(ctx):
    """Отправляет статистику использованных слов"""
    # Описание комманды
    morph_dict = {'NOUN': 0, 'NPRO': 0, 'VERB': 0, 'ADJF': 0, 'ADVB': 0, 'PREP': 0, 'CONJ': 0}
    # Словарь с тегами
    messages_data = []
    # Список русских слов
    async for message in discord.TextChannel.history(ctx, limit=None):
        if message.author != client.user and not message.content.startswith('!'):
            messages_data.append(message.content)
    # Если сообщение не от бота и не является командой, то добавляем
    messages_data = list(filter(lambda x: x != '',
                                re.sub(r"[^А-Яа-яЁё ]*", '',
                                       re.sub(r"[.,/+\"\'!:;]", ' ', ' '.join(messages_data))).split(' ')))
    # Убираем знаки препинания, оставляем только слова из русских букв)
    data = Counter(map(lambda x: morph.parse(x)[0].tag.POS, messages_data))
    # Объект типа Counter {Тег : кол-во слов}
    for i in data:
        if i in morph_dict:
            morph_dict[i] += data[i]
    # Обновляем словарь с тегами
    data, x = morph_dict.values(), range(7)
    # Кол-ва слов каждого типа, 7 столбцов
    fig, ax = plt.subplots()
    # Не понял что это, но без него не работает))
    plt.bar(x, data)
    # Создаем график типа bar
    plt.xticks(x, ('Сущ', 'Мест', 'Глаг', 'Прил', 'Нареч', 'Пред', 'Союз'))
    # Подписываем столбцы
    ax.set_title('Количество слов по частям речи:')
    plt.savefig('info.png')
    # Сохраняем график

    for i in range(len(messages_data)):
        messages_data[i] = (morph.parse(messages_data[i])[0]).normal_form
    # Приводим слова в исходную форму
    data = {}
    for i in Counter(messages_data):
        if "NPRO" not in morph.parse(i)[0].tag and "PREP" not in morph.parse(i)[0].tag \
                and "CONJ" not in morph.parse(i)[0].tag:
            data[i] = messages_data.count(i)
    # Формируем словарь, ключами которого являются слова, а значениями - количество их повторений
    lst = list(data.items())
    lst.sort(key=lambda i: i[1], reverse=True)
    # Создаём из словаря список кортежей вида "(слово, кол-во повторений)" для того, чтобы его можно было отсортировать.
    comment = morph.parse('повторение')[0]
    try:
        await ctx.send(
            f'Топ-5 слов на этом канале:\n1.) "{lst[0][0]}", {lst[0][1]} {comment.make_agree_with_number(lst[0][1]).word}\n'
            f'2.) "{lst[1][0]}", {lst[1][1]} {comment.make_agree_with_number(lst[1][1]).word}\n3.) "{lst[2][0]}", {lst[2][1]} {comment.make_agree_with_number(lst[2][1]).word}\n'
            f'4.) "{lst[3][0]}", {lst[3][1]} {comment.make_agree_with_number(lst[3][1]).word}\n5.) "{lst[4][0]}", {lst[4][1]} {comment.make_agree_with_number(lst[4][1]).word}\n',
            file=discord.File('info.png'))
    except IndexError:
        await ctx.send("К сожалению, эта команда не работает в личных сообщениях.")

        # Приводим слова в соответствие с чилительными и отправляем

@client.command()
async def weather(ctx, city):
    """Показывает погоду в заданном городе"""
    try:
        city_name = city
        params = {
            'q': city_name,
            'units': 'metric',
            'appid': '5ffd78188a2352cc9d6281eb6b29f0ff'
        }
        response = requests.get("https://api.openweathermap.org/data/2.5/weather", params=params)
        json_response = response.json()
        temperature = json_response['main']['temp']
        feels_like = json_response['main']['feels_like']
        sunrise, sunset = datetime.fromtimestamp(
            json_response['sys']['sunrise'] - 36000 + json_response['timezone']), datetime.fromtimestamp(
            json_response['sys']['sunset'] - 36000 + json_response['timezone'])
        wind = json_response['wind']['speed']
        ico = json_response['weather'][0]['icon']
        icon = open('icon.png', 'wb')
        icon.write(requests.get(f"http://openweathermap.org/img/wn/{ico}@2x.png").content)
        icon.close()
        ico = Image.open('icon.png')
        resized_ico = ico.resize((400, 400), Image.ANTIALIAS)
        fn_main = ImageFont.truetype('14155.ttf', 136)
        fn_sunrise = ImageFont.truetype('14155.ttf', 113)
        fn_date = ImageFont.truetype('14155.ttf', 82)
        color = (255, 255, 255)
        img = Image.open('weather.png')
        draw = ImageDraw.Draw(img)
        value = datetime.now()
        draw.text((140, 180), f'Погода в городе {city_name}:', font=fn_main, fill=color)
        draw.text((129, 906), f'Температура воздуха: {int(temperature)}°', font=fn_main, fill=color)
        draw.text((129, 1077), f'Ощущается как: {int(feels_like)}°', font=fn_main, fill=color)
        draw.text((129, 1244), f'Скорость ветра: {wind} м/с', font=fn_main, fill=color)
        draw.text((129, 1440), f"Рассвет: {':'.join(str(sunrise.time()).split(':')[:-1])}", font=fn_sunrise, fill=color)
        draw.text((1253, 1440), f"Закат: {':'.join(str(sunset.time()).split(':')[:-1])}", font=fn_sunrise, fill=color)
        draw.text((1700, 604), value.date().strftime('%d.%m'), font=fn_date, fill=color)
        draw.text((438, 752), json_response['weather'][0]['description'], font=fn_date, fill=color)
        img.paste(resized_ico, (80, 530), resized_ico)
        img.save("weather_stat.png")
        await ctx.send(file=discord.File('weather_stat.png'))
    except KeyError:
        await ctx.send('Город не найден:(')


@client.command()
async def wiki(ctx, req):
    """Отправляет запрошенную статью из Википедии"""
    req_name = req
    if req_name.lower() in ['рандом', 'random']:
        try:
            search_res = wikipedia.random()
            wiki_pg = wikipedia.page(title=search_res)
            urls = wiki_pg.images
            with open('wiki.jpg', 'wb') as wiki_img:
                wiki_img.write(requests.get(list(filter(lambda x: not x.endswith('.svg'), urls))[0]).content)
            wiki_summary = (wiki_pg.summary[:1900] + '...' if len(wiki_pg.summary) > 1900 else wiki_pg.summary)
            # await ctx.send(wiki_pg.url + '\n' + wiki_summary, file=discord.File('wiki.jpg'))
            embed = discord.Embed(color=0xff9900, title=search_res, description=wiki_summary)  # Создание Embed'a
            embed.add_field(name='Ссылка:', value=wiki_pg.url)
            embed.set_image(url=wiki_pg.images[0])  # Устанавливаем картинку Embed'a
            await ctx.send(embed=embed)  # Отправляем Embed

        except IndexError:
            await ctx.send('Запрос не найден:(')
        except wikipedia.exceptions.DisambiguationError:
            await ctx.send('Произошла ошибка, попробуйте еще раз:(')
    else:
        try:
            search_res = wikipedia.search(req_name, results=1)[0]
            wiki_pg = wikipedia.page(title=search_res)
            urls = wiki_pg.images
            with open('wiki.jpg', 'wb') as wiki_img:
                wiki_img.write(requests.get(list(filter(lambda x: not x.endswith('.svg'), urls))[0]).content)
            wiki_summary = (wiki_pg.summary[:1900] + '...' if len(wiki_pg.summary) > 1900 else wiki_pg.summary)
            # await ctx.send(wiki_pg.url + '\n' + wiki_summary, file=discord.File('wiki.jpg'))
            embed = discord.Embed(color=0xff9900, title=search_res, description=wiki_summary)  # Создание Embed'a
            embed.add_field(name='Ссылка:', value=wiki_pg.url)
            embed.set_image(url=wiki_pg.images[0])  # Устанавливаем картинку Embed'a
            await ctx.send(embed=embed)  # Отправляем Embed
        except IndexError:
            await ctx.send('Запрос не найден:(')
        except wikipedia.exceptions.DisambiguationError:
            await ctx.send('Произошла ошибка, попробуйте еще раз:(')


@client.command()
async def fox(ctx):
    response = requests.get('https://some-random-api.ml/img/fox')  # Get-запрос
    json_data = json.loads(response.text)  # Извлекаем JSON

    embed = discord.Embed(color=0xff9900, title='Random Fox')  # Создание Embed'a
    embed.set_image(url=json_data['link'])  # Устанавливаем картинку Embed'a
    await ctx.send(embed=embed)  # Отправляем Embed


client.run('NzE5ODg4NjY0MjQ2ODc4MjQ4.Xt9-kA.R0sm5OUftEF3Q_l9kvErjMz2mNA')
# Запуск бота)
