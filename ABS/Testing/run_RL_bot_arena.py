import time
import datetime
import os
import shutil
from importlib import import_module
from multiprocessing import Process
import csv
import random
import numpy as np
from AuctionServer import AuctionServer
from Q import learn
import pandas as pd

# DATA = ['RL_data/exported_results.csv', 'RL_data/individual_results.csv',
#         'RL_data/players.csv', 'RL_data/Flat.csv']
# for filenames in DATA:
#     open(filenames, 'a')

print("Finding bots . . . ")

live_bot_dir = os.getcwd() + "/LiveBots"
live_bot_folders = [f.path.split("/")[-1] for f in os.scandir(live_bot_dir) if f.is_dir()]
live_bot_folders_clean = [f for f in live_bot_folders if f != "__pycache__"]
live_bot_folders_clean = sorted(live_bot_folders_clean)[1:-1]

itr = 1000
for i in range(0, itr):

    if i > 0:
        cols = ["Rate83", "Rate90", "Rate100", "firstgamefreq",
                "secondgamefreq", "round_const", "agg_const"]
        strat = pd.read_csv("RL_data/exploit.csv", ';', names=cols)
        strat_ = learn(list(strat.Rate83)[-1], list(strat.Rate90)[-1], list(strat.Rate100)[-1], list(strat.firstgamefreq)
                       [-1], list(strat.secondgamefreq)[-1], list(strat.round_const)[-1], list(strat.agg_const)[-1])
        strat_.update()

    # DATA = ['RL_data/exported_results.csv', 'RL_data/individual_results.csv',
    #         'RL_data/players.csv']
    #
    # for filenames in DATA:
    #     try:
    #         os.remove(filenames)
    #     except FileNotFoundError:
    #         pass

    k = int(np.ceil(random.random()*(len(live_bot_folders_clean)-1)))
    bots = sorted(list(random.sample(live_bot_folders_clean, k)))
    bots.insert(0, 'A0Policy')

    for j in range(0, len(bots)-1):
        if bots[j] == bots[j+1]:
            try:
                os.mkdir("/home/rfox/Term2_MSc/ABS/Testing/LiveBots/"+bots[j] + "_1")
                shutil.copy("/home/rfox/Term2_MSc/ABS/Testing/LiveBots/" +
                            bots[j]+"/AuctionClient.py", "/home/rfox/Term2_MSc/ABS/Testing/LiveBots/"+bots[j]+"_1/AuctionClient.py")
            except FileExistsError:
                pass
            bots[j] = bots[j] + "_1"

    print(bots)
    numbidders = len(bots)

    with open("Data/players.csv", 'a', newline='') as fp:
        a = csv.writer(fp, delimiter=';')
        data = [bots]
        a.writerows(data)

    print("{} bots found".format(numbidders))

    HOST = "localhost"

    # Bit hacky - just choose a random port number, unlikely to be a conflict
    # ports = random.randint(10000,60000)
    ports = (7000)
    itemtypes = ['Picasso', 'Van_Gogh', 'Rembrandt', 'Da_Vinci']
    # numitems = {'Picasso': 50, 'Van_Gogh' : 40, 'Rembrandt' : 30, 'Da_Vinci' : 10}
    numitems = {}
    auction_size = 200
    budget = 1000
    values = {'Picasso': 4, 'Van_Gogh': 6, 'Rembrandt': 8, 'Da_Vinci': 12}

    verbose = False

    # pk = int(np.ceil(random.random()*4))

    game = 1  # pk
    if game == 1:
        neededtowin = 5
        winner_pays = 0
        announce_order = True
    if game == 2:
        neededtowin = 5
        winner_pays = 0
        announce_order = False
    if game == 3:
        neededtowin = 0
        winner_pays = 0
        announce_order = True
    if game == 4:
        neededtowin = 0
        winner_pays = 1
        announce_order = True

    args = (HOST, ports, numbidders, neededtowin, itemtypes, numitems,
            auction_size, budget, values, announce_order, winner_pays, )

    print("\nGAME STYLE {} STARTING".format(game))

    time.sleep(0.1)

    def run_auction(host, ports, numbidders, neededtowin, itemtypes, numitems, auction_size, budget, values, announce_order, winner_pays):

        auctionroom = AuctionServer(host=host, ports=ports, numbidders=numbidders, neededtowin=neededtowin,
                                    itemtypes=itemtypes, numitems=numitems, auction_size=auction_size, budget=budget, values=values, announce_order=announce_order, winner_pays=winner_pays)
        auctionroom.announce_auction()
        auctionroom.run_auction()

    def run_client(port, bidderid, verbose, ThisClient):
        bidbot = ThisClient(port=port, mybidderid=bidderid, verbose=verbose)
        bidbot.play_auction()

    if __name__ == '__main__':

        p = ports+i*10
        args = (HOST, p, numbidders, neededtowin, itemtypes, numitems,
                auction_size, budget, values, announce_order, winner_pays, )
        print("Starting AuctionServer - Iteration "+str(i)+" of "+str(itr))

        auctionserver = Process(target=run_auction, args=args)
        auctionserver.start()

        time.sleep(0.1)

        for bot_name in bots:
            name = bot_name
            # import_module('AuctionClient', 'test_bot_1')
            module_name = "LiveBots." + bot_name + ".AuctionClient"
            ac = import_module(module_name, __name__)
            b = Process(target=run_client, args=(p, name, verbose, ac.AuctionClient))
            b.start()
            p = p + 1
            time.sleep(0.2)
        # time.sleep(2)
        while auctionserver.is_alive() is True:
            time.sleep(0.1)
        b.terminate()
        auctionserver.terminate()

os.rename("RL_data/exported_results.csv", "RL_data/" +
          str(datetime.datetime.now().strftime("%Y-%m-%d_%H:%M"))+"_Game"+str(game)+"_Winner.csv")
os.rename("RL_data/individual_results.csv", "RL_data/" +
          str(datetime.datetime.now().strftime("%Y-%m-%d_%H:%M"))+"_Game"+str(game)+"_Me.csv")
