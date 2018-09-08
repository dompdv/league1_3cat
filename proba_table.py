import numpy as np
import csv
from itertools import product

def proba_table2(NCAT, file=None, matrices=None):
    # construit la matrice de probabilités
    rp = np.zeros((NCAT, NCAT, NCAT, NCAT, 8, 8))
    if file is not None:
        with open(file, 'r', newline='') as csvfile:
            reader = csv.DictReader(csvfile, delimiter=',')
            for row in reader:
                if row['Aa'] == '':
                    continue
                Aa, Ad, Ba, Bd = int(row['Aa']), int(row['Ad']), int(row['Ba']), int(row['Bd'])
                s1, s2 = int(row['s1']), int(row['s2'])
                p = float(row['p'])
                rp[Aa, Ad, Ba, Bd, min(s1, 7), min(s2, 7)] += p
    elif matrices is not None:
        for Aa, Ad, Ba, Bd in product(range(NCAT), repeat=4):
            for s1, l in enumerate(matrices[(Aa, Ad, Ba, Bd)]['p']):
                for s2, p in enumerate(l):
                    rp[Aa, Ad, Ba, Bd, min(s1, 7), min(s2, 7)] += p

    # renormalisaton à cause du petit 0.0001
    for Aa, Ad, Ba, Bd in product(range(NCAT), repeat=4):
        rp[Aa, Ad, Ba, Bd, :, :] += 0.0001
        t = np.sum(rp[Aa, Ad, Ba, Bd, :, :])
        rp[Aa, Ad, Ba, Bd, :, :] /= t
    return rp

