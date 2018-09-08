import teams_data
from modelattackdefense import ModelAttackDefense
import data_matches_2018
import numpy as np
import simul2018_data

def find_maximum_values(scores):
    max_1 = max(p for (i, j), p in scores.items() if i > j)
    max_n = max(p for (i, j), p in scores.items() if i == j)
    max_2 = max(p for (i, j), p in scores.items() if i < j)
    max_1_indexes = [(i ,j) for (i, j), p in scores.items() if i > j and p == max_1]
    max_n_indexes = [(i ,j) for (i, j), p in scores.items() if i == j and p == max_n]
    max_2_indexes = [(i ,j) for (i, j), p in scores.items() if i < j and p == max_2]
    return (max_1, max_n, max_2), (max_1_indexes, max_n_indexes, max_2_indexes)

def teams_data_referential():
    # Build teams matches referential
    teams = teams_data.teams_data()
    teams_invert = {r['N']: k for k, r in teams.items()}
    return teams, teams_invert

# Load teams matches
teams, teams_invert = teams_data_referential()
teams_of_the_season = {teams[t]['N'] for t in teams if 2018 in teams[t]['seasons']}

attack_vector, defense_vector = simul2018_data.attack_defense_vectors()

'''
Div = League Division
Date = Match Date (dd/mm/yy)
HomeTeam = Home Team
AwayTeam = Away Team
FTHG and HG = Full Time Home Team Goals
FTAG and AG = Full Time Away Team Goals
FTR and Res = Full Time Result (H=Home Win, D=Draw, A=Away Win)
'''
# Matches de la saison 2018
matches = data_matches_2018.calendar()

ncat = 8
# Initialisation du modèle
model = ModelAttackDefense(n_teams=len(teams),
                           n_levels=ncat,
                           options={
                               'teams': teams_invert,
                               'attack_vector': np.array(attack_vector),
                               'defense_vector': np.array(defense_vector),
                               'proba_table_file': 'data_built_m3_cat8.csv'})
model.print(teams_of_the_season)

matches = simul2018_data.account_for_2018_results(matches)
# Passer en revue les matchs passés et ajuster les probas
print("Ajustement sur les résultats des matchs passés")
last_day = 0
counter = 0
play_score = 0
play_score_prono = 0
play_score_exact = 0
for match in matches:
    if match['Played']:
        home_team_number, away_team_number = teams[match['HomeTeam']]['N'], teams[match['AwayTeam']]['N']
        s1, s2 = match['FTHG'], match['FTAG']
        print("Jour {} : {} / {} -> {}/{}".format(match['Date'], match['HomeTeam'], match['AwayTeam'], s1, s2))
        model.print(set([home_team_number, away_team_number]))
        model.account_for2(home_team_number, away_team_number, s1, s2)
        model.print(set([home_team_number, away_team_number]))
        last_day = match['Date']
        counter += 1
        if (s1 > s2 and match['Prono'] == 1) or (s1 == s2 and match['Prono'] == 0) or (s1 < s2 and match['Prono'] == 2):
            play_score += 3
            play_score_prono += 3
            if s1 == match['Exact_s1'] and s2 == match['Exact_s2']:
                play_score += 2
                play_score_exact += 2

model.print(teams_of_the_season)
print('Dernier jour joué:', last_day)
if counter > 0:
    print("Matchs joués: {}".format(counter))
    print("Score total / moyen = {} / {:3.2f}".format(play_score, play_score / counter))
    print("Score prono / moyen = {} / {:3.2f}".format(play_score_prono, play_score_prono / counter))
    print("Score exact / moyen = {} / {:3.2f}".format(play_score_exact, play_score_exact / counter))

# sur les matches futurs, mettre les pronostics (probas et scores,...)
print("Prochains matchs")
for match in matches:
    # Afficher les prochains matchs
    if not match['Played'] and match['Date'] <= last_day + 1:
        print("Jour {} {} ({}) contre {} ({})".format(match['Date'],
                                                      match['HomeTeam'],
                                                      teams[match['HomeTeam']]['Code'],
                                                      match['AwayTeam'],
                                                      teams[match['AwayTeam']]['Code'],
                                                      ))
        home_team_number, away_team_number = teams[match['HomeTeam']]['N'], teams[match['AwayTeam']]['N']
        scores, p_1_n_2 = model.compute_outcome_probabilities(home_team_number, away_team_number, printing=True)
        p_1, p_n, p_2 = p_1_n_2
        (max_1, max_n, max_2),(maxi_1, maxi_n, maxi_2) = find_maximum_values(scores)
        # print("1/N/2 = {:^5.2f},{:^5.2f},{:^5.2f}".format(p_1 * 100, p_n * 100, p_2 * 100))
        print("Max 1/N/2 = {:^5.2f},{:^5.2f},{:^5.2f}".format(max_1 * 100, max_n * 100, max_2 * 100))
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
        print("Bet on : {}, Score: {}/{}".format(bet_on, bet_s1, bet_s2))

