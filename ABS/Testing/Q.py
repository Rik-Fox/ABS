import csv
import random
import pandas as pd


class learn(object):

    def __init__(self, Rate83, Rate90, Rate100, firstgamefreq,
                 secondgamefreq, round_const, agg_const):

        self.Rate83 = float(Rate83)
        self.Rate90 = float(Rate90)
        self.Rate100 = float(Rate100)

        cols_flat = ["rand_num", "Rate83", "Rate90", "Rate100"]
        flat_data = pd.read_csv("RL_data/Flat.csv", ';', names=cols_flat)
        self.flat_num = list(flat_data.rand_num)[-1]

        cols_win = ['Timestamp', 'N', 'Winner', 'Budget Left', 'Points', 'Paintings']
        filename = "exported_results"
        win_data = pd.read_csv("RL_data/"+filename+".csv", ';', names=cols_win)
        self.Winner = list(win_data.Winner)

        cols_my = ['Timestamp', 'N', 'Winner', 'Budget Left', 'Points', 'Paintings']
        filename = "individual_results"
        my_data = pd.read_csv("RL_data/"+filename+".csv", ';', names=cols_my)
        self.me = list(my_data.Winner)[-1]

        self.strat = [self.Rate83, self.Rate90, self.Rate100, int(firstgamefreq),
                      int(secondgamefreq), int(round_const), float(agg_const)]

        self.strat_v = list(pd.read_csv("RL_data/state_values.csv", ';').tail(1))
        self.strat_v[-1] = str(sum(float(n) for n in self.strat_v[0:-2]))

        self.epsilon = {"firstgamefreq": 0.05,
                        "secondgamefreq": 0.05, "round_const": 0.1, "agg_const": 0.2}
        cols_state = ["numberbidders", "wincondition",
                      "known", "winnerpays", "standings"]

        state_data = pd.read_csv("RL_data/state.csv", ';', names=cols_state)
        self.states_N = list(state_data.numberbidders)[-1]
        self.states_Game = [list(state_data.wincondition)[-1],
                            list(state_data.known)[-1], list(state_data.winnerpays)[-1]]
        self.standings = list(state_data.standings)

    def update_mixed(self):

        if self.flat_num >= float(self.Rate83) and self.Winner == self.me:
            self.strat['Rate83'] += 0.05
            self.strat['Rate90'] += 0.03
            self.strat['Rate100'] += 0.03
        elif self.flat_num >= float(self.Rate90) and self.Winner == self.me:
            self.strat['Rate83'] -= 0.02
            self.strat['Rate90'] += 0.03
            self.strat['Rate100'] += 0.01
        elif self.flat_num >= float(self.Rate100) and self.Winner == self.me:
            self.strat['Rate83'] -= 0.02
            self.strat['Rate90'] -= 0.04
            self.strat['Rate100'] += 0.01
        elif self.Winner == self.me:
            self.strat['Rate83'] -= 0.01
            self.strat['Rate90'] -= 0.02
            self.strat['Rate100'] -= 0.03

    def explore(self):

        if self.states_Game[0] == 5:

            if random.random() < self.epsilon['firstgamefreq']:
                if random.random() > 0.5 and self.strat[3] >= 0:
                    self.strat[3] -= 1
                elif random.random() < 0.5 and self.strat[3] <= 3:
                    self.strat[3] += 1

            if random.random() < self.epsilon['secondgamefreq']:
                if random.random() > 0.5 and self.strat[4] >= 0:
                    self.strat[4] -= 1
                elif random.random() < 0.5 and self.strat[4] <= 3:
                    self.strat[4] += 1

            if random.random() < self.epsilon['round_const']:
                if random.random() > 0.5 and self.strat[5] >= 3:
                    self.strat[5] -= 1
                elif random.random() < 0.5 and self.strat[5] <= 8:
                    self.strat[5] += 1
        else:

            if random.random() < self.epsilon['agg_const']:
                if random.random() > 0.5 and self.strat[6] >= 0:
                    self.strat[6] -= 0.05
                elif random.random() < 0.5 and self.strat[6] <= 0.5:
                    self.strat[6] += 0.05

    def strat_timeseries(self):
        append_to_csv(self.strat, "RL_data/exploit.csv")

    def Q(self):
        prob = self.Winner.count(self.me)/len(self.Winner)
        if self.Winner[-1] == self.me:
            self.strat_v[-2] = str(float(self.strat_v[-2])+100)
        for i in range(len(self.Winner)-1, 0, -1):
            if self.Winner[i] == self.me:
                self.strat_v[i] = str(float(self.strat_v[i]) + prob)
            else:
                self.strat_v[i] = str(float(self.strat_v[i]) + (1-prob)*-0.005)

        self.strat_v[-1] = str(sum(float(n) for n in self.strat_v[0:-2]))
        append_to_csv(self.strat_v, "RL_data/state_values.csv")

    def update(self):
        if self.states_Game[0] == 5:
            self.update_mixed()
        self.explore()
        self.Q()
        self.strat_timeseries()


def append_to_csv(csv_list, output_filename):
    with open(output_filename, 'a', newline='') as fp:
        a = csv.writer(fp, delimiter=';')
        data = [csv_list]
        a.writerows(data)
