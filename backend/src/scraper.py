import pandas as pd
from scraper_helpers import canucks_win, home_game, fetch_table
from pathlib import Path

# This script fetches historical game data from https://www.naturalstattrick.com then processes it
# The site only lets you view 3 seasons at once, to simplify we can just look at 5 seasons individually to build our dataset
# pandas.read_html handles scrapes for a table and parses it into a DataFrame
# Assumes the games are sorted chronologically which is the default

season = '20252026'
team1_code = 'VAN'
team2_code = None

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)

df_raw = fetch_table(season, team1_code, team2_code)
print(df_raw)

df_eng = pd.DataFrame()

# Each column in Game column looks like: '2024-10-09 - Flames 6, Canucks 5'
# Subtracts consecutive datetimes creating a timedelta column to calculate the days between games feature
game_datetimes = pd.to_datetime(df_raw['Game'].map(lambda x: x.split(' - ')[0]))
df_eng['Days Since Last Game'] = (game_datetimes - game_datetimes.shift(1)).dt.days

# Add home game feature
df_eng['Home'] = df_raw['Game'].map(home_game, na_action='ignore')

# Add win/loss supervised learning label
df_eng['Win'] = df_raw['Game'].map(canucks_win, na_action='ignore')

# Rolling features
features = ['CF/60', 'CA/60', 'SF/60', 'SA/60', 'xGF/60', 'xGA/60', 'SCF/60', 'SCA/60', 'HDCA/60', 'HDSF/60']
window_size = 5
rolling_stats = df_raw[features].rolling(window=window_size).mean().shift(1)
rolling_stats = rolling_stats.rename(columns=lambda x: f'{x}_rolling')

df_eng = pd.concat(objs=[rolling_stats, df_eng], axis=1)

df_eng = df_eng.dropna()

print(df_eng)