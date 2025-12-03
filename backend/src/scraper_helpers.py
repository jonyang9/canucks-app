# Helpers for scraper.py

def canucks_win(game_str):
    # Example of str: '2024-10-09 - Flames 6, Canucks 5',
    # returns true if the Canucks won
    # used to determine outcome of a game for supervised learning label
    
    score_str = game_str.split(' - ')[1].strip()
    team_scores = score_str.split(', ')
    if 'Canucks' in team_scores[0]:
        canucks_goals = team_scores[0].split(' ')[1]
        opp_goals_arr = team_scores[1].split(' ')
        opp_goals = opp_goals_arr[len(opp_goals_arr) - 1]
    else:
        canucks_goals = team_scores[1].split(' ')[1]
        opp_goals_arr = team_scores[0].split(' ')
        opp_goals = opp_goals_arr[len(opp_goals_arr) - 1]

    canucks_goals = int(canucks_goals)
    opp_goals = int(opp_goals)

    return 1 if canucks_goals > opp_goals else 0