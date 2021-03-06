import discord
from discord.ext import commands
from discord.ext.commands import cooldown, BucketType, CommandOnCooldown, Context, CommandNotFound, BadArgument
import requests as rq
from bs4 import BeautifulSoup
import csv
import json
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os
from plottingFunctions import plotDev
from Plot import Plot, DevPlot

IGNORE_EXCEPTIONS = (CommandNotFound, BadArgument)
client = commands.Bot(command_prefix='!SkanderBot ')

#------------------ENV Vars--------------------
# SKANDERBEG_API = os.environ['SKANDERBEG API']
# SKANDERBEG_WEEKS = {
#     "Week 1": os.environ['SKANDERBEG WK1'],
#     "Week 2": os.environ['SKANDERBEG WK2']
# }
SKANDERBEG_API = "2fe79beca3a56dbf49185845ce109cec"
DISCORD_KEY = "ODgxMzU2ODY0MDcwMjM4MjA5.YSrpiw.7baeGE4lbKUmGDU3cRxuAtiM6gU"


#-------------------SETUP---------------------
client.remove_command('help')


@commands.Cog.listener()
async def on_command_error(self, ctx, exc):
    if isinstance(exc, CommandOnCooldown):
        emb = discord.Embed(
            title='Shut up and let me think!',
            description=
            f'That command is on cooldown, try again in {exc.retry_after:,.2f} seconds.',
            color=0xFFBF00)
        await ctx.send(embed=emb)


#--------------------EVENTS--------------------
# bot ready statement on start
@client.event
async def on_ready():
    print('bot ready')


#-------------------COMMANDS---------------------------


#~~~~~~~~~~~~~~~~~~~~~PING~~~~~~~~~~~~~~~~~~~~~~~
@client.command()
@cooldown(1, 15, BucketType.user)
async def ping(ctx):
    await ctx.send(f'pong {round(client.latency * 1000)}ms')


#~~~~~~~~~~~~~~~~~~~~~HELP~~~~~~~~~~~~~~~~~~~~~
@client.command(pass_context=True)
@cooldown(1, 15, BucketType.user)
async def help(ctx):
    author = ctx.message.author
    embed = discord.Embed(colour=discord.Colour.dark_blue())
    embed.set_author(name='Help')
    embed.add_field(
        name='Description',
        value=
        'The Goal of this bot is to make graphs for Europa universalis 4,by using the Skanderbeg save data',
        inline=False)
    embed.add_field(name='!SkanderBot ping',
                    value='returns pong!',
                    inline=False)
    embed.add_field(
        name='!SkanderBot graphs',
        value=
        f'if you want to make graphs use this format: \n !SkanderBot graphs Skanderbeg_Save_ID \n Ex:  !SkanderBot graphs d852c8 \n you can get the Skanderbeg_Save_ID in the skanderbeg site in the ID column in My Maps (https://skanderbeg.pm/maps.php)',
        inline=False)
    embed.add_field(name='!SkanderBot creator',
                    value='returns the discord id of me:the creator',
                    inline=False)
    await ctx.send(embed=embed)


#~~~~~~~~~~~~~~~~~~~~~CREATOR~~~~~~~~~~~~~~~~~~~~~
@client.command()
@cooldown(1,15, BucketType.user)
async def creator(ctx):
  await ctx.send('The first creator of this bot is mak84271#3674.\nMasonStevens95#5018 then picked up the torch to refactor and add functionality including 3D chart plotting, and the ability to see multiple Skanderbeg campaigns at one time (soon).\nIf you want to help with this monetarily, please donate to the Skanderbeg Patreon :) https://www.patreon.com/skanderbeg')


#~~~~~~~~~~~~~~~~~~~~~LOCKED LEDGER GRAPHS~~~~~~~~~~~~~~~~~~~~~
# @client.command()
# @cooldown(1, 120, BucketType.user)
# async def lockedLedgerGraphs(ctx, *, code):

#~~~~~~~~~~~~~~~~~~~~~GRAPHS~~~~~~~~~~~~~~~~~~~~~
@client.command()
@cooldown(1, 120, BucketType.user)
async def graphs(ctx, *, code):

    await ctx.send('wait for the graphs')
    a = code
    save = code

    print('do you want to compare this save with an older one?[y/n]')
    resp1 = 'n'
    save2 = ''
    if resp1 == 'y':
        print('type the older skanderbeg Save code')
        save2 = input()

    print('do you want to show only players?[y/n]')
    ia = 'y'
    try:
        with open('folder.txt') as f:
            folder = f.read()
            f.close()
    except:
        f = open('folder.txt', 'x')
        folder = ''
    if folder == '':
        print(
            'please indicate the location of the folder where you want to store your graphs'
        )
        folder = ''
        with open('folder.txt', 'wt') as z:
            z.write(str(folder))

    if ia == 'y' or ia == 'yes':
        ia = '&playersOnly=yes'
    else:
        ia = ''

    url = getUrl(save, ia)

    #gets response from Skanderbeg API, parses to data.json file
    response = rq.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    with open('data.json', 'w', encoding='utf-8') as f_out:
        f_out.write(soup.prettify())

    #loads data.json into a variable, data
    with open('data.json') as json_file:
        try:
            data = json.load(json_file)
        except:
            await ctx.send(
                f'Invalid Skanderbeg Save id / the Skanderbeg server is offline \n Try to redo the command with the correct id or dm me with:,creator'
            )

    #creates dataframe with pandas, based on what stats wanted in the API call
    df = pd.read_json('data.json')
    corpus = df.iloc[0][1]
    csv_columns = [
        'tag', 'fdp', 'battleCasualties', 'max_manpower', 'countryName',
        'player', 'total_development', 'spent_total',
        'total_mana_on_teching_up', 'provinces', 'qualityScore', 'inc_no_subs',
        'total_army', 'total_mana_spent_on_deving', 'buildings_value',
        'continents', 'total_navy', 'dev_clicks', 'deving_stats', 'hex'
    ]

    #grabs all the tags, adds them as the first column of the table
    i = 0
    dict = []
    tags = []
    for tag in data:
        tags.append(tag)
    while i < len(df.columns):
        a = df.iloc[0][i]
        a.update({'tag': tags[i]})
        dict.append(a)
        i = i + 1

    #writes provences to a CSV
    csv_file = "found.csv"
    try:
        with open(csv_file, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
            writer.writeheader()
            for data in dict:
                for key, value in data.items():
                    if key == 'provinces' and int(value) >= 1:
                        writer.writerow(data)
    except IOError:
        print("I/O error")

    #does it again if save 2 exists
    #TODO: abstract this to any number of saves
    if save2 != '':
        url = getUrl(save2, ia)
        response = rq.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        with open('data.json', 'w', encoding='utf-8') as f_out:
            f_out.write(soup.prettify())

        with open('data.json') as json_file:
            data = json.load(json_file)

        df = pd.read_json('data.json')
        corpus = df.iloc[0][1]
        csv_columns = [
            'tag', 'fdp', 'battleCasualties', 'max_manpower', 'countryName',
            'player', 'total_development', 'spent_total',
            'total_mana_on_teching_up', 'provinces', 'qualityScore',
            'inc_no_subs', 'total_army', 'total_mana_spent_on_deving',
            'buildings_value', 'continents', 'total_navy', 'dev_clicks',
            'deving_stats', 'hex'
        ]

        i = 0
        dict = []
        tags = []
        for tag in data:
            tags.append(tag)
        while i < len(df.columns):
            a = df.iloc[0][i]
            a.update({'tag': tags[i]})
            dict.append(a)
            i = i + 1

        csv_file = "found2.csv"
        try:
            with open(csv_file, 'w', newline='') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
                writer.writeheader()
                for data in dict:
                    for key, value in data.items():
                        if key == 'provinces' and int(value) >= 1:
                            writer.writerow(data)
        except IOError:
            print("I/O error")

    #writes the found to .csv
    with open('found.csv', 'r') as csvfile:
        lines = csvfile.readlines()
    x = 'found.csv'
    y = 'found2.csv'

    #writes to pandas dataframe
    df1 = pd.read_csv(x, encoding='latin1')
    try:
        df2 = pd.read_csv(y, encoding='latin1')
    except:
        y = 'found.csv'
        df2 = pd.read_csv(y, encoding='latin1')

    #cleans up DF values
    def replace(df):
        a = df.columns
        # print("replace funciton, here is df before transform: ")
        # print(df)
        list(a)
        h = []
        j = []
        for x in a:
            h.append(x)
            if x == '|':
                x = 'tag'
            y = x.replace('|', '')
            z = y.replace('_', '')
            j.append(z)
        df.rename(columns={x: y for x, y in zip(h, j)}, inplace=True)
        # print("replace funciton, here is df after transform: ")
        # print(df)

    replace(df1)
    replace(df2)

    #fills N/A values with 0
    df1['totalarmy'] = df1['totalarmy'].fillna(0)
    df1['totalnavy'] = df1['totalnavy'].fillna(0)
    df2['totalarmy'] = df2['totalarmy'].fillna(0)
    df2['totalnavy'] = df2['totalnavy'].fillna(0)
    df1['buildingsvalue'] = df1['buildingsvalue'].fillna(0)
    df2['buildingsvalue'] = df2['buildingsvalue'].fillna(0)

    #lista1 is used for when there are multiple weeks. will have to be refactored TODO
    lista1 = [df1, df2]
    lista = [df1]

    #tags to list
    tags = df1['tag'].tolist()
    # tagss = tags

    #get "countries" list not really players. will refactor later TODO
    players = df1['countryName'].tolist()
    i = 0
    # print("Players list: \n")
    # print(players)

    #This normalizes the tags
    for player in players:
        if type(player) == type(0.54):
            players[i] = tags[i]
        i += 1

    #grabs all the dataframes
    allDataFrames = trial(lista, tags, players)
    k = 0

    # colors graphic. assigned later, but not used?
    colors = [
        'black', 'grey', 'rosybrown', 'brown', 'darkred', 'red', 'tomato',
        'coral', 'orangered', 'sienna', 'peru', 'orange', 'goldenrod', 'gold',
        'khaki', 'olive', 'yellow', 'lawngreen', 'green', 'lime', 'teal',
        'cyan', 'steelblue', 'navy', 'blue', 'blueviolet', 'indigo', 'violet',
        'magenta', 'deeppink'
    ]

    #Listaz is actually just all the country names
    listaz = allDataFrames[0].columns
    nationColor = {}
    count = 0
    hex = df1['hex']
    for nation in listaz:
        nationColor[nation] = hex[count]
        count = count + 1

    #find maximum number of players
    az = np.linspace(0, 1, len(players))
    playerMaximum = len(lines) - 1
    if playerMaximum > 20:
        resp = ' but the optimal maximum is around 20'
        y = str(20)
    else:
        resp = ''
        y = str(playerMaximum)

    print('how many nation do you want ot print? the max is ' +
          str(playerMaximum) + resp)

    #I believe this is prepping the graphs with max player numbers
    y = int(y)
    f = 100 / y
    alpha1 = 0.8
    alphagrid = 0.4
    sz = adjustTextSpacingOfColumns(y)
    sizes = adjustTextSizeForColumns(y)

    #print all dataframes for reference
    # allDataFrames.to_csv('allDataFrames.csv')

    #actually does the plotting
    for s in allDataFrames:
        # s.to_csv(str(k))
        if k == 0:  # dev
            #dataframe, text spacing of column, text size for column, nation color, 100/player count, folder, alpha, alpha grid, player count
            #plotDev(s, sz, sizes, nationColor, f, folder, alpha1, alphagrid, y)
            devPlot = DevPlot(s, sz, sizes, nationColor, f, folder, alpha1, alphagrid, y)
            devPlot.plotDev()

        if k == 1:  # income
            plt.figure(figsize=[19.2, 10.8])
            s = s.sort_values(by=(len(s) - 1), axis=1,
                              ascending=False)  # sort data
            plt.xticks(rotation=-90)

            s = s.iloc[:, range(0, y)]
            coloriar = []
            for nomej in s.columns:
                coloriar.append(nationColor[nomej])

            ax1 = s.loc[len(s) - 1].plot.bar(color=coloriar,
                                             alpha=alpha1,
                                             edgecolor='black')  # bar plt
            plt.grid(axis='y', alpha=alphagrid)

            plt.xticks(rotation=-90)

            plt.ylabel('income')
            somma = 0
            for a in s.loc[len(s) - 1]:  # somma ultima riga matrice
                somma = somma + a
            h = 0
            percentuali = []
            for ap in s.loc[len(s) - 1]:
                h += ((ap / somma) * 100)
                percentuali.append(h)
            balances = []
            q = f
            for l in percentuali:
                d = l - q
                balances.append(d)
                q += f
            j = max(balances)
            pvalue = (1 - ((j**2) / 2500)) * 100
            ax2 = ax1.twinx()
            ax2.spines['right'].set_position(('axes', 1.0))
            plt.ylim(0, 101)
            plt.plot(percentuali, marker='o', color='r')  # linea paretiana
            ax1.set_title('income' + '       Balancing%=' +
                          str(round(pvalue)) + '%')
            plt.ylabel('% of income on total')
            j = 0
            for i, v in enumerate(percentuali):  # testo su linea
                ax2.text(i - 0.10,
                         v + 1,
                         str(round(v)) + '%',
                         color='black',
                         fontweight='bold',
                         size=sizes)
            for i, v in enumerate(s.loc[len(s) - 1]):  # testo su barre
                ax1.text(i - len(str(round(v))) * sz,
                         v + 0.5,
                         str(round(v)),
                         color='black',
                         fontweight='bold',
                         size=sizes)
            plt.savefig(folder + 'income.png')
            plt.close()
        if k == 2:  # valore immobili
            plt.figure(figsize=[19.2, 10.8])
            s = s.sort_values(by=(len(s) - 1), axis=1, ascending=False)
            if y > 10:
                hj = s.iloc[:, range(10, y)]
                s = s.iloc[:, range(0, 10)]
                others = 0
                counting = 0
                coloriar = []
                hh = hj.values.tolist()
                for value in hh[0]:
                    others = others + value
                    counting = counting + 1
                s['Others'] = others

                for nomej in s.columns:
                    try:
                        coloriar.append(nationColor[nomej])
                    except:
                        coloriar.append('gray')
            else:
                coloriar = []
                for nomej in s.columns:
                    try:
                        coloriar.append(nationColor[nomej])
                    except:
                        coloriar.append('gray')

            ax2 = s.loc[len(s) - 1].plot.pie(
                autopct=lambda pct: func(pct, s.loc[len(s) - 1]),
                startangle=90,
                radius=1.3,
                colors=coloriar)
            plt.grid(axis='y', alpha=alphagrid)

            ax2.text(-0.3,
                     1.5,
                     'Buildings Value',
                     color='black',
                     fontweight='bold',
                     size=sizes)
            plt.savefig(folder + 'Buildings Value.png')
            plt.close()
        if k == 3:  # province
            plt.figure(figsize=[19.2, 10.8])
            s = s.sort_values(by=(len(s) - 1), axis=1,
                              ascending=False)  # sort data
            s = s.iloc[:, range(0, y)]
            coloriar = []
            for nomej in s.columns:
                coloriar.append(nationColor[nomej])

            ax1 = s.loc[len(s) - 1].plot.bar(color=coloriar,
                                             alpha=alpha1,
                                             edgecolor='black')  # bar plt
            plt.grid(axis='y', alpha=alphagrid)
            plt.xticks(rotation=-90)

            plt.ylabel('provinces')
            somma = 0
            for a in s.loc[len(s) - 1]:  # somma ultima riga matrice
                somma = somma + a
            h = 0
            percentuali = []
            for ap in s.loc[len(s) - 1]:
                h += ((ap / somma) * 100)
                percentuali.append(h)
            ax2 = ax1.twinx()
            ax2.spines['right'].set_position(('axes', 1.0))
            plt.ylim(0, 101)
            plt.plot(percentuali, marker='o', color='g')  # linea paretiana
            ax1.set_title('provinces')
            plt.ylabel('% of provinces on total')
            j = 0
            for i, v in enumerate(percentuali):  # testo su linea
                ax2.text(i - 0.10,
                         v + 1,
                         str(round(v)) + '%',
                         color='black',
                         fontweight='bold',
                         size=sizes)
            for i, v in enumerate(s.loc[len(s) - 1]):  # testo su barre.
                ax1.text(i - len(str(round(v, 1))) * sz,
                         v + 0.5,
                         str(round(v, 1)),
                         color='black',
                         fontweight='bold',
                         size=sizes)
            plt.savefig(folder + 'provinces.png')
            plt.close()
        if k == 4:
            plt.figure(figsize=[19.2, 10.8])
            s = s.sort_values(by=(len(s) - 1), axis=1,
                              ascending=False)  # sort data
            s = s.iloc[:, range(0, y)]
            coloriar = []
            for nomej in s.columns:
                coloriar.append(nationColor[nomej])

            ax1 = s.loc[len(s) - 1].plot.bar(color=coloriar,
                                             alpha=alpha1,
                                             edgecolor='black')  # bar plt
            plt.grid(axis='y', alpha=alphagrid)

            plt.xticks(rotation=-90)

            plt.ylabel('Battle casualities')
            somma = 0
            for a in s.loc[len(s) - 1]:  # somma ultima riga matrice
                somma = somma + a
            h = 0
            percentuali = []

            for ap in s.loc[len(s) - 1]:
                try:
                    h += ((ap / somma) * 100)
                except:
                    pass
                percentuali.append(h)
            ax2 = ax1.twinx()
            ax2.spines['right'].set_position(('axes', 1.0))
            plt.ylim(0, 101)
            plt.plot(percentuali, marker='o', color='g')  # linea paretiana
            ax1.set_title('Battle casualities')
            plt.ylabel('% battle casualities on total')
            j = 0
            for i, v in enumerate(percentuali):  # testo su linea
                ax2.text(i - 0.10,
                         v + 1,
                         str(round(v)) + '%',
                         color='black',
                         fontweight='bold',
                         size=sizes)
            for i, v in enumerate(s.loc[len(s) - 1]):  # testo su barre
                if v >= 100000:
                    ax1.text(i - len(str(round(v / 1000000, 1)) + 'M') * sz,
                             v + 0.5,
                             str(round(v / 1000000, 1)) + 'M',
                             color='black',
                             fontweight='bold',
                             size=sizes)
                else:
                    ax1.text(i - len(str(round(v / 1000, 1)) + 'k') * sz,
                             v + 0.5,
                             str(round(v / 1000, 1)) + 'k',
                             color='black',
                             fontweight='bold',
                             size=sizes)

            plt.savefig(folder + 'Battle casualities.png')
            plt.close()
        if k == 5:
            plt.figure(figsize=[19.2, 10.8])

            s = s.sort_values(by=(len(s) - 1), axis=1,
                              ascending=False)  # sort data
            s = s.iloc[:, range(0, y)]
            coloriar = []
            for nomej in s.columns:
                coloriar.append(nationColor[nomej])

            ax1 = s.loc[len(s) - 1].plot.bar(color=coloriar,
                                             alpha=alpha1,
                                             edgecolor='black')  # bar plt
            plt.grid(axis='y', alpha=alphagrid)

            plt.xticks(rotation=-90)

            plt.ylabel('Total armies')
            somma = 0
            for a in s.loc[len(s) - 1]:  # somma ultima riga matrice
                somma = somma + a
            h = 0
            percentuali = []
            for ap in s.loc[len(s) - 1]:
                h += ((ap / somma) * 100)
                percentuali.append(h)
            balances = []
            q = f
            for l in percentuali:
                d = l - q
                balances.append(d)
                q += f
            j = max(balances)
            pvalue = (1 - ((j**2) / 2500)) * 100
            ax2 = ax1.twinx()
            ax2.spines['right'].set_position(('axes', 1.0))
            plt.ylim(0, 101)
            plt.plot(percentuali, marker='o', color='y')  # linea paretiana
            ax1.set_title('armies' + '       Balancing%=' +
                          str(round(pvalue)) + '%')
            plt.ylabel('% Armies on total')
            j = 0
            for i, v in enumerate(percentuali):  # testo su linea
                ax2.text(i - 0.10,
                         v + 1,
                         str(round(v)) + '%',
                         color='black',
                         fontweight='bold',
                         size=sizes)
            for i, v in enumerate(s.loc[len(s) - 1]):  # testo su barre
                ax1.text(i - len(str(int(v))) * sz,
                         v + 0.5,
                         str(int(v)),
                         color='black',
                         fontweight='bold',
                         size=sizes)
            plt.savefig(folder + 'armies.png')
            plt.close()
        if k == 7:
            plt.figure(figsize=[19.2, 10.8])

            s = s.sort_values(by=(len(s) - 1), axis=1,
                              ascending=False)  # sort data
            s = s.iloc[:, range(0, y)]
            coloriar = []
            for nomej in s.columns:
                coloriar.append(nationColor[nomej])

            ax1 = s.loc[len(s) - 1].plot.bar(color=coloriar,
                                             alpha=alpha1,
                                             edgecolor='black')  # bar plt
            plt.grid(axis='y', alpha=alphagrid)

            plt.xticks(rotation=-90)

            plt.ylabel('Mana spent on devving')
            somma = 0
            for a in s.loc[len(s) - 1]:  # somma ultima riga matrice
                somma = somma + a
            h = 0
            percentuali = []
            for ap in s.loc[len(s) - 1]:
                try:
                    h += ((ap / somma) * 100)
                except:
                    pass
                percentuali.append(h)
            ax1.set_title('Mana spent on devving')
            j = 0

            for i, v in enumerate(s.loc[len(s) - 1]):  # testo su barre
                ax1.text(i - len(str(round(v / 1000, 1)) + 'k') * sz,
                         v + 0.5,
                         str(round(v / 1000, 1)) + 'k',
                         color='black',
                         fontweight='bold',
                         size=sizes)
            plt.savefig(folder + 'Mana spent on devving.png')
            plt.close()
        if k == 8:
            plt.figure(figsize=[19.2, 10.8])

            s = s.sort_values(by=(len(s) - 1), axis=1,
                              ascending=False)  # sort data
            s = s.iloc[:, range(0, y)]
            coloriar = []
            for nomej in s.columns:
                coloriar.append(nationColor[nomej])

            ax1 = s.loc[len(s) -
                        1].plot.bar(color=coloriar,
                                    alpha=alpha1,
                                    edgecolor='black')  # bar plt # bar plt
            plt.grid(axis='y', alpha=alphagrid)

            plt.xticks(rotation=-90)

            plt.ylabel('Mana spent on teching up')
            a = s.loc[len(s) - 1]
            plt.ylim(a[-1] - 500, a[0] + 500)
            somma = 0
            for a in s.loc[len(s) - 1]:  # somma ultima riga matrice
                somma = somma + a
            h = 0
            percentuali = []
            for ap in s.loc[len(s) - 1]:
                try:
                    h += ((ap / somma) * 100)
                except:
                    pass

                percentuali.append(h)
            ax1.set_title('Mana spent on teching up')
            j = 0

            for i, v in enumerate(s.loc[len(s) - 1]):  # testo su barre
                ax1.text(i - len(str(round(v / 1000, 1)) + 'k') * sz,
                         v + 0.5,
                         str(round(v / 1000, 1)) + 'k',
                         color='black',
                         fontweight='bold',
                         size=sizes)
            plt.savefig(folder + 'Mana spent on teching up.png')
            plt.close()
        if k == 9:
            plt.figure(figsize=[19.2, 10.8])

            s = s.sort_values(by=(len(s) - 1), axis=1,
                              ascending=False)  # sort data
            s = s.iloc[:, range(0, y)]
            coloriar = []
            for nomej in s.columns:
                coloriar.append(nationColor[nomej])

            ax1 = s.loc[len(s) - 1].plot.bar(color=coloriar,
                                             alpha=alpha1,
                                             edgecolor='black')  # bar plt
            plt.grid(axis='y', alpha=alphagrid)

            plt.xticks(rotation=-90)

            plt.ylabel('money spent')
            plt.title('money spent')
            somma = 0
            for a in s.loc[len(s) - 1]:  # somma ultima riga matrice
                somma = somma + a
            for i, v in enumerate(s.loc[len(s) - 1]):  # testo su barre
                if v >= 100000:
                    ax1.text(i - len(str(round(v / 1000000, 1)) + 'M') * sz,
                             v + 0.5,
                             str(round(v / 1000000, 1)) + 'M',
                             color='black',
                             fontweight='bold',
                             size=sizes)
                else:
                    ax1.text(i - len(str(round(v / 1000, 1)) + 'k') * sz,
                             v + 0.5,
                             str(round(v / 1000, 1)) + 'k',
                             color='black',
                             fontweight='bold',
                             size=sizes)
            plt.savefig(folder + 'moneyspent.png')
            plt.close()
        if k == 10:
            plt.figure(figsize=[19.2, 10.8])

            s = s.sort_values(by=(len(s) - 1), axis=1,
                              ascending=False)  # sort data
            s = s.iloc[:, range(0, y)]
            coloriar = []
            for nomej in s.columns:
                coloriar.append(nationColor[nomej])

            ax1 = s.loc[len(s) - 1].plot.bar(color=coloriar,
                                             alpha=alpha1,
                                             edgecolor='black')  # bar plt
            plt.grid(axis='y', alpha=alphagrid)

            plt.xticks(rotation=-90)

            plt.ylabel('max mp')
            somma = 0
            for a in s.loc[len(s) - 1]:  # somma ultima riga matrice
                somma = somma + a
            h = 0
            percentuali = []
            for ap in s.loc[len(s) - 1]:
                h += ((ap / somma) * 100)
                percentuali.append(h)

            balances = []
            q = f
            for l in percentuali:
                d = l - q
                balances.append(d)
                q += f
            j = max(balances)
            pvalue = (1 - ((j**2) / 2500)) * 100
            ax2 = ax1.twinx()
            ax2.spines['right'].set_position(('axes', 1.0))
            plt.ylim(0, 101)
            plt.plot(percentuali, marker='o', color='g')  # linea paretiana
            ax1.set_title('max manpower' + '       Balancing%=' +
                          str(round(pvalue)) + '%')
            plt.ylabel('% max mp on total')
            j = 0
            for i, v in enumerate(percentuali):  # testo su linea
                ax2.text(i - 0.10,
                         v + 1,
                         str(round(v)) + '%',
                         color='black',
                         fontweight='bold',
                         size=12)
            for i, v in enumerate(s.loc[len(s) - 1]):  # testo su barre
                if v >= 100000:
                    ax1.text(i - len(str(round(v / 1000000, 1)) + 'M') * sz,
                             v + 0.5,
                             str(round(v / 1000000, 1)) + 'M',
                             color='black',
                             fontweight='bold',
                             size=sizes)
                else:
                    ax1.text(i - len(str(round(v / 1000, 1)) + 'k') * sz,
                             v + 0.5,
                             str(round(v / 1000, 1)) + 'k',
                             color='black',
                             fontweight='bold',
                             size=sizes)
            plt.savefig(folder + 'max manpower.png')
            plt.close()
        if k == 11:
            plt.figure(figsize=[19.2, 10.8])

            s = s.sort_values(by=(len(s) - 1), axis=1,
                              ascending=False)  # sort data
            s = s.iloc[:, range(0, y)]
            coloriar = []
            for nomej in s.columns:
                coloriar.append(nationColor[nomej])

            ax1 = s.loc[len(s) - 1].plot.bar(color=coloriar,
                                             alpha=alpha1,
                                             edgecolor='black')  # bar plt
            plt.grid(axis='y', alpha=alphagrid)

            plt.xticks(rotation=-90)

            plt.ylabel('total navy')
            somma = 0
            for a in s.loc[len(s) - 1]:  # somma ultima riga matrice
                somma = somma + a
            h = 0
            percentuali = []
            for ap in s.loc[len(s) - 1]:
                h += ((ap / somma) * 100)
                percentuali.append(h)
            ax2 = ax1.twinx()
            ax2.spines['right'].set_position(('axes', 1.0))
            plt.ylim(0, 101)
            plt.plot(percentuali, marker='o', color='g')  # linea paretiana
            ax1.set_title('total navy')
            plt.ylabel('% total navy on total')
            j = 0
            for i, v in enumerate(percentuali):  # testo su linea
                ax2.text(i - 0.10,
                         v + 1,
                         str(round(v)) + '%',
                         color='black',
                         fontweight='bold',
                         size=sizes)
            for i, v in enumerate(s.loc[len(s) - 1]):  # testo su barre
                ax1.text(i - len(str(int(v))) * sz,
                         v + 0.5,
                         str(int(v)),
                         color='black',
                         fontweight='bold',
                         size=sizes)
            plt.savefig(folder + 'total navy.png')
            plt.close()
        if k == 13:
            try:
                plt.figure(figsize=[19.2, 10.8])

                s = s.sort_values(by=(len(s) - 1), axis=1,
                                  ascending=False)  # sort data
                s = s.iloc[:, range(0, y)]
                coloriar = []
                for nomej in s.columns:
                    coloriar.append(nationColor[nomej])

                ax1 = s.loc[len(s) - 1].plot.bar(color=coloriar,
                                                 alpha=alpha1,
                                                 edgecolor='black')  # bar plt
                plt.grid(axis='y', alpha=alphagrid)

                plt.xticks(rotation=-90)

                plt.ylabel('dev clicks')
                somma = 0
                for a in s.loc[len(s) - 1]:  # somma ultima riga matrice
                    somma = somma + a
                h = 0
                percentuali = []
                for ap in s.loc[len(s) - 1]:
                    h += ((ap / somma) * 100)
                    percentuali.append(h)
                ax2 = ax1.twinx()
                ax2.spines['right'].set_position(('axes', 1.0))
                plt.ylim(0, 101)
                plt.plot(percentuali, marker='o', color='g')  # linea paretiana
                ax1.set_title('total dev clicks')
                plt.ylabel('% dev clicks on the total')
                j = 0
                for i, v in enumerate(percentuali):  # testo su linea
                    ax2.text(i - 0.10,
                             v + 1,
                             str(round(v)) + '%',
                             color='black',
                             fontweight='bold',
                             size=sizes)
                for i, v in enumerate(s.loc[len(s) - 1]):  # testo su barre
                    ax1.text(i - len(str(int(v))) * sz,
                             v + 0.5,
                             str(int(v)),
                             color='black',
                             fontweight='bold',
                             size=sizes)
                plt.savefig(folder + 'dev clicks.png')
                plt.close()
            except:
                pass
        k += 1

    def boh(lista):
        a1 = []
        b1 = []
        c1 = []
        d1 = []
        for df in lista:
            i = 0
            tags1 = df['tag'].tolist()
            players1 = df['countryName'].tolist()
            for player in players1:
                if type(player) == type(0.54):
                    players1[i] = tags1[i]
                i += 1
            a = pd.DataFrame([df['incnosubs'].tolist()], columns=players1)
            b = pd.DataFrame([df['provinces'].tolist()], columns=players1)
            c = pd.DataFrame([df['totaldevelopment'].tolist()],
                             columns=players1)
            d = pd.DataFrame([df['maxmanpower'].tolist()], columns=players1)
            a1.append(a)
            b1.append(b)
            c1.append(c)
            d1.append(d)
        a2 = pd.concat(a1)
        b2 = pd.concat(b1)
        c2 = pd.concat(c1)
        d2 = pd.concat(d1)
        total = [a2, b2, c2, d2]
        return total

    h = boh(lista1)

    dev = allDataFrames[0]
    pro = allDataFrames[3]
    manpower = allDataFrames[10]
    income = allDataFrames[1]
    fdp = allDataFrames[12]
    plt.figure(figsize=[19.2, 10.8])
    fdpdev = [a * b for a, b in zip(dev.loc[0], fdp.loc[0])]
    dffdpdev = pd.DataFrame(np.array([fdpdev]), columns=players)
    dffdpdev = dffdpdev.append(fdp, ignore_index=True)
    dffdpdev = dffdpdev.sort_values(by=0, axis=1, ascending=False)
    dffdpdev = dffdpdev.iloc[:, range(0, y)]

    plt.figure(figsize=[19.2, 10.8])

    avgdev = [a / b for a, b in zip(dev.loc[0], pro.loc[0])]
    dfavgdev = pd.DataFrame(np.array([avgdev]), columns=players)
    dfavgdev = dfavgdev.sort_values(by=(len(dfavgdev) - 1),
                                    axis=1,
                                    ascending=False)
    dfavgdev = dfavgdev.iloc[:, range(0, y)]
    coloriar = []
    for nomej in dfavgdev.columns:
        coloriar.append(nationColor[nomej])
    ax1 = dfavgdev.loc[len(dfavgdev) - 1].plot.bar(
        color=coloriar, alpha=alpha1, edgecolor='black')  # bar plt
    plt.grid(axis='y', alpha=alphagrid)

    plt.xticks(rotation=-90)

    for i, v in enumerate(dfavgdev.loc[len(dfavgdev) - 1]):  # testo su barre
        ax1.text(i - len(str(round(v, 1))) * sz,
                 v + 0.005,
                 str(round(v, 1)),
                 color='black',
                 fontweight='bold',
                 size=sizes)
    plt.title('avg dev')
    plt.savefig(folder + 'avg dev.png')
    plt.close()
    plt.figure(figsize=[19.2, 10.8])

    avgmanpower = [(a - 10000) / b
                   for a, b in zip(manpower.loc[0], pro.loc[0])]
    dfavgmanpower = pd.DataFrame(np.array([avgmanpower]), columns=players)
    dfavgmanpower = dfavgmanpower.sort_values(by=(len(dfavgmanpower) - 1),
                                              axis=1,
                                              ascending=False)  #
    dfavgmanpower = dfavgmanpower.iloc[:, range(0, y)]
    coloriar = []
    for nomej in dfavgmanpower.columns:
        coloriar.append(nationColor[nomej])
    ax1 = dfavgmanpower.loc[len(dfavgmanpower) - 1].plot.bar(color=coloriar,
                                                             alpha=alpha1,
                                                             edgecolor='black')
    plt.grid(axis='y', alpha=alphagrid)

    plt.xticks(rotation=-90)

    for i, v in enumerate(dfavgmanpower.loc[len(dfavgmanpower) -
                                            1]):  # testo su barre
        ax1.text(i - len(str(round(v / 1000, 1)) + 'k') * sz,
                 v + 0.05,
                 str(round(v / 1000, 1)) + 'k',
                 color='black',
                 fontweight='bold',
                 size=sizes)
    plt.title('manpower per province')
    plt.savefig(folder + 'manpower per province.png')
    plt.close()
    plt.figure(figsize=[19.2, 10.8])
    avgincome = [(a - 2) / b for a, b in zip(income.loc[0], dev.loc[0])]
    dfavgincome = pd.DataFrame(np.array([avgincome]), columns=players)
    dfavgincome = dfavgincome.sort_values(by=(len(dfavgincome) - 1),
                                          axis=1,
                                          ascending=False)  #
    dfavgincome = dfavgincome.iloc[:, range(0, y)]
    coloriar = []
    for nomej in dfavgincome.columns:
        coloriar.append(nationColor[nomej])
    ax1 = dfavgincome.loc[len(dfavgincome) - 1].plot.bar(color=coloriar,
                                                         alpha=alpha1,
                                                         edgecolor='black')
    plt.grid(axis='y', alpha=alphagrid)

    plt.xticks(rotation=-90)

    for i, v in enumerate(dfavgincome.loc[len(dfavgincome) -
                                          1]):  # testo su barre
        ax1.text(i - len(str(round(v, 2))) * sz,
                 v,
                 str(round(v, 2)),
                 color='black',
                 fontweight='bold',
                 size=sizes)
    plt.title('income per dev(nation efficency)')
    plt.savefig(folder + 'income per dev(nation efficency).png')
    plt.close()

    # diff income %
    def differenza(playerincome, cosa):
        global y
        global alpha1
        global alphagrid

        plt.figure(figsize=[19.2, 10.8])
        diffincome = []
        diffincomeper = []
        diff = lambda x: round(x.iloc[0] - x.iloc[1], 2)
        diffper = lambda x: round(((x.iloc[0] / x.iloc[1]) * 100) - 100, 1)
        playerincome.loc[2] = playerincome.apply(diff)
        playerincome.loc[3] = playerincome.apply(diffper)
        playerincome.dropna(axis=1, inplace=True)
        dfdiffincome = pd.DataFrame(np.array(
            [playerincome.iloc[-1].tolist(), playerincome.iloc[-2].tolist()]),
                                    columns=playerincome.columns)
        dfdiffincome = dfdiffincome.sort_values(by=1, axis=1, ascending=False)
        if len(dfdiffincome.columns) <= y:
            y = len(dfdiffincome.columns)
        sz = adjustTextSpacingOfColumns(y)
        sizes = adjustTextSizeForColumns(y)
        dfdiffincomeper = pd.DataFrame(np.array(
            [playerincome.iloc[-1].tolist()]),
                                       columns=playerincome.columns)
        dfdiffincome = dfdiffincome.iloc[:, range(0, y)]
        coloriar = []
        for nomej in dfdiffincome.columns:
            coloriar.append(nationColor[nomej])
        dfdiffincomeper = dfdiffincomeper.iloc[:, range(0, y)]
        ax1 = dfdiffincome.iloc[-1].plot.bar(color=coloriar,
                                             alpha=alpha1,
                                             edgecolor='black')
        plt.grid(axis='y', alpha=alphagrid)
        plt.xticks(rotation=-90)
        plt.title(cosa + ' gained in this session')
        ax2 = ax1.twinx()
        ax2.spines['right'].set_position(('axes', 1.0))

        plt.ylim(-5, 321)
        for i, v in enumerate(dfdiffincome.iloc[0]):  # testo su linea
            if v > 0:
                ax2.text(i - len(str(round(v)) + '+%') * sz,
                         0.5,
                         '+' + str(round(v)) + '%',
                         color='black',
                         fontweight='bold',
                         size=sizes)
            else:
                try:
                    ax2.text(i - len(str(round(v)) + '%') * sz,
                             0.5,
                             str(round(v)) + '%',
                             color='black',
                             fontweight='bold',
                             size=sizes)
                except:
                    pass
        for i, v in enumerate(dfdiffincome.iloc[1]):  # testo su barre
            if v > 1000:
                ax1.text(i - len(str(round(v / 1000, 2)) + 'k') * sz,
                         v + 0.1,
                         str(round(v / 1000)) + 'k',
                         color='black',
                         fontweight='bold',
                         size=sizes)
            elif v < -1000:
                ax1.text(i - len(str(round(v / 1000, 2)) + 'k') * sz,
                         v + 0.1,
                         str(round(v / 1000)) + 'k',
                         color='black',
                         fontweight='bold',
                         size=sizes)
            else:
                ax1.text(i - len(str(int(v))) * sz,
                         v + 0.1,
                         str(round(v)),
                         color='black',
                         fontweight='bold',
                         size=sizes)

        plt.savefig(folder + '/#' + cosa + ' gained in this session')
        plt.close()

    if save2 != '':
        differenza(h[0], 'income')
        differenza(h[1], 'provinces')
        differenza(h[2], 'development')
        differenza(h[3], 'max manpower')
    xfiles = [
        'dev clicks', 'max manpower', 'Development', 'income', 'armies', 'avg dev',
        'Battle casualities', 'Buildings Value', 'provinces', 'total navy',
        'moneyspent', 'manpower per province', 'Mana spent on teching up',
        'Mana spent on devving', 'income per dev(nation efficency)'
    ]
    for jf in xfiles:
        png = jf + '.png'
        with open(png, 'rb') as f:
            picture = discord.File(f)

            await ctx.send(file=picture)

    print('check your graphs folder(Press ENTER to close)')
    await ctx.send('Spam limiter: 2 minutes in Cooldown')


#-----------------------------FUNCTIONS---------------------------------


#generates the URL for the skanderbeg request given conditions above
#TODO: add options for what graphs wanted in each request
def getUrl(saveID, iaID):
    return 'https://skanderbeg.pm/api.php?key=' + SKANDERBEG_API + '&scope=getCountryData&save=' + saveID + '&tag=IRE&value=inc_no_subs;total_development;buildings_value;provinces;total_army;qualityScore;total_mana_spent_on_deving;total_mana_on_teching_up;spent_total;fdp;total_mana_spent_on_deving;battleCasualties;max_manpower;continents;dev_clicks;total_navy;total_army;hex;player;countryName&' + iaID + '&format=json'


#Not used?
def a_su_b(dfa, dfb, nomicolumn):
    dfx = pd.DataFrame()
    i = 0
    length = len(nomicolumn)
    while i < length:
        z = nomicolumn[i]
        x = [a / b for a, b in zip(dfa[z], dfb[z])]
        dfx[z] = x
        i += 1
    return dfx


#TODO: Unknown what used for - calculate ranges between? for graphs
def adjustTextSpacingOfColumns(ncolumn):
    a = ((4 * ncolumn) + 45) / 2000
    return a


#TODO: Calculate column size?
def adjustTextSizeForColumns(ncolumn):
    size = ((1 / 5) * -ncolumn) + 14
    return size


#HumanValue checks if the person is a human or not
def humanvalue(dict, valueName, tags):
    j = valueName
    a = []
    for i in tags:
        x = dict[i]
        try:
            s = x[valueName]
            y = round(s, 2)
            a.append(y)
        except:
            pass
    return (a)


#Adds all rows together
def sumof(data):
    a = 0
    for row in data:
        a = a + row
    return a


#unused
def testosucolumn(columns, ncifre):
    return columns


#TODO: No longer used
def devonnprovince(data):
    x = [
        round(i / k, 1)
        for i, k in zip(data['realdevelopment'], data['provinces'])
    ]
    return x


#TODO
def func(pct, allvals):
    absolute = int(pct / 100. * np.sum(allvals))
    return "{:.1f}%\n{:d}".format(pct, absolute)


#
def transposeReplace(df):
    dft = df.T
    dict = dft.to_dict()
    for i in list(df.index.values):
        a = df['tag']
        y = a[i]
        dict[y] = dict.pop(i)
    return dict


#UNUSED
def human(df):
    Humanplayers = df.loc[(df['tag'] == 'TUR') | (df['tag'] == 'FRA') |
                          (df['tag'] == 'MOS') | (df['tag'] == 'CAS') |
                          (df['tag'] == 'ENG') | (df['tag'] == 'HAB') |
                          (df['tag'] == 'QOM') | (df['tag'] == 'PER') |
                          (df['tag'] == 'SWE') | (df['tag'] == 'BRA') |
                          (df['tag'] == 'HOL') | (df['tag'] == 'SWI') |
                          (df['tag'] == 'PAL')]
    return Humanplayers


#this is the main function to get all dataframes
def trial(listadf, tags, players):
    i = 0
    for df in listadf:
        # print("Dataframe in Trial, number ")
        # print(i)
        # print(": \n")
        # print(df)
        dict = transposeReplace(df)
        humandict = {item: dict.get(item) for item in tags}
        # print("humanDict")
        # print(humandict)
        playerdev = humanvalue(humandict, 'totaldevelopment', tags)
        playerincome = humanvalue(humandict, 'incnosubs', tags)
        playerbuildingsvalue = humanvalue(humandict, 'buildingsvalue', tags)
        playerprovinces = humanvalue(humandict, 'provinces', tags)
        playerbattlecasualites = humanvalue(humandict, 'battleCasualties',
                                            tags)
        playertotalarmy = humanvalue(humandict, 'totalarmy', tags)
        playerqualityscore = humanvalue(humandict, 'qualityScore', tags)
        playermanadev = humanvalue(humandict, 'totalmanaspentondeving', tags)
        playermanatech = humanvalue(humandict, 'totalmanaontechingup', tags)
        playermoneyspent = humanvalue(humandict, 'spenttotal', tags)
        playermaxmanpower = humanvalue(humandict, 'maxmanpower', tags)
        playertotalnavy = humanvalue(humandict, 'totalnavy', tags)
        playerfdp = humanvalue(humandict, 'fdp', tags)
        playerclick = humanvalue(humandict, 'devclicks', tags)

        #always true?
        if i == 0:
            a = [playerdev]
            b = [playerincome]
            c = [playerbuildingsvalue]
            d = [playerprovinces]
            e = [playerbattlecasualites]
            f = [playertotalarmy]
            g = [playerqualityscore]
            h = [playermanadev]
            ix = [playermanatech]
            l = [playermoneyspent]
            n = [playermaxmanpower]
            m = [playertotalnavy]
            o = [playerfdp]
            p = [playerclick]
            i += 1

        #never true?
        else:
            print("something unusual happened in trial")

            i += 1
            a.append(playerdev)
            b.append(playerincome)
            c.append(playerbuildingsvalue)
            d.append(playerprovinces)
            e.append(playerbattlecasualites)
            f.append(playertotalarmy)
            g.append(playerqualityscore)
            h.append(playermanadev)
            ix.append(playermanatech)
            l.append(playermoneyspent)
            n.append(playermaxmanpower)
            m.append(playertotalnavy)
            o.append(playerfdp)
            p.append(playerclick)

    #All of these individually are going to be a graph
    #TODO: should be separated into different funtions
    dfplayerdev = pd.DataFrame(a, columns=players)
    dfplayerincome = pd.DataFrame(b, columns=players)
    dfplayerbuildingsvalue = pd.DataFrame(c, columns=players)
    dfplayerprovinces = pd.DataFrame(d, columns=players)
    dfplayerbattlecasualites = pd.DataFrame(e, columns=players)
    dfplayertotalarmy = pd.DataFrame(f, columns=players)
    dfplayerqualityscore = pd.DataFrame(g, columns=players)
    dfplayermanadev = pd.DataFrame(h, columns=players)
    dfplayermanatech = pd.DataFrame(ix, columns=players)
    dfplayermoneyspent = pd.DataFrame(l, columns=players)
    dfplayermaxmanpower = pd.DataFrame(n, columns=players)
    dfplayertotalnavy = pd.DataFrame(m, columns=players)
    playerfdp = pd.DataFrame(o, columns=players)
    playerclick = pd.DataFrame(p, columns=players)

    everything = [
        dfplayerdev, dfplayerincome, dfplayerbuildingsvalue, dfplayerprovinces,
        dfplayerbattlecasualites, dfplayertotalarmy, dfplayerqualityscore,
        dfplayermanadev, dfplayermanatech, dfplayermoneyspent,
        dfplayermaxmanpower, dfplayertotalnavy, playerfdp, playerclick
    ]
    return everything


#-------------------------RUN BOT----------------------------

client.run(DISCORD_KEY)
