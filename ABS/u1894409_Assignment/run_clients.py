from multiprocessing import Process
from AuctionClientOG2 import AuctionClientOG2
from AuctionClientOG import AuctionClientOG
from AuctionClient_flatbot import AuctionClient_flatbot
from AuctionClient_Policy import AuctionClient_Policy
from AuctionClient_u1894409 import AuctionClient_u1894409
from AuctionServer import AuctionServer
import time

HOST = "localhost"
ports = 8440
numbidders = 12
neededtowin = 5
itemtypes = ['Picasso', 'Van_Gogh', 'Rembrandt', 'Da_Vinci']
# numitems = {'Picasso': 50, 'Van_Gogh' : 40, 'Rembrandt' : 30, 'Da_Vinci' : 10}
numitems = {}

auction_size = 200
budget = 1000
values = {'Picasso': 4, 'Van_Gogh': 6, 'Rembrandt': 8, 'Da_Vinci': 12}
announce_order = True
winner_pays = 0

args = (HOST, ports, numbidders, neededtowin, itemtypes, numitems,
        auction_size, budget, values, announce_order, winner_pays, )

verbose = False


def run_auction(host, ports, numbidders, neededtowin, itemtypes, numitems,
                auction_size, budget, values, announce_order, winner_pays):
    auctionroom = AuctionServer(host=host, ports=ports, numbidders=numbidders,
                                neededtowin=neededtowin, itemtypes=itemtypes, numitems=numitems,
                                auction_size=auction_size, budget=budget, values=values,
                                announce_order=announce_order, winner_pays=winner_pays)
    auctionroom.announce_auction()
    auctionroom.run_auction()


def run_client(port, bidderid, verbose):
    bidbot = AuctionClient_u1894409(port=port, mybidderid=bidderid, verbose=verbose)
    bidbot.play_auction()


def run_client_flatbot(port, bidderid, verbose):
    bidbot = AuctionClient_flatbot(port=port, mybidderid=bidderid, verbose=verbose)
    bidbot.play_auction()


def run_client_OG(port, bidderid, verbose):
    bidbot = AuctionClientOG(port=port, mybidderid=bidderid, verbose=verbose)
    bidbot.play_auction()


def run_client2(port, bidderid, verbose):
    bidbot = AuctionClientOG2(port=port, mybidderid=bidderid, verbose=verbose)
    bidbot.play_auction()


def run_client_policy(port, bidderid, verbose):
    bidbot = AuctionClient_Policy(port=port, mybidderid=bidderid, verbose=verbose)
    bidbot.play_auction()


if __name__ == '__main__':
    print("Starting AuctionServer")
    auctionserver = Process(target=run_auction, args=args)
    auctionserver.start()
    time.sleep(0.5)
    bidbots = []

    p = ports
    name = 'u1894409'
    print("Starting AuctionClient on port %d with name %s" % (p, name))
    b = Process(target=run_client, args=(p, name, verbose, ))
    bidbots.append(b)
    b.start()

    p = ports + 1
    name = 'FlatBot'
    print("Starting AuctionClient on port %d with name %s" % (p, name))
    b = Process(target=run_client_flatbot, args=(p, name, verbose, ))
    bidbots.append(b)
    b.start()

    p = ports + 2
    name = 'OG'
    print("Starting AuctionClient on port %d with name %s" % (p, name))
    b = Process(target=run_client_OG, args=(p, name, verbose, ))
    bidbots.append(b)
    b.start()

    p = ports + 3
    name = 'Policy'
    print("Starting AuctionClient on port %d with name %s" % (p, name))
    b = Process(target=run_client_policy, args=(p, name, verbose, ))
    bidbots.append(b)
    b.start()

    for i in range(numbidders-4):
        p = ports + i + 4

        name = "Test" + str(i+1)
        print("Starting AuctionClient on port %d with name %s" % (p, name))
        b = Process(target=run_client_OG, args=(p, name, verbose, ))
        bidbots.append(b)
        b.start()
        time.sleep(0.5)
