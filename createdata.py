from __future__ import print_function
import json
import requests
import urllib.parse
from collections import deque
import matplotlib.dates
import matplotlib.pyplot
import discord
import os

client = discord.Client()
TOKEN = ''
GUILD = ''

@client.event
async def on_ready():
    for guild in client.guilds:
        if guild.name == GUILD:
            break

    print(
        f'{client.user} is connected to the following guild:\n'
        f'{guild.name}(id: {guild.id})'
    )
@client.event
async def on_message(message):
    if '$' in message.content.lower() and len(message.content) < 7:
        ticker = message.content[1:]
        quote = requests.get('https://api.twelvedata.com/quote?symbol=' + ticker + '&apikey=')
        if 'code' in str(quote.json()):
            await message.channel.send('I cannot find ticker: ' + ticker)
        else:
            quoteopen= quote.json()['open']

            response = requests.get(
                "https://api.twelvedata.com/time_series?interval=5min&symbol=" + ticker + "&apikey=")
            dates = deque()
            closes = deque()
            for value in response.json()['values']:
                dateval = value['datetime']
                dates.append(dateval)
                closes.append(float(value['close']))
            currprice = closes.popleft()
            dateaxis = matplotlib.dates.date2num(dates)
            closes.appendleft(float(currprice))
            if float(currprice) < float(quoteopen):
                matplotlib.pyplot.plot_date(dateaxis, closes, linestyle='solid', color='red')
            else:
                matplotlib.pyplot.plot_date(dateaxis, closes, linestyle='solid', color='green')
            matplotlib.pyplot.xlabel("Current Price " + str(closes.popleft()) + ' at ' + str(dates.popleft()[11:]))
            matplotlib.pyplot.axhline(y=float(quoteopen), linestyle='dashed', color='black')
            matplotlib.pyplot.title("Chart for " + ticker.upper())
            matplotlib.pyplot.savefig('chart.png')
            file = discord.File("chart.png", filename="chart.png")
            await message.channel.send(file=file)
            matplotlib.pyplot.clf()

client.run(TOKEN)


