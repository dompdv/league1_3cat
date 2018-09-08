import csv
import itertools

# Load data from
def load_data_from_files(from_year, to_year):
    # Recupere les matches des dernières saisons
    matches = []
    for season in range(from_year, to_year):

        if __name__ == "__main__":
            file = 'F' + str(season) + str(season + 1) + '.csv'
        else:
            file = 'history_analysis/F' + str(season) + str(season + 1) + '.csv'
        with open(file, 'r', newline='') as csvfile:
            reader = csv.DictReader(csvfile, delimiter=',')
            for r in reader:
                if r['Div'] == '':
                    continue
                row = { 'Season': season }
                for f in ['Date', 'Div', 'HomeTeam', 'AwayTeam', 'FTR']:
                    row[f] = r[f]
                for f in ['FTHG', 'FTAG']:
                    row[f] = int(r[f])
                matches.append(row)

    # Trouve toutes les équipes
    teams = set(r['HomeTeam'] for r in matches) | set(r['AwayTeam'] for r in matches)
    # Liste complète des matches, chaque match apparaisant deux fois, une par équipe,
    # Determine le nombre de matches joués par équipe
    match_list = [r['HomeTeam'] for r in matches] + [r['AwayTeam'] for r in matches]
    teams_count = { t: match_list.count(t) for t in teams}
    total_match = len(match_list)
    # Plus petit et plus grand
    max_score = max(max(r['FTHG'], r['FTAG']) for r in matches)
    min_score = min(min(r['FTHG'], r['FTAG']) for r in matches)
    return matches, total_match, teams, teams_count, min_score, max_score

# Compute global sastistiques for the scores (% of 1/0, 3/2, etc)
def compute_global_scores(matches):
    # Premières statistiques des scores pour se faire une idée
    scores = {}  # différentie 0:1 et 1:0
    scores_ordered = {}  # cumule 0:1 et 1:0
    for r in matches:
        sc = (r['FTHG'], r['FTAG'])
        if r['FTHG'] <= r['FTAG']:
            sco = sc
        else:
            sco = (r['FTAG'], r['FTHG'])
        if sc in scores:
            scores[sc] += 1
        else:
            scores[sc] = 1
        if sco in scores_ordered:
            scores_ordered[sco] += 1
        else:
            scores_ordered[sco] = 1
    return scores, scores_ordered


# Affichage desc scores (matriciel)
def print_scores(scores, min_score, max_score):
    goals = sum(v for v in scores.values())
    print("   |", end='')
    [print("{:^7}|".format(i), end='') for i in range(min_score, max_score + 1)]
    print()
    for i in range(min_score, max_score + 1):
        print("{:^3}|".format(i), end='')
        for j in range(min_score, max_score + 1):
            if (i, j) in scores:
                print("{:^7.3f}|".format(100*scores[(i, j)] / goals), end='')
            else:
                print("       |", end='')
        print()

# Affichage desc scores (liste)
def print_scores_list(scores, min_score, max_score):
    goals = sum(v for v in scores.values())
    for i in range(min_score, max_score + 1):
        for j in range(min_score, max_score + 1):
            if (i, j) in scores:
                print("{:^3}|{:^3}|{:^5.1f}|".format(i, j, 100*scores[(i, j)] / goals))


## Va chercher à séparer les équipes en groupes de meilleurs attaquants et défenseur
def split_teams_into_groups(matches, teams, NCAT):

    # On crée le meilleur groupe à la main. De niveau NCAT-1
    best_group = set(["Lyon", "Monaco", "Paris SG"])
    best_group = set()
    adjusted_teams = teams - best_group


    # Les matchs joués par équipe
    played = {t : [] for t in adjusted_teams}
    for r in matches:
        if r['HomeTeam'] in adjusted_teams:
            played[r['HomeTeam']].append(r)
        if r['AwayTeam'] in adjusted_teams:
            played[r['AwayTeam']].append(r)
    # Goals matked and received per team
    goal_marked = {t:0 for t in adjusted_teams}
    goal_received = {t:0 for t in adjusted_teams}
    for r in matches:
        if r['HomeTeam'] in adjusted_teams:
            goal_marked[r['HomeTeam']] += r['FTHG']
            goal_received[r['HomeTeam']] += r['FTAG']
        if r['AwayTeam'] in adjusted_teams:
            goal_marked[r['AwayTeam']] += r['FTAG']
            goal_received[r['AwayTeam']] += r['FTHG']
    # Average using the number of matches playes by a team
    # Nombre de buts moyens données ou recus. Les équipes sont classées par ordre de force croissante
    for t in adjusted_teams:
        goal_marked[t] /= len(played[t])
        goal_received[t] /= len(played[t])

    goal_marked_ordered = sorted(goal_marked.items(), key=lambda x:x[1], reverse=False)
    goal_received_ordered = sorted(goal_received.items(), key=lambda x:x[1], reverse=True)
    #print(goal_marked_ordered)
    #print(goal_received_ordered)

    # La répartition par groupe se fait de telle sorte que le nombre de matchs joués par groupe soit équivalent
    # sinon, à cause du bas de tableau changeant, on a une mauvaise répartition

    # OLD : grpoupes de même taille
    #group_size_old = len(goal_marked_ordered) / NCAT
    #attack_group_old = {t: int(i / group_size_old) for i,(t,_) in enumerate(goal_marked_ordered)}
    #defense_group_old = {t: int(i / group_size_old) for i,(t,_) in enumerate(goal_received_ordered)}

    total_match = sum(len(played[t]) for t in adjusted_teams)
    group_size = total_match / (NCAT - (1 if len(best_group) > 0 else 0))  # car j'ai séparé le groupe de tête à la main
    goal_marked_match = [len(played[t]) for t,_ in goal_marked_ordered]
    goal_marked_match = list(itertools.accumulate(goal_marked_match))
    goal_marked_match = [int(g / group_size) for g in goal_marked_match]
    attack_group = {t: min(g, NCAT - 1 - (1 if len(best_group)> 0 else 0)) for (t,_), g in zip(goal_marked_ordered, goal_marked_match)}
    #print(attack_group)

    goal_received_match = [len(played[t]) for t,_ in goal_received_ordered]
    goal_received_match = list(itertools.accumulate(goal_received_match))
    goal_received_match = [ int(g / group_size) for g in goal_received_match]
    defense_group = {t: min(g, NCAT - 1 - (1 if len(best_group) > 0 else 0)) for (t,_), g in zip(goal_received_ordered, goal_received_match)}
    #print(defense_group)

    # ajout du groupe de tête
    for t in best_group:
        defense_group[t] = NCAT - 1
        attack_group[t] = NCAT - 1
    return attack_group, defense_group

def compute_base_statistics(matches, attack_group, defense_group, min_score, max_score, NCAT):
    # Regroupement des scores par classes d'attaque
    base_statistics = {}  # dictionnaire indexé par (Aa, Ad, Ba, Bd, s1, s2)
    base_2 = {}   # dictionnaire indexé par (Aa, Ad, Ba, Bd} = { 's': {(s1,s2):nbre de buts, 'p':(s1,s2):proba, 'l':# échantillons)

    # initialise base_2
    ra = range(NCAT)
    sca = range(min_score, max_score + 1)
    p_array = [[0 for _ in list(sca)] for _ in list(sca)]
    for Aa, Ad, Ba, Bd in itertools.product(ra, ra, ra, ra):
        base_2[(Aa, Ad, Ba, Bd)] = {'s': [[0 for _ in list(sca)] for _ in list(sca)], 'l': 0}

    for r in matches:
        Aa = attack_group[r['HomeTeam']]
        Ad = defense_group[r['HomeTeam']]
        Ba = attack_group[r['AwayTeam']]
        Bd = defense_group[r['AwayTeam']]
        s1 = r['FTHG']
        s2 = r['FTAG']
        k = (Aa, Ad, Ba, Bd, s1, s2)
        if k not in base_statistics:
            base_statistics[k] = 0
        base_statistics[k] += 1
        base_2[(Aa, Ad, Ba, Bd)]['l'] += 1
        base_2[(Aa, Ad, Ba, Bd)]['s'][s1][s2] += 1

    base_statistics = {k: v / len(matches) for k, v in base_statistics.items()}
    for Aa, Ad, Ba, Bd in itertools.product(ra, ra, ra, ra):
        n = base_2[(Aa, Ad, Ba, Bd)]['l']
        if n > 0:
            base_2[(Aa, Ad, Ba, Bd)]['p'] = [[base_2[(Aa, Ad, Ba, Bd)]['s'][i][j] / n for j in list(sca)] for i in list(sca)]

    return base_statistics, base_2


def print_base_statistics(stats):
    print()
    for (Aa, Ad, Ba, Bd, s1, s2), p in stats.items():
        print("{},{},{},{},{},{},{}".format(Aa, Ad, Ba, Bd, s1, s2, p))

# Affichage des base_statistics avec les deux vecteurs cumulés, en version matricielle
def print_base_statistics_array(stats, min_score, max_score, NCAT):
    ra = range(NCAT)
    sca = range(min_score, max_score + 1)
    data_length = []
    print("Stats")
    for Aa, Ad, Ba, Bd in itertools.product(ra, ra, ra, ra):
        print("Aa:{}, Ad:{}, Ba:{}, Bd:{}".format(Aa, Ad, Ba, Bd))
        extract = { (s1, s2): v for (Aa_, Ad_, Ba_, Bd_, s1, s2), v in stats.items() if Aa == Aa_ and Ad == Ad_ and Ba == Ba_ and Bd == Bd_ }
        if len(extract) > 10:
            print_scores(extract, min_score, max_score)
            data_length.append((Aa, Ad, Ba, Bd, len(extract)))
    return data_length

# Affichage des base_statistics avec les deux vecteurs cumulés
def print_base_statistics_vector(stats, min_score, max_score, NCAT):
    ra = range(NCAT)
    sca = range(min_score, max_score + 1)
    print("Stats vector")
    print("  Aa ,  Ad ,  Ba ,  Bd ,", end='')
    [print("A{}   ,".format(i), end='') for i in range(min_score, max_score + 1)]
    [print("D{}   ,".format(i), end='') for i in range(min_score, max_score + 1)]
    print("length")
    for Aa, Ad, Ba, Bd in itertools.product(ra, ra, ra, ra):
        print("{:^5},{:^5},{:^5},{:^5},".format(Aa, Ad, Ba, Bd), end='')
        extract = { (s1, s2): v for (Aa_, Ad_, Ba_, Bd_, s1, s2), v in stats.items() if Aa == Aa_ and Ad == Ad_ and Ba == Ba_ and Bd == Bd_ }
        # Total sur les buts marqués
        total = sum(v for v in extract.values())
        for i in list(sca):
            if total == 0:
                print("{:^5},".format(''), end='')
            else:
                print("{:^5.2f},".format(100 * sum(v for (s1, _),v in extract.items() if s1 == i) / total) , end='')
        for i in list(sca):
            if total == 0:
                print("{:^5},".format(''), end='')
            else:
                print("{:^5.2f},".format(100 * sum(v for (_, s2),v in extract.items() if s2 == i) / total), end='')
        print(len(extract))

# Construire des vecteurs (de probabilité de mettre des buts/ probabilités d'en encaisser
def build_vectors(base_statistics, base_2, min_score, max_score, NCAT):
    vectors = {}
    ra = range(NCAT)
    sca = range(min_score, max_score + 1)
    for Aa, Ad, Ba, Bd in itertools.product(ra, ra, ra, ra):
        extract = {(s1, s2): v for (Aa_, Ad_, Ba_, Bd_, s1, s2), v in base_statistics.items() if Aa == Aa_ and Ad == Ad_ and Ba == Ba_ and Bd == Bd_}
        total = sum(v for v in extract.values())
        bm = [100 * sum(v for (s1, _), v in extract.items() if s1 == i) / total if total > 0 else 0 for i in list(sca)]
        br = [100 * sum(v for (_, s2), v in extract.items() if s2 == i) / total if total > 0 else 0 for i in list(sca)]
        vectors[(Aa, Ad, Ba, Bd)] = {
            'bm':bm,  # vecteur de probabilité de buts marqués
            'br':br,  # vecteur de probabilité de buts reçus
            # 'l': len(extract)  # nombre d'échantillons (de valeurs non nulles dans la matrice de scores ??)
            'l': base_2[(Aa, Ad, Ba, Bd)]['l']  # nombre d'échantillons (de valeurs non nulles dans la matrice de scores ??)
        }
    return vectors

# distance entre deux Aa, Ad, Ba, Bd
def dist_v(a, b):
    Aa, Ad, Ba, Bd = a
    Aa_, Ad_, Ba_, Bd_ = b
    return abs(Aa - Aa_) + abs(Ad - Ad_) + abs(Ba - Ba_) + abs(Bd - Bd_)

# Construit les vecteurs manquants
def build_vectors_rebuilt(vectors, threshold_1, threshold_2):
    vectors_rebuilt = {}
    sub_vector = {k:r for k,r in vectors.items() if r['l'] > threshold_1}
    zeros = False
    for k, r in list(vectors.items()):
        if not zeros:
            zeros = [0.0 for _ in r['bm']]
        if r['l'] >= threshold_1:
            vectors_rebuilt[k]  = r
            continue
        # ordonne les vecteurs proches par distance croissante
        closest = sorted([(kc, rc['l'], dist_v(k, kc)) for kc, rc in vectors.items() if rc['l'] > 0], key=lambda x:x[2])
        closest_l = list(itertools.takewhile(lambda x: x < threshold_2, itertools.accumulate(l for _, l, _ in closest)))
        closest = closest[:len(closest_l) + 1]
        bm, br = zeros.copy(), zeros.copy()
        for kc, l, _ in closest:
            bm = [ x + l * y for x,y in zip(bm, vectors[kc]['bm'])]
            br = [ x + l * y for x,y in zip(br, vectors[kc]['br'])]
        t = sum(l for _, l ,_ in closest)
        bm = [ x / t for x in bm]
        br = [ x / t for x in br]
        vectors_rebuilt[k] =  {
            'bm': bm,
            'br': br,
            'l': t
        }
    return vectors_rebuilt

def print_vectors(vectors, min_score, max_score, NCAT):
    ra = range(NCAT)
    sca = range(min_score, max_score + 1)
    print("Stats vector")
    print("Aa,Ad,Ba,Bd,", end='')
    [print("A{},".format(i), end='') for i in range(min_score, max_score + 1)]
    [print("D{},".format(i), end='') for i in range(min_score, max_score + 1)]
    print("length")
    for Aa, Ad, Ba, Bd in itertools.product(ra, ra, ra, ra):
        print("{},{},{},{},".format(Aa, Ad, Ba, Bd), end='')
        r = vectors[(Aa, Ad, Ba, Bd)]
        for i in list(sca):
            print("{:^.4f},".format(r['bm'][i]) , end='')
        for i in list(sca):
            print("{:^.4f},".format(r['br'][i]) , end='')
        print(r['l'])

def significant_matrices(stats, min_score, max_score, threshold):
    flat = [(k, r['p'], r['l']) for k, r in stats.items() if r['l'] > 0]
    data_full = sorted([(k, p, l) for k, p, l in flat if l > 0], key=lambda x: x[2], reverse=True)
    data_full = list(itertools.takewhile(lambda x: x[2] > threshold, (x for x in data_full)))
    return data_full

def print_matrices(matrices):
    print("Aa,Ad,Ba,Bd,l,s1,s2,p")
    for (Aa, Ad, Ba, Bd), p, l in matrices:
        for s1, row in enumerate(p):
            for s2, p in enumerate(row):
                print("{},{},{},{},{},".format(Aa, Ad, Ba, Bd, l), end='')
                print("{},{},{}".format(s1, s2, p))

# Construit les vecteurs manquants
def build_matrices_rebuilt(stats, threshold_1, threshold_2):
    stats_rebuilt = {}
    flat = [(k, r['p'], r['l']) for k, r in stats.items() if r['l'] > 0]
    data_full = sorted([(k, p, l) for k, p, l in flat if l > 0], key=lambda x: x[2], reverse=True)
    for k, r in list(stats.items()):
        if r['l'] >= threshold_1:
            stats_rebuilt[k]  = r
            continue
        # ordonne les vecteurs proches par distance croissante
        closest = sorted([(kc, rc['l'], dist_v(k, kc)) for kc, rc in stats.items() if rc['l'] > 0], key=lambda x:x[2])
        closest_l = list(itertools.takewhile(lambda x: x < threshold_2, itertools.accumulate(l for _, l, _ in closest)))
        closest = closest[:len(closest_l) + 1]
        new_matrix = [[0 for _ in row] for row in r['s']]
        t = 0
        for kc, l, d in closest:
            f = l / (1+d)
            t += f
            new_matrix = [
                [x1 + f * y1 for x1, y1 in zip(x,y)] for x,y in zip(new_matrix, stats[kc]['p'])
            ]
        #t = sum(l for _, l ,_ in closest)
        new_matrix = [ [x1 / t for x1 in x] for x in new_matrix]
        stats_rebuilt[k] =  {
            'p': new_matrix,
            'l': sum(l for _, l ,_ in closest)
        }
    return stats_rebuilt

def print_rebuilt_matrices(matrices):
    print("Aa,Ad,Ba,Bd,l,s1,s2,p")
    for (Aa, Ad, Ba, Bd), r in matrices.items():
        p = r['p']
        l = r['l']
        for s1, row in enumerate(p):
            for s2, proba in enumerate(row):
                print("{},{},{},{},{},".format(Aa, Ad, Ba, Bd, l), end='')
                print("{},{},{}".format(s1, s2, proba))

# =================================================================================================
## Load data from files, identify teams and number of matches per team
def compute_rebuilt_matrices(from_year, to_year, proba_table_file, threshold_1, threshold_2, NCAT, printing=True):
    matches, total_match, teams, teams_count, min_score, max_score = load_data_from_files(from_year, to_year)

    '''
    ## Statistiques globales des scores
    scores, scores_ordered = compute_global_scores(matches)
    if printing:
        print_scores(scores, min_score, max_score)
        print()
        print_scores(scores_ordered, min_score, max_score)
        print()
    '''
    ## Séparer les équipes en groupes de meilleurs attaquants et défenseur
    attack_group, defense_group = split_teams_into_groups(matches, teams, NCAT)

    # Première approche : cumuler par Aa,Ad, Ba,Bd,s1,s2
    base_statistics, base_2 = compute_base_statistics(matches, attack_group, defense_group, min_score, max_score, NCAT)
    #print_base_statistics_vector(base_statistics, min_score, max_score, NCAT)

    # Construire des vecteurs (de probabilité de mettre des buts/ probabilités d'en encaisser
    #vectors = build_vectors(base_statistics, base_2, min_score, max_score, NCAT)
    #vectors_rebuilt = build_vectors_rebuilt(vectors, threshold_1, threshold_2, NCAT)
    #print_vectors(vectors_rebuilt, min_score, max_score, NCAT)

    ordered_matrices = significant_matrices(base_2, min_score, max_score, 20)
    rebuilt_matrices = build_matrices_rebuilt(base_2, threshold_1, threshold_2)
    if printing:
        print_rebuilt_matrices(rebuilt_matrices)
    if proba_table_file is not '':
        with open(proba_table_file, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, delimiter=',', fieldnames=['Aa', 'Ad', 'Ba', 'Bd', 'l', 's1', 's2', 'p'])
            writer.writeheader()
            for (Aa, Ad, Ba, Bd), r in rebuilt_matrices.items():
                p = r['p']
                l = r['l']
                for s1, row in enumerate(p):
                    for s2, p in enumerate(row):
                        w_r = {'Aa': Aa, 'Ad':Ad, 'Ba':Ba, 'Bd':Bd, 'l':l, 's1':s1, 's2':s2, 'p':p}
                        writer.writerow(w_r)
    return rebuilt_matrices


if __name__ == "__main__":
    compute_rebuilt_matrices(2010, 2018, 'data_built_m3_cat8_long.csv', threshold_1=1, threshold_2=1,NCAT=8, printing=False )