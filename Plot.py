import matplotlib.pyplot as plt

"""
Plotting functions - Plot is the main class, all other classes inherit from it. 

TODO, say what each of the arguments mean
"""



class Plot:

    def __init__(self, dataframe, columnTextSpacing, columnTextSize, nationColor, inversePlayerCount, folder, alpha, alphaGrid, playerCount):
        self.dataframe = dataframe
        self.columnTextSpacing = columnTextSpacing
        self.columnTextSize = columnTextSize
        self.nationColor = nationColor
        self.inversePlayerCount = inversePlayerCount
        self.folder = folder
        self.alpha = alpha
        self.alphaGrid = alphaGrid
        self.playerCount = playerCount

    #Development, dev clicks, max mp, income, armies, total navy, battle casualties, provinces
    def plotWithLine(self, name = 'NameUndefined'):
        
        if(name != 'NameUndefined'):
            plt.figure(figsize=[19.2, 10.8])
            self.dataframe = self.dataframe.sort_values(by=(len(self.dataframe) - 1), axis=1, ascending=False)  # sort data

            self.dataframe = self.dataframe.iloc[:, range(0, self.playerCount)]
            coloriar = []
            for nomej in self.dataframe.columns:
                coloriar.append(self.nationColor[nomej])

            ax1 = self.dataframe.loc[len(self.dataframe) - 1].plot.bar(color=coloriar,
                                            alpha=self.alpha,
                                            edgecolor='black')  # bar plt
            plt.grid(axis='y', alpha=self.alphaGrid)

            plt.xticks(rotation=-90)
            plt.ylabel(name)
            somma = 0
            for a in self.dataframe.loc[len(self.dataframe) - 1]:  # somma ultima riga matrice
                somma = somma + a
            h = 0
            percentuali = []
            for ap in self.dataframe.loc[len(self.dataframe) - 1]:
                h += ((ap / somma) * 100)
                percentuali.append(h)
            balances = []
            q = self.inversePlayerCount
            for l in percentuali:
                d = l - q
                balances.append(d)
                q += self.inversePlayerCount
            j = max(balances)
            pvalue = (1 - ((j**2) / 2500)) * 100
            ax2 = ax1.twinx()
            ax2.spines['right'].set_position(('axes', 1.0))
            plt.ylim(0, 101)
            plt.plot(percentuali, marker='o', color='r')  # linea paretiana
            ax1.set_title(name + '       Balancing%=' + str(round(pvalue)) +
                        '%')
            plt.ylabel('% of dev on total')

            j = 0
            for i, v in enumerate(percentuali):  # testo su linea
                ax2.text(i - 0.10,
                        v + 1,
                        str(round(v)) + '%',
                        color='black',
                        fontweight='bold',
                        size=self.columnTextSize)
            for i, v in enumerate(self.dataframe.loc[len(self.dataframe) - 1]):  # testo su barre
                ax1.text(i - len(str(round(v, 1))) * self.columnTextSpacing,
                        v + 0.5,
                        str(round(v, 1)),
                        color='black',
                        fontweight='bold',
                        size=self.columnTextSize)
            plt.savefig(self.folder + name + '.png')
            plt.close()
        else:   
            raise ValueError('name for the plot is undefined...')

    def plotStandard(self, name = 'NameUndefined'):
        if(name != 'NameUndefined'):
            pass
        else:   
            raise ValueError('name for the plot is undefined...')

    def plotPieChart(self, name = 'NameUndefined'):
        if(name != 'NameUndefined'):
            pass
        else:   
            raise ValueError('name for the plot is undefined...')
    
class DevPlot(Plot):

    def plotDev(self):
        super().plotWithLine("Development")

class DevClicksPlot(Plot):

    def plotDevClicks(self):
        super().plotWithLine("Dev Clicks")
        
class MaxManpowerPlot(Plot):

    def plotMaxManpower(self):
        super().plotWithLine("Max Manpower")

class IncomePlot(Plot):

    def plotIncome(self):
        super().plotWithLine("Income")

class TotalArmyPlot(Plot):

    def plotTotalArmy(self):
        super().plotWithLine("Total Army")

class TotalNavyPlot(Plot):

    def plotTotalNavy(self):
        super().plotWithLine("Total Navy")
        
class TotalCasualtiesPlot(Plot):

    def plotTotalCasualties(self):
        super().plotWithLine("Total Casualties")

class ProvincesCountPlot(Plot):

    def plotProvincesCount(self):
        super().plotWithLine("Provinces Count")
        


#dataframe, text spacing of column, text size for column, nation color, 100/player count, folder, alpha, alpha grid, player count
# (s, sz, sizes, nationColor, f, folder, alpha1, alphagrid, y)