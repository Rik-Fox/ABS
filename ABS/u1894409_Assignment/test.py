import numpy as np

winnerarray = ["u1894409" "a" "b" "u1894409" "c"]

list(filter(lambda x: x == "u1894409", winnerarray))

artists = {'Picasso': 40, 'Van_Gogh': 60, 'Rembrandt': 8, 'Da_Vinci': 12}

v = list(artists.values())
k = list(artists.keys())

sorted(artists.iteritems(), key=lambda (k, v): (v, k))

artists.values()
sorted(artists)
