import socket
import random
import csv
import math
import pandas as pd
import numpy as np


class AuctionClient(object):
    """A client for bidding with the AucionRoom"""

    def __init__(self, host="localhost", port=8020, mybidderid=None, verbose=False):
        self.verbose = verbose
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host, port))
        forbidden_chars = set(""" '".,;:{}[]()""")
        if mybidderid:
            if len(mybidderid) == 0 or any((c in forbidden_chars) for c in mybidderid):
                print("""mybidderid cannot contain spaces or any of the following: '".,;:{}[]()!""")
                raise ValueError
            self.mybidderid = mybidderid
        else:
            # this is the only thing that distinguishes the clients
            self.mybidderid = raw_input("Input team / player name : ").strip()
            while len(self.mybidderid) == 0 or any((c in forbidden_chars) for c in self.mybidderid):
                self.mybidderid = raw_input(
                    """You input an empty string or included a space  or one of these '".,;:{}[]() in your name which is not allowed (_ or / are all allowed)\n for example Emil_And_Nischal is okay\nInput team / player name: """).strip()
        self.sock.send(self.mybidderid.encode("utf-8"))

        data = self.sock.recv(5024).decode('utf_8')
        x = data.split(" ")
        if self.verbose:
            print("Have received response of %s" % ' '.join(x))
        if(x[0] != "Not" and len(data) != 0):
            self.numberbidders = int(x[0])
            if self.verbose:
                print("Number of bidders: %d" % self.numberbidders)
            self.numtypes = int(x[1])
            if self.verbose:
                print("Number of types: %d" % self.numtypes)
            self.numitems = int(x[2])
            if self.verbose:
                print("Items in auction: %d" % self.numitems)
            self.maxbudget = int(x[3])
            if self.verbose:
                print("Budget: %d" % self.maxbudget)
            self.neededtowin = int(x[4])
            if self.verbose:
                print("Needed to win: %d" % self.neededtowin)
            self.order_known = "True" == x[5]
            if self.verbose:
                print("Order known: %s" % self.order_known)
            self.auctionlist = []
            self.winnerpays = int(x[6])
            if self.verbose:
                print("Winner pays: %d" % self.winnerpays)
            self.values = {}
            self.artists = {}
            order_start = 7
            if self.neededtowin > 0:
                self.values = None
                for i in range(7, 7+(self.numtypes*2), 2):
                    self.artists[x[i]] = int(x[i+1])
                    order_start += 2
                if self.verbose:
                    print("Item types: %s" % str(self.artists))
            else:
                for i in range(7, 7+(self.numtypes*3), 3):
                    self.artists[x[i]] = int(x[i+1])
                    self.values[x[i]] = int(x[i+2])
                    order_start += 3
                if self.verbose:
                    print("Item types: %s" % str(self.artists))
                    print("Values: %s" % str(self.values))

            if self.order_known:
                for i in range(order_start, order_start+self.numitems):
                    self.auctionlist.append(x[i])
                if self.verbose:
                    print("Auction order: %s" % str(self.auctionlist))

        self.sock.send('connected '.encode("utf-8"))

        data = self.sock.recv(5024).decode('utf_8')
        x = data.split(" ")
        if x[0] != 'players':
            print("Did not receive list of players!")
            raise IOError
        if len(x) != self.numberbidders + 2:
            print("Length of list of players received does not match numberbidders!")
            raise IOError
        if self.verbose:
            print("List of players: %s" % str(' '.join(x[1:])))

        self.players = []

        for player in range(1, self.numberbidders + 1):
            self.players.append(x[player])

        self.sock.send('ready '.encode("utf-8"))

        self.standings = {name: {artist: 0 for artist in self.artists} for name in self.players}
        for name in self.players:
            self.standings[name]["money"] = self.maxbudget

###########################################################################
# MY ARTRIBUTES FROM RL ###################################################
###########################################################################

        rate_83, rate90, rate100 = 0.08, 0.134, 0.256      # interval spacing in lieu of distribution

        self.mix = [random.random(), rate_83, rate90, rate100]     # run lottery for mixed strat

        self.firstgamefreq = 3  # pick most frequent
        self.round_const = 7  # constant to multiply by numbidders setting future to analyse
        self.secondgamefreq = 2  # pick second most frequent
        self.agg_const = 0.185   # multiplicative constant that defines aggression level

        self.mean = np.zeros(200)  # empty array to save averages
        self.loss = 0       # count times lost to use with aggresion
###########################################################################
# MY ARTRIBUTES FROM RL ###################################################
###########################################################################

    def play_auction(self):
        winnerarray = []
        winneramount = []
        done = False
        while not done:
            data = self.sock.recv(5024).decode('utf_8')
            x = data.split(" ")
            if x[0] != "done":
                if x[0] == "selling":
                    currentitem = x[1]
                    if not self.order_known:
                        self.auctionlist.append(currentitem)
                    if self.verbose:
                        print("Item on sale is %s" % currentitem)
                    bid = self.determinebid(self.numberbidders, self.neededtowin, self.artists, self.values, len(
                        winnerarray), self.auctionlist, winnerarray, winneramount, self.mybidderid, self.players, self.standings, self.winnerpays)
                    if self.verbose:
                        print("Bidding: %d" % bid)
                    self.sock.send(str(bid).encode("utf-8"))
                    data = self.sock.recv(5024).decode('utf_8')
                    x = data.split(" ")
                    if x[0] == "draw":
                        winnerarray.append(None)
                        winneramount.append(0)
                    if x[0] == "winner":
                        winnerarray.append(x[1])
                        winneramount.append(int(x[3]))
                        self.standings[x[1]][currentitem] += 1
                        self.standings[x[1]]["money"] -= int(x[3])
            else:
                done = True
                if self.verbose:
                    if self.mybidderid in x[1:-1]:
                        print("I won! Hooray!")
                    else:
                        print("Well, better luck next time...")
        self.sock.close()

    def determinebid(self, numberbidders, wincondition, artists, values, rd, itemsinauction, winnerarray, winneramount, mybidderid, players, standings, winnerpays):
        '''You have all the variables and lists you could need in the arguments of the function,
        these will always be updated and relevant, so all you have to do is use them.
        Write code to make your bot do a lot of smart stuff to beat all the other bots. Good luck,
        and may the games begin!'''

        '''
        numberbidders is an integer displaying the amount of people playing the auction game.

        wincondition is an integer. A postiive integer means that whoever gets that amount of a single type
        of item wins, whilst 0 means each itemtype will have a value and the winner will be whoever accumulates the
        highest total value before all items are auctioned or everyone runs out of funds.

        artists will be a dict of the different item types as keys with the total number of that type on auction as elements.

        values will be a dict of the item types as keys and the type value if wincondition == 0. Else value == None.

        rd is the current round in 0 based indexing.

        itemsinauction is a list where at index "rd" the item in that round is being sold is displayed.
        Note that it will either be as long as the sum of all the number of the items (as in "artists")
        in which case the full auction order is pre-announced and known, or len(itemsinauction) == rd+1,
        in which case it only holds the past and current items, the next item to be auctioned is unknown.

        winnerarray is a list where at index "rd" the winner of the item sold in that round is displayed.

        winneramount is a list where at index "rd" the amount of money paid for the item sold in that round is displayed.

        example: I will now construct a sentence that would be correct if you substituted the outputs of the lists:
        In round 5 winnerarray[4] bought itemsinauction[4] for winneramount[4] pounds/dollars/money unit.

        mybidderid is your name: if you want to reference yourself use that.

        players is a list containing all the names of the current players.

        standings is a set of nested dictionaries (standings is a dictionary that for each person has another dictionary
        associated with them). standings[name][artist] will return how many paintings "artist" the player "name" currently has.
        standings[name]['money'] (remember quotes for string, important!) returns how much money the player "name" has left.

            standings[mybidderid] is the information about you.
            I.e., standings[mybidderid]['money'] is the budget you have left.

        winnerpays is an integer representing which bid the highest bidder pays. If 0, the highest bidder pays their own bid,
        but if 1, the highest bidder instead pays the second highest bid (and if 2 the third highest, ect....).
        Note though that if you win, you always pay at least 1 (even if the second-highest was 0).

        Don't change any of these values, or you might confuse your bot! Just use them to determine your bid.
        You can also access any of the object variables defined in the constructor (though again don't change these!),
        or declare your own to save state between determinebid calls if you so wish.

        determinebid should return your bid as an integer. Note that if it exceeds your current budget (standings[mybidderid]['money']),
        the auction server will simply set it to your current budget.

        Good luck!
        '''

        # Game 1: First to buy wincondition of any artist wins, highest bidder pays own bid, auction order known.
        if (wincondition > 0) and (winnerpays == 0) and self.order_known:
            return self.first_bidding_strategy(numberbidders, wincondition, artists, values, rd, itemsinauction, winnerarray, winneramount, mybidderid, players, standings, winnerpays)

        # Game 2: First to buy wincondition of any artist wins, highest bidder pays own bid, auction order not known.
        if (wincondition > 0) and (winnerpays == 0) and not self.order_known:
            return self.second_bidding_strategy(numberbidders, wincondition, artists, values, rd, itemsinauction, winnerarray, winneramount, mybidderid, players, standings, winnerpays)

        # Game 3: Highest total value wins, highest bidder pays own bid, auction order known.
        if (wincondition == 0) and (winnerpays == 0) and self.order_known:
            return self.third_bidding_strategy(numberbidders, wincondition, artists, values, rd, itemsinauction, winnerarray, winneramount, mybidderid, players, standings, winnerpays)

        # Game 4: Highest total value wins, highest bidder pays second highest bid, auction order known.
        if (wincondition == 0) and (winnerpays == 1) and self.order_known:
            return self.fourth_bidding_strategy(numberbidders, wincondition, artists, values, rd, itemsinauction, winnerarray, winneramount, mybidderid, players, standings, winnerpays)

        # Though you will only be assessed on these four cases, feel free to try your hand at others!

    def freq(self, first, known):

        if known is True:
            arts = {'Picasso': first.count('Picasso'),  # dict with freq in desired future
                    'Van_Gogh': first.count('Van_Gogh'),
                    'Rembrandt': first.count('Rembrandt'),
                    'Da_Vinci': first.count('Da_Vinci')}
            # print(sorted(arts.items(), key=lambda x: x[1]))

            # return desired freq artists
            return sorted(arts.items(), key=lambda x: x[1])[self.firstgamefreq][0]

        else:
            # return desired freq artists
            return sorted(first.items(), key=lambda item: (item[1], item[0]))[self.secondgamefreq][0]

    def first_bidding_strategy(self, numberbidders, wincondition, artists, values, rd, itemsinauction, winnerarray, winneramount, mybidderid, players, standings, winnerpays):
        """Game 1: First to buy wincondition of any artist wins, highest bidder pays own bid, auction order known."""
        known = True

        if float(self.mix[0]) < float(self.mix[1]):  # this if uses the right start from the mixrate
            if standings[mybidderid][itemsinauction[rd]] == 4:
                return int(standings[mybidderid]['money'])  # sting in the tail for FlatBot
            else:
                return 83
        elif float(self.mix[0]) < float(self.mix[2]):
            if standings[mybidderid][itemsinauction[rd]] == 4:
                return int(standings[mybidderid]['money'])
            else:
                return 90
        elif float(self.mix[0]) < float(self.mix[3]):
            if standings[mybidderid][itemsinauction[rd]] == 4:
                return int(standings[mybidderid]['money'])
            else:
                return 100
        else:

            expected_rounds = int(math.ceil(self.round_const*numberbidders))  # future considered

            if expected_rounds > 200:   # make sure it isn't over the max
                expected_rounds = 200

            # returns string of desired artist
            pick = self.freq(itemsinauction[0:expected_rounds], known)

            if itemsinauction[rd] == pick:  # only bid on desired
                return 200
            else:
                return 0

    def second_bidding_strategy(self, numberbidders, wincondition, artists, values, rd, itemsinauction, winnerarray, winneramount, mybidderid, players, standings, winnerpays):
        """Game 2: First to buy wincondition of any artist wins, highest bidder pays own bid, auction order not known."""
        known = False

        if float(self.mix[0]) < float(self.mix[1]):  # this if uses the right start from the mixrate
            if standings[mybidderid][itemsinauction[rd]] == 4:
                return int(standings[mybidderid]['money'])  # sting in the tail for FlatBot
            else:
                return 83
        elif float(self.mix[0]) < float(self.mix[2]):
            if standings[mybidderid][itemsinauction[rd]] == 4:
                return int(standings[mybidderid]['money'])
            else:
                return 90
        elif float(self.mix[0]) < float(self.mix[3]):
            if standings[mybidderid][itemsinauction[rd]] == 4:
                return int(standings[mybidderid]['money'])
            else:
                return 100
        else:
            pick = self.freq(artists, known)  # returns string of desired artist

            if itemsinauction[rd] == pick:  # only bid on desired
                return 200
            else:
                return 0


#####################################################################################

    def valuation(self, whats_left, values, budget, itemsinauction, winneramount, numbidders, rd):

        points_left = whats_left.count('Picasso')*4 + whats_left.count('Van_Gogh') * \
            6 + whats_left.count('Rembrandt')*8 + whats_left.count('Da_Vinci')*12

        if rd > 1 and points_left != 0:
            tot = [winneramount[i]/values[itemsinauction[i]]
                   for i in range(0, rd-1)]   # point per money calculation
            self.mean[rd-1] = sum(tot)/len(tot)  # average up to now
            self.mean[0] = sum(self.mean[1:rd])/rd  # running avg
            unit_value = budget/points_left
            plus_std = unit_value + \
                math.fabs(unit_value-self.mean[0]) + \
                np.std(self.mean[1:rd])*math.sqrt(rd)  # add on std dev
        elif points_left != 0:
            plus_std = budget/points_left     # use base value before have 2 data point for std dev

        elif points_left == 0:
            return budget

        value = plus_std*values[whats_left[0]]  # base value of item times NE value+stddev

        return math.ceil(value)

    def mult(self, mybidderid, winnerarray):

        if mybidderid in winnerarray and winnerarray[-1] == mybidderid:
            self.loss = math.floor(self.loss/2)  # drop aggression if winning
        else:
            self.loss += 1  # increase aggression if losing

        mult = 1
        for i in range(0, self.loss):  # compute multipler for aggression
            mult *= self.agg_const

        return mult

    def third_bidding_strategy(self, numberbidders, wincondition, artists, values, rd, itemsinauction, winnerarray, winneramount, mybidderid, players, standings, winnerpays):
        """Game 3: Highest total value wins, highest bidder pays own bid, auction order known."""

        value = self.valuation(itemsinauction[rd:-1],
                               values, standings[mybidderid]['money'], itemsinauction, winneramount, numberbidders, rd)  # return valuation +stdev
        mult = self.mult(mybidderid, winnerarray)  # return aggression multipler

        util = ((numberbidders-1)/numberbidders)*value*mult  # NE of valuation with aggression

        return math.ceil(util)

    def fourth_bidding_strategy(self, numberbidders, wincondition, artists, values, rd, itemsinauction, winnerarray, winneramount, mybidderid, players, standings, winnerpays):
        """Game 4: Highest total value wins, highest bidder pays second highest bid, auction order known."""

        value = self.valuation(itemsinauction[rd:-1],
                               values, standings[mybidderid]['money'], itemsinauction, winneramount, numberbidders, rd)  # return valuation +stdev
        mult = self.mult(mybidderid, winnerarray)  # return aggression multipler

        util = value*mult  # NE of valuation with aggression

        return math.ceil(util)