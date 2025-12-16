import pandas as pd
from helpers import canucks_win, home_game, fetch_table, game_to_opp_team_code
from pathlib import Path

# This script fetches historical game data from https://www.naturalstattrick.com then processes it
# The site only lets you view 3 seasons at once, to simplify we can look at seasons individually to build our dataset
# Assumes the games are sorted chronologically which is the default

seasons = ['20242025', '20252026']
team_code = 'VAN'

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)

all_seasons = []

for season in seasons:
    df_raw = fetch_table(season, team_code)

    df_eng = pd.DataFrame()

    # Each column in Game column looks like: '2024-10-09 - Flames 6, Canucks 5'
    # Subtracts consecutive datetimes creating a timedelta column to calculate the days between games feature
    game_datetimes = pd.to_datetime(df_raw['Game'].map(lambda x: x.split(' - ')[0]))
    df_eng['Days Since Last Game'] = (game_datetimes - game_datetimes.shift(1)).dt.days

    # Add home game feature
    df_eng['Home'] = df_raw['Game'].map(home_game, na_action='ignore')

    # Add win/loss supervised learning label
    df_eng['Win'] = df_raw['Game'].map(canucks_win, na_action='ignore')

    # Compute rolling statistics for the Canucks
    features = ['CF/60', 'CA/60', 'SF/60', 'SA/60', 'xGF/60', 'xGA/60', 'SCF/60', 'SCA/60', 'HDCA/60', 'HDSF/60']
    window_size = 5
    rolling_stats = df_raw[features].rolling(window=window_size).mean().shift(1)
    rolling_stats = rolling_stats.rename(columns=lambda x: f'{x}_rolling')

    df_eng = pd.concat(objs=[rolling_stats, df_eng], axis=1)

    df_eng = df_eng.dropna()

    # For each game, fetch opponent stats and compute rolling statistics
    rows = []
    for index in df_eng.index:
        game_str = df_raw.loc[index, 'Game']
        team_code_opp = game_to_opp_team_code(game_str)
        df_raw_opp = fetch_table(season, team_code_opp)
        rolling_stats_opp = df_raw_opp[features].rolling(window=window_size).mean().shift(1)
        date_str = game_str.split(' - ')[0]
        mask = df_raw_opp.index[df_raw_opp['Game'].str.contains(date_str)]
        assert len(mask) == 1
        row = rolling_stats_opp.loc[mask]
        row = row.rename(columns=lambda x: f'{x}_rolling_opp')
        rows.append(row)

    df_eng_opp = pd.concat(rows, ignore_index=True)
    df_eng = df_eng.reset_index(drop=True)
    df_eng_combined = pd.concat(objs=[df_eng, df_eng_opp], axis=1)
    df_eng_combined = df_eng_combined.dropna()
    all_seasons.append(df_eng_combined)

df_eng_all_seasons = pd.concat(all_seasons, ignore_index=True)
df_eng_all_seasons = df_eng_all_seasons.round(3)
file_name = f'{seasons[0]}.csv' if len(seasons) == 1 else f'{seasons[0]}-to-{seasons[len(seasons) - 1]}.csv'
path = Path(__file__).resolve().parent.parent / 'data' / 'engineered' / file_name
path.parent.mkdir(parents=True, exist_ok=True)
df_eng_all_seasons.to_csv(path, index=False)