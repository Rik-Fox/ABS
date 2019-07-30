import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


cols = ['Timestamp', 'Win Condition', 'Winnerpays', 'Order Known',
        '# rounds', 'Budget', 'Number of Bidders', 'Winner', 'Game Type']

df = pd.read_csv("Data/2019-03-26 18:14Game1.csv", ';')
df = pd.DataFrame(df[df.columns[0:9]])
df.columns = cols
wins = list(df.Winner)
items = np.array(pd.unique(df.Winner))
len(items)
count = 0
wincounts = np.zeros(len(items))
wincounts
for item in items:
    wincounts[count] = wins.count(item)
    count += 1

items
wincounts
plt.bar(items, wincounts)
