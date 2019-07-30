import time
import datetime
import os
from importlib import import_module
from multiprocessing import Process
import csv
from AuctionServer import AuctionServer

print("Finding bots . . . ")

live_bot_dir = os.getcwd() + "/LiveBots"
live_bot_folders = [f.path.split("/")[-1] for f in os.scandir(live_bot_dir) if f.is_dir()]
live_bot_folders_clean = [f for f in live_bot_folders if f != "__pycache__"]

numbidders = len(live_bot_folders_clean)
try:
    os.remove('Data/players.csv')
except:
    pass
with open("Data/players.csv", 'a', newline='') as fp:
    a = csv.writer(fp, delimiter=';')
    data = [live_bot_folders_clean]
    a.writerows(data)

print("{} bots found".format(numbidders))

print(live_bot_folders_clean)

HOST = "localhost"

# Bit hacky - just choose a random port number, unlikely to be a conflict
# ports = random.randint(10000,60000)
ports = (5000)
itemtypes = ['Picasso', 'Van_Gogh', 'Rembrandt', 'Da_Vinci']
# numitems = {'Picasso': 50, 'Van_Gogh' : 40, 'Rembrandt' : 30, 'Da_Vinci' : 10}
numitems = {}
auction_size = 200
budget = 1000
values = {'Picasso': 4, 'Van_Gogh': 6, 'Rembrandt': 8, 'Da_Vinci': 12}

verbose = False

game = 3
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


def ascii_intro():
    print("\nGET READY")
    time.sleep(1)
    print("\nFOR")
    time.sleep(1)

    import sys

    from colorama import init
    init(strip=not sys.stdout.isatty())  # strip colors if stdout is redirected
    from termcolor import cprint
    from pyfiglet import figlet_format

    cprint(figlet_format('BOT ARENA', font='starwars'),
           'yellow', 'on_red', attrs=['bold'])

    time.sleep(0.5)


print("\nGAME STYLE {} STARTING".format(game))

time.sleep(0.1)


# ascii_intro()

def run_auction(host, ports, numbidders, neededtowin, itemtypes, numitems, auction_size, budget, values, announce_order, winner_pays):

    auctionroom = AuctionServer(host=host, ports=ports, numbidders=numbidders, neededtowin=neededtowin,
                                itemtypes=itemtypes, numitems=numitems, auction_size=auction_size, budget=budget, values=values, announce_order=announce_order, winner_pays=winner_pays)
    auctionroom.announce_auction()
    auctionroom.run_auction()


def run_client(port, bidderid, verbose, ThisClient):
    bidbot = ThisClient(port=port, mybidderid=bidderid, verbose=verbose)
    bidbot.play_auction()


try:
    os.remove('Data/exported_results.csv')
except:
    pass

if __name__ == '__main__':
    itr = 500
    for i in range(0, itr):
        p = ports+i*10
        args = (HOST, p, numbidders, neededtowin, itemtypes, numitems,
                auction_size, budget, values, announce_order, winner_pays, )
        print("Starting AuctionServer - Iteration "+str(i)+" of "+str(itr))

        auctionserver = Process(target=run_auction, args=args)
        auctionserver.start()

        time.sleep(0.1)

        for bot_name in live_bot_folders_clean:
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

os.rename("Data/exported_results.csv", "Data/" +
          str(datetime.datetime.now().strftime("%Y-%m-%d_%H:%M"))+"_Game"+str(game)+"_Winner_Flat.csv")
# os.rename("Data/individual_results.csv", "Data/" +
#           str(datetime.datetime.now().strftime("%Y-%m-%d_%H:%M"))+"_Game"+str(game)+"_Me.csv")
