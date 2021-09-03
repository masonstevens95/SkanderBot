import matplotlib.pyplot as plt


def plotDev(s, sz, sizes, nationColor, f, folder, alpha1, alphagrid, y):

    plt.figure(figsize=[19.2, 10.8])
    s = s.sort_values(by=(len(s) - 1), axis=1, ascending=False)  # sort data

    s = s.iloc[:, range(0, y)]
    coloriar = []
    for nomej in s.columns:
        coloriar.append(nationColor[nomej])

    ax1 = s.loc[len(s) - 1].plot.bar(color=coloriar,
                                     alpha=alpha1,
                                     edgecolor='black')  # bar plt
    plt.grid(axis='y', alpha=alphagrid)

    plt.xticks(rotation=-90)
    plt.ylabel('Development')
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
    ax1.set_title('development' + '       Balancing%=' + str(round(pvalue)) +
                  '%')
    plt.ylabel('% of dev on total')

    j = 0
    for i, v in enumerate(percentuali):  # testo su linea
        ax2.text(i - 0.10,
                 v + 1,
                 str(round(v)) + '%',
                 color='black',
                 fontweight='bold',
                 size=sizes)
    for i, v in enumerate(s.loc[len(s) - 1]):  # testo su barre
        ax1.text(i - len(str(round(v, 1))) * sz,
                 v + 0.5,
                 str(round(v, 1)),
                 color='black',
                 fontweight='bold',
                 size=sizes)
    plt.savefig(folder + 'dev.png')
    plt.close()







