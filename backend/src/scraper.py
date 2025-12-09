import pandas as pd
from scraper_helpers import canucks_win, home_game, build_url

# This script fetches historical game data from https://www.naturalstattrick.com then processes it
# The site only lets you view 3 seasons at once, to simplify we can just look at 5 seasons individually to build our dataset
# pandas.read_html handles scrapes for a table and parses it into a DataFrame
# Assumes the games are sorted chronologically which is the default

season = '20252026'
team1_code = 'VAN'
team2_code = None

# read_html returns a list of DataFrames; get the first (and only) one
df = pd.read_html(build_url(season, team1_code), attrs={'id': 'teams'})[0] 

# Add win/loss supervised learning label
df['Win'] = df['Game'].map(canucks_win, na_action='ignore')

# Each column in Game column looks like: '2024-10-09 - Flames 6, Canucks 5'
# Subtracts consecutive datetimes creating a timedelta column to calculate the days between games feature
df['Game Date'] = pd.to_datetime(df['Game'].map(lambda x: x.split(' - ')[0]))
df['Days Since Last Game'] = (df['Game Date'] - df['Game Date'].shift(1)).dt.days

# Add home game feature
df['Home'] = df['Game'].map(home_game, na_action='ignore')

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
print(df.dtypes)
print(df)
df.to_csv(f"../data/{team1_code}_{season}.csv", index=False)

df.drop(columns=['Unnamed: 2', 'Team', 'Game',], inplace=True)