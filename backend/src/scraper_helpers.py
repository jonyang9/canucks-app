from pathlib import Path
import pandas as pd

# Helpers for scraper.py

# Useful data structures
# Note: - Arizona Coyotes transfered to the Utah HC/Mammoth
#       - Both Mammoth and Utah HC refer to the code 'UTA'
team_codes_dict = {
    'Ducks': 'ANA',
    'Coyotes': 'ARI',
    'Bruins': 'BOS',
    'Sabres': 'BUF',
    'Flames': 'CGY',
    'Hurricanes': 'CAR',
    'Blackhawks': 'CHI',
    'Avalanche': 'COL',
    'Blue Jackets': 'CBJ',
    'Stars': 'DAL',
    'Red Wings': 'DET',
    'Oilers': 'EDM',
    'Panthers': 'FLA',
    'Kings': 'L.A',
    'Wild': 'MIN',
    'Canadiens': 'MTL',
    'Predators': 'NSH',
    'Devils': 'N.J',
    'Islanders': 'NYI',
    'Rangers': 'NYR',
    'Senators': 'OTT',
    'Flyers': 'PHI',
    'Penguins': 'PIT',
    'Sharks': 'S.J',
    'Kraken': 'SEA',
    'Blues': 'STL',
    'Lightning': 'T.B',
    'Maple Leafs': 'TOR',
    'Canucks': 'VAN',
    'Golden Knights': 'VGK',
    'Capitals': 'WSH',
    'Jets': 'WPG',
    'Mammoth': 'UTA',
    'Utah HC': 'UTA'
}

team_codes = team_codes_dict.values()


def home_game(game_str):
    # Example of str: '2024-10-09 - Flames 6, Canucks 5'
    # returns 1 if the Canucks play at home
    # the site (and most other NHL sites) lists the home team as the second team
    score_str = game_str.split(' - ')[1].strip()
    team_scores = score_str.split(', ')
    return 1 if 'Canucks' in team_scores[1] else 0


def validate_season(season):
    # Effect: raises an error if season isn't a string with format: '20252026'
    if not isinstance(season, str):
        raise TypeError('Season must be a string')
    
    if len(season) != 8 or not season.isdigit():
        raise ValueError('Season is not the right format')
    
    first_year = int(season[:4])
    second_year = int(season[4:])
    if second_year - first_year != 1:
        raise ValueError('Season is not the right format')
    

def validate_team_code(team_code):
    # Effect: raises an error if team_code isn't a string and a valid NHL team code
    if not isinstance(team_code, str):
        raise TypeError('Team code must be a string')
    
    if team_code not in team_codes:
        raise ValueError("Team code is not a valid NHL team code")


def canucks_win(game_str):
    # Example of str: '2024-10-09 - Flames 6, Canucks 5'
    # returns 1 if the Canucks won
    # used to determine outcome of a game as the supervised learning label
    
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


def build_url(season, team_code):
    validate_season(season)
    validate_team_code(team_code)
    return f'https://www.naturalstattrick.com/games.php?fromseason={season}&thru_season={season}&stype=2&sit=5v5&loc=B&team={team_code}&team2=All&rate=y'

def build_csv_path(season, team_code):
    validate_season(season)
    validate_team_code(team_code)
    return f"../data/{team_code}_{season}.csv"


def fetch_table(season, team_code):
    # returns a dataframe fetched from disk or naturalstattrick site
    path = Path(build_csv_path(season, team_code))
    if path.exists():
        print('read from disk.')
        df = pd.read_csv(path)
    else:
        # read_html returns a list of DataFrames; get the first (and only) one
        df = pd.read_html(build_url(season, team_code), attrs={'id': 'teams'})[0]
        df.to_csv(path, index=False)

    return df

def game_to_opp_team_code(game_str):
    # Example of str: '2024-10-09 - Flames 6, Canucks 5' or '2024-10-09 - Blue Jackets 6, Canucks 5'
    score_str = game_str.split(' - ')[1].strip()
    team_scores = score_str.split(', ')
    if 'Canucks' in team_scores[0]:
        split = team_scores[1].split(' ')
        split.pop()
        opp_name = ' '.join(split)
        return team_codes_dict[opp_name]
    else:
        split = team_scores[0].split(' ')
        split.pop()
        opp_name = ' '.join(split)
        return team_codes_dict[opp_name]