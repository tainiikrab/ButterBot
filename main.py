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
from random import randint
wikipedia.set_lang('ru')
morph = MorphAnalyzer()
client = commands.Bot(command_prefix='!')


@client.event
async def on_connect():
    print('Подключение...')


@client.event
async def on_disconnect():
    print('Переподключение...')


@client.event
async def on_ready():
    print('{0.user} начал работу'.format(client))


@client.command()
async def weather(ctx, city=""):
    """Показывает погоду в заданном городе"""
    if city == "":
        embed = discord.Embed(color=0xff0000, title='Введите название города')
        await ctx.send(embed=embed)
    else:
        embed = discord.Embed(color=0xed4b62, title='Ищу погоду...')
        await ctx.send(embed=embed)
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
            fn_main = ImageFont.truetype('data/14155.ttf', 136)
            fn_sunrise = ImageFont.truetype('data/14155.ttf', 113)
            fn_date = ImageFont.truetype('data/14155.ttf', 82)
            color = (255, 255, 255)
            img = Image.open('data/weather.png')
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
            embed = discord.Embed(color=0xff0000, title='Город не найден!')
            await ctx.send(embed=embed)


@client.command()
async def wiki(ctx, req="random"):
    """Отправляет запрошенную статью из Википедии"""
    req_name = req
    if req_name.lower() in ['рандом', 'random']:
        embed = discord.Embed(color=0xed4b62, title='Отправляю случайную статью...')
        await ctx.send(embed=embed)
        try:
            search_res = wikipedia.random()
            wiki_pg = wikipedia.page(title=search_res)
            urls = wiki_pg.images
            with open('wiki.jpg', 'wb') as wiki_img:
                wiki_img.write(requests.get(list(filter(lambda x: not x.endswith('.svg'), urls))[0]).content)
            wiki_summary = (wiki_pg.summary[:1900] + '...' if len(wiki_pg.summary) > 1900 else wiki_pg.summary)
            embed = discord.Embed(color=0xed4b62, title=search_res, description=wiki_summary)
            embed.add_field(name='Ссылка:', value=wiki_pg.url)
            embed.set_image(url=wiki_pg.images[0])  # Устанавливаем картинку Embed'a
            await ctx.send(embed=embed)

        except IndexError:
            embed = discord.Embed(color=0xff0000, title='Запрос не найден!')
            await ctx.send(embed=embed)
        except wikipedia.exceptions.DisambiguationError:
            embed = discord.Embed(color=0xff0000, title='Произошла ошибка, попробуйте еще раз')
            await ctx.send(embed=embed)
    else:
        embed = discord.Embed(color=0xed4b62, title=f'Ищу, что такое "{req_name}"...')
        await ctx.send(embed=embed)
        try:

            search_res = wikipedia.search(req_name, results=1)[0]
            wiki_pg = wikipedia.page(title=search_res)
            urls = wiki_pg.images
            with open('wiki.jpg', 'wb') as wiki_img:
                wiki_img.write(requests.get(list(filter(lambda x: not x.endswith('.svg'), urls))[0]).content)
            wiki_summary = (wiki_pg.summary[:1900] + '...' if len(wiki_pg.summary) > 1900 else wiki_pg.summary)
            embed = discord.Embed(color=0xed4b62, title=search_res, description=wiki_summary)
            embed.add_field(name='Ссылка:', value=wiki_pg.url)
            embed.set_image(url=wiki_pg.images[0])
            await ctx.send(embed=embed)
        except IndexError:
            embed = discord.Embed(color=0xff0000, title='Запрос не найден!')
            await ctx.send(embed=embed)
        except wikipedia.exceptions.DisambiguationError:
            embed = discord.Embed(color=0xff0000, title='Произошла ошибка, попробуйте еще раз')
            await ctx.send(embed=embed)


@client.command()
async def meme(ctx):
    """Отправляет мем"""
    response = requests.get('https://some-random-api.ml/meme')
    json_data = json.loads(response.text)
    embed = discord.Embed(color=0xed4b62, title=json_data['caption'])
    embed.set_image(url=json_data['image'])
    await ctx.send(embed=embed)


@client.command()
async def anecdote(ctx):
    """Отправляет анекдот"""
    response = requests.get(f'http://rzhunemogu.ru/RandJSON.aspx?CType=1')
    json_data = json.loads(json.dumps(response.text))
    embed = discord.Embed(color=0xed4b62, title='Внимание, анекдот!', description=json_data[12:-2])
    await ctx.send(embed=embed)


@client.command()
async def gif(ctx, title="Рандом"):
    """Отправляет гифку на выбранную тему"""
    embed = discord.Embed(color=0xed4b62, title="Ищу гифку...")
    await ctx.send(embed=embed)
    if title == "Рандом":
        response = requests.get('https://api.giphy.com/v1/gifs/random?api_key=Wg5q9ryG602qLq6ku36O9E2ovUp8VLfr&tag=&rating=pg-13')
        json_data = response.json()
        embed = discord.Embed(color=0xed4b62, title=f'{title} - это...')
        embed.set_image(url=json_data["data"]["images"]["original"]["url"])
        await ctx.send(embed=embed)
    else:
        try:
            response = requests.get(f'https://api.giphy.com/v1/gifs/search?api_key=Wg5q9ryG602qLq6ku36O9E2ovUp8VLfr&'
                                f'q={title}&limit=25&offset=0&rating=pg-13&lang=ru')
            json_data = response.json()
            embed = discord.Embed(color=0xed4b62, title=f'{title} - это...')
            embed.set_image(url=json_data["data"][randint(0, 24)]["images"]["original"]["url"])
            await ctx.send(embed=embed)
        except IndexError:
            response = requests.get(f'https://api.giphy.com/v1/gifs/search?api_key=Wg5q9ryG602qLq6ku36O9E2ovUp8VLfr&'
                                    f'q={"error"}&limit=25&offset=0&rating=pg-13&lang=ru')
            json_data = response.json()
            embed = discord.Embed(color=0xff0000, title='Гифка не найдена!')
            embed.set_image(url=json_data["data"][randint(0, 24)]["images"]["original"]["url"])
            await ctx.send(embed=embed)


# Запуск бота
client.run('NzE5ODg4NjY0MjQ2ODc4MjQ4.Xt9-kA.kY1hHV1CIRJLa-nYxLqoA3CQhlM')
