import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

cols = ['Timestamp', 'N', 'Winner', 'Budget Left', 'Points', 'Paintings']
file_name = "2019-03-30_14:25_Game1_Winner_Flat"
g = 4

wins = list(pd.read_csv("Data/"+file_name+".csv", ';', names=cols).Winner)
players = ["FlatBot090", ]

wincounts = [wins.count(item) for item in players]
wincounts
x = [str(players[i][7:10]) for i in range(0, len(players))]

plt.figure(figsize=(40, 25))
plt.bar(x, wincounts)
plt.title('N='+str(28) + ' for ' + str(len(wins)) +
          ' Games with Degenerate Players', fontsize=70)
plt.xlabel('Amount Bid', fontsize=50)
plt.ylabel('Number of Wins', fontsize=50)
plt.xticks(fontsize=30)
plt.yticks(fontsize=30)
plt.savefig("Plots/"+file_name+"_g"+str(g)+".png")
plt.close()

# wincounts_rev = [wincounts[-i] for i in range(1, len(wincounts)+1)]
wincounts_rev_norm = [count/len(wins) for count in wincounts]
round_density = [np.floor(np.sqrt((players.index(win)-len(players))**2)/g)+5 for win in wins]
# wincounts_rev_norm
# wincounts
count_data = np.linspace(int(np.min(round_density)), int(np.max(round_density)),
                         num=len(wincounts))
bin_data = np.linspace(int(np.min(round_density)), int(np.max(round_density)),
                       num=int(np.max(round_density)-np.min(round_density)+1))
kde_data = np.linspace(int(np.min(round_density)), int(np.max(round_density)),
                       num=int(np.max(round_density)-np.min(round_density)+1)*10)
vari = stats.variation(round_density)
stdi = np.std(round_density)
print(stdi, stdi**2, vari)
kde = stats.gaussian_kde(round_density)
normal = stats.gaussian_kde((np.random.randn(len(round_density)))+np.mean(round_density))
normal2 = stats.gaussian_kde((np.random.randn(len(round_density))
                              * g)+np.mean(round_density))

plt.figure(figsize=(40, 25))
plt.hist(round_density, bins=bin_data, density=True)
plt.title('N='+str(len(players)) + ' for ' + str(len(wins)) +
          ' Games with Degenerate Players', fontsize=70)
plt.xlabel('Mₑ of Winning Bidder', fontsize=50)
plt.ylabel('Normalised Win Proportion', fontsize=50)
plt.xticks(bin_data, fontsize=30)
plt.yticks(fontsize=30)
plt.savefig("Plots/"+file_name+"_Hist_g"+str(g)+".png")
