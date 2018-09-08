import csv
import teams_data
from modelattackdefense import ModelAttackDefense, draw_ps

def print_attack_or_defense_vector(vector):
    print('[')
    for row in vector:
        print('[{}], '.format(", ".join([str(x) for x in row])))
    print(']')

def load_history_data(from_year, to_year):
    # Load matches matches from files, and retain only some columns
    data = []
    for season in range(from_year, to_year):  # to_year is excluded (year is the start of the season)
        file = 'history_analysis/F' + str(season) + str(season + 1) + '.csv'
        with open(file, 'r', newline='') as csvfile:
            reader = csv.DictReader(csvfile, delimiter=',')
            for r in reader:
                if r['Div'] == '':  # jump over empty lines
                    continue
                row = {'Season': season }
                # FTR = Full time result (who wuins)
                for f in ['Date', 'Div', 'HomeTeam', 'AwayTeam', 'FTR']:
                    row[f] = r[f]
                # FTHG = Full time home goals  == nombre de buts marqués à domicile à la fin du temps réglementaire
                # FTAG = full time away goals
                for f in ['FTHG', 'FTAG']:
                    row[f] = int(r[f])
                for f in ['B365H', 'B365D', 'B365A', 'BSH', 'BSD', 'BSA', 'GBH', 'GBD', 'GBA']:
                    try:
                        o = float(r[f])
                        row[f] = o / (1 + o)  # Conversion from odd to probabilities
                        if o < 1.0:
                            print(row)
                    except:
                        r[f] = None
                        continue
                data.append(row)
    # Identify all the teams
    teams = set(r['HomeTeam'] for r in data) | set(r['AwayTeam'] for r in data)

    # Liste de tous les matchs (un match compte pour deux)
    match_list = [r['HomeTeam'] for r in data] + [r['AwayTeam'] for r in data]

    # Nombre de matchs joués par équipe
    teams_count = {t: match_list.count(t) for t in teams}
    total_match = len(match_list)

    # matches by seasons
    matches_by_seasons = {}
    for m in data:
        s = m['Season']
        if s not in matches_by_seasons:
            matches_by_seasons[s] = []
        matches_by_seasons[s].append(m)

    return data, matches_by_seasons, total_match, teams, teams_count

def teams_data_referential(matches):
    # Build teams matches referential
    teams = teams_data.teams_data()
    teams_invert = {r['N']: k for k, r in teams.items()}

    for season in range(2011, 2018):
        for t in teams:
            teams[t][season] = False

    for m in matches:
        for t in m['HomeTeam'], m['AwayTeam']:
            teams[t]['seasons'].add(m['Season'])
            teams[t][m['Season']] = True

    seasons = {}
    for t, r in teams.items():
        for s in r['seasons']:
            if s not in seasons:
                seasons[s] = set()
            seasons[s].add(t)

    return teams, teams_invert, seasons

def find_maximum_values(scores):
    max_1 = max(p for (i, j), p in scores.items() if i > j)
    max_n = max(p for (i, j), p in scores.items() if i == j)
    max_2 = max(p for (i, j), p in scores.items() if i < j)
    max_1_indexes = [(i ,j) for (i, j), p in scores.items() if i > j and p == max_1]
    max_n_indexes = [(i ,j) for (i, j), p in scores.items() if i == j and p == max_n]
    max_2_indexes = [(i ,j) for (i, j), p in scores.items() if i < j and p == max_2]
    return (max_1, max_n, max_2), (max_1_indexes, max_n_indexes, max_2_indexes)

def simulate_bet_over(from_year_load, to_year_load, from_year, to_year, proba_table_file, printing='N'):
    # Load matches matches
    matches, matches_by_seasons, matches_count, _, teams_match_count = load_history_data(from_year_load, to_year_load)

    # Load teams matches
    teams, teams_invert, seasons = teams_data_referential(matches)

    # initialisation du modèle
    model = ModelAttackDefense(n_teams=len(teams), options={'teams': teams_invert,
                                                            'proba_table_file': proba_table_file})
    if printing:
        model.print()

    '''
    l = 1000
    a = [draw_ps({1: 40, 0: 30, 2: 30}) for _ in range(l)]
    print(a.count(1) / l, a.count(0) / l, a.count(2) / l)
    '''
    # Score by season
    play_scores = {}

    # Compute several seasons
    for season in range(from_year, to_year):
        if printing:
            print()
            print("Start Season: {}".format(season))
        teams_of_the_season = {teams[t]['N'] for t in seasons[season]}
        if printing:
            model.print(teams_of_the_season)
        if printing:
            print()
        counter = 0
        play_score = 0
        play_score_prono = 0
        play_score_exact = 0
        for m in matches_by_seasons[season]:
            counter += 1
            # Récupère l'information
            home_team_number = teams[m['HomeTeam']]['N']
            away_team_number = teams[m['AwayTeam']]['N']
            s1 = m['FTHG']
            s2 = m['FTAG']
            if printing:
                print(counter, m)
                # Print team status before match
                model.print({home_team_number, away_team_number})

            # Play and see
            scores, p_1_n_2 = model.compute_outcome_probabilities(home_team_number, away_team_number, printing=False if printing is not 'V' else True)
            p_1, p_n, p_2 = p_1_n_2
            (max_1, max_n, max_2),(maxi_1, maxi_n, maxi_2) = find_maximum_values(scores)
            if printing:
                print("1/N/2 = {:^5.2f},{:^5.2f},{:^5.2f}".format(p_1 * 100, p_n * 100, p_2 * 100))
                print("Max 1/N/2 = {:^5.2f},{:^5.2f},{:^5.2f}".format(max_1 * 100, max_n * 100, max_2 * 100))
            '''
            p_m = max(p_1_n_2)
            bet_on = 1 if p_m == p_1 else (2 if p_m == p_2 else 0)
            '''
            p_m = max(3*p_1 + 2*max_1, 3*p_n + 2*max_n, 3*p_2 + 2*max_2)
            bet_on = 1 if p_m == (3*p_1 + 2*max_1) else (2 if p_m == (3*p_2 + 2*max_2) else 0)
            # bet_on = 1
            # bet_on = draw_ps({1: 46, 0: 27, 2: 27})
            if bet_on == 1:
                bet_s1, bet_s2 = maxi_1[0]
                # bet_s1, bet_s2 = 1, 0
            elif bet_on == 0:
                bet_s1, bet_s2 = maxi_n[0]
                # bet_s1, bet_s2 = 0, 0
            else:
                bet_s1, bet_s2 = maxi_2[0]
                # bet_s1, bet_s2 = 0, 1
            #bet_s1, bet_s2 = 1, 0
            '''
            # tirage aléatoire d'un score dans la matrice des scores
            bet_s1, bet_s2 = draw_ps(scores)
            bet_on = 1 if bet_s1 > bet_s2 else (2 if bet_s1 < bet_s2 else 0)
            '''

            if printing:
                print("Bet on : {}, Score: {}/{}".format(bet_on, bet_s1, bet_s2))
            # Tirage aléatoire
            #bet_on = draw_ps({1: p_1, 0: p_n, 2: p_2})
            #bet_on = draw_ps({1: 40, 0: 30, 2: 30})
            if bet_on == 1 and s1 > s2:
                play_score += 3
                play_score_prono += 3
                if bet_s1 == s1 and bet_s2 == s2:
                    play_score += 2
                    play_score_exact += 2
            elif bet_on == 2 and s1 < s2:
                play_score += 3
                play_score_prono += 3
                if bet_s1 == s1 and bet_s2 == s2:
                    play_score += 2
                    play_score_exact += 2
            elif bet_on == 0 and s1 == s2:
                play_score += 3
                play_score_prono += 3
                if bet_s1 == s1 and bet_s2 == s2:
                    play_score += 2
                    play_score_exact += 2
            if printing:
                print("Score total / moyen = {} / {:3.2f}".format(play_score, play_score / counter))
                print("Score prono / moyen = {} / {:3.2f}".format(play_score_prono, play_score_prono / counter))
                print("Score exact / moyen = {} / {:3.2f}".format(play_score_exact, play_score_exact / counter))

            # Account for the match
            model.account_for2(home_team_number, away_team_number, s1, s2)
            # Print team status after match
            if printing:
                model.print({home_team_number, away_team_number})

        if printing:
            print('End of season {}'.format(season))
            print("Score total / moyen = {} / {:3.2f}".format(play_score, play_score / counter))
            print("Score prono / moyen = {} / {:3.2f}".format(play_score_prono, play_score_prono / counter))
            print("Score exact / moyen = {} / {:3.2f}".format(play_score_exact, play_score_exact / counter))
        play_scores[season] = {
            'total': [play_score, play_score / counter],
            'prono': [play_score_prono, play_score_prono / counter],
            'exact': [play_score_exact, play_score_exact / counter]
        }
        if printing:
            model.print(teams_of_the_season)

    if printing:
        print('End of seasons')
        print("Attack")
        print_attack_or_defense_vector(model.attack_vector)
        print("Defense")
        print_attack_or_defense_vector(model.defense_vector)
        model.print()
    return  play_scores, model

# ===================================================================================
if __name__ == "__main__":
    play_scores, final_model = simulate_bet_over(2011, 2018, 2015, 2018, proba_table_file='data_built_m_20180813.csv', printing=False)

    #final_model.print()
    #print()

    for season, r in play_scores.items():
        print("Season {:^5} Total {:^5.0f} {:^5.3f} Prono {:^5.0f} {:^5.3f} Exact {:^5.0f} {:^5.3f} ".format(
            season, r['total'][0], r['total'][1], r['prono'][0], r['prono'][1], r['exact'][0], r['exact'][1]
        ))
