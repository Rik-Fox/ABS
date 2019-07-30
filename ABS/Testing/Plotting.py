import matplotlib.pyplot as plt
import pandas as pd


df = pd.read_csv("RL_data/state_values_Game1.csv", ';')
df.rename(columns={'0.200': 't'}, inplace=True)
ts = list(df.t)
ts

plt.figure(figsize=(40, 25))
plt.plot(ts)
plt.title("Value for Money Throughout an Auction (10 Realizations)", fontsize=70)
plt.xlabel('Round', fontsize=50)
plt.ylabel('Money Per Point', fontsize=50)
plt.xticks(fontsize=30)
plt.yticks(fontsize=30)
plt.savefig("converge1.png")
