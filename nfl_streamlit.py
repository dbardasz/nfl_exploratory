import pandas as pd
import nfl_data_py as nfl
import numpy
import matplotlib.pyplot as plt
import streamlit as st
import altair as alt
import plotly.express as px


# pull 2022 nfl data
@st.cache_data
def get_data(year):
    return nfl.import_pbp_data([year], downcast=True, cache=False, alt_path=None)


df1 = get_data(2022)

# change play type for qb scramble because its considered a run, but it was a designed passing play
df1['play_type'] = df1.apply(lambda row: 'pass' if (row['qb_scramble'] == 1) else row['play_type'], axis=1)

# filter out plays that aren't passes or runs (kickoffs, punts, etc)
plays = df1.loc[(df1['play_type'] == 'run') | (df1['play_type'] == 'pass')]

# only regular season plays
regular_season = plays.loc[plays['season_type'] == 'REG']

# fill null values in downs to 2 point conversions
regular_season['down'] = regular_season['down'].fillna('2pt Conv')

# drop null values in offense formation - fakes or qb knees/spikes
regular_season = regular_season.loc[regular_season['offense_formation'].notnull()]


# function to create bins for yards to go for a first down
def downs_bin(row):
    if row['ydstogo'] <= 3:
        return 'Short (<=3)'
    elif 3 < row['ydstogo'] <= 8:
        return 'Medium (4-8)'
    elif 8 < row['ydstogo'] <= 12:
        return 'Long (9-12)'
    else:
        return 'Very Long (13+)'


# apply the function
# make sure ydstogo is float
regular_season['ydstogo'] = regular_season['ydstogo'].astype('float')
regular_season['downs_label'] = regular_season.apply(lambda row: downs_bin(row), axis=1)

# get only the columns we want for streamlit data
streamlit_data = regular_season[['home_team',
                                 'away_team',
                                 'season_type',
                                 'week',
                                 'posteam',
                                 'posteam_type',
                                 'defteam',
                                 'side_of_field',
                                 'yardline_100',
                                 'game_date',
                                 'quarter_seconds_remaining',
                                 'half_seconds_remaining',
                                 'game_seconds_remaining',
                                 'game_half',
                                 'quarter_end',
                                 'drive',
                                 'qtr',
                                 'down',
                                 'goal_to_go',
                                 'time',
                                 'yrdln',
                                 'ydstogo',
                                 'ydsnet',
                                 'play_type',
                                 'yards_gained',
                                 'shotgun',
                                 'no_huddle',
                                 'pass_length',
                                 'air_yards',
                                 'run_location',
                                 'run_gap',
                                 'posteam_timeouts_remaining',
                                 'defteam_timeouts_remaining',
                                 'fg_prob',
                                 'td_prob',
                                 'epa',
                                 'third_down_converted',
                                 'third_down_failed',
                                 'fourth_down_converted',
                                 'fourth_down_failed',
                                 'incomplete_pass',
                                 'interception',
                                 'safety',
                                 'tackled_for_loss',
                                 'qb_hit',
                                 'sack',
                                 'touchdown',
                                 'pass_touchdown',
                                 'rush_touchdown',
                                 'fumble',
                                 'complete_pass',
                                 'time_of_day',
                                 'stadium',
                                 'weather',
                                 'roof',
                                 'surface',
                                 'temp',
                                 'wind',
                                 'offense_formation',
                                 'offense_personnel',
                                 'defenders_in_box',
                                 'defense_personnel',
                                 'number_of_pass_rushers',
                                 'downs_label']]

streamlit_data['play_count'] = 1

# work on streamlit markdown and graphs
st.title('NFL Next Gen Stats')

st.header('NFL Play by Play Data')
st.subheader('Run vs Pass Plays')

st.write('NFL Teams Play Mix')

# get unique teams for filter
team_options = streamlit_data['posteam'].unique()
team_options.sort()

# get unique quarters for filter
qtr_options = streamlit_data['qtr'].unique()
qtr_options.sort()

# get unique downs for filter
down_options = streamlit_data['down'].unique()

# get unique distance to go filters
distancetogo_options = streamlit_data['downs_label'].unique()
distancetogo_options.sort()


# create multiselects, defaults to all options
teams = st.multiselect('Team(s)', team_options, default=team_options, key=1)
qtr = st.slider('Quarter', min_value=1, max_value=5, value=(1, 5), key=2)
down = st.multiselect('Down', down_options, default=down_options, key=3)
togo = st.multiselect('Distance to Go', distancetogo_options, default=distancetogo_options, key=4)

# filter dataframe to selected options
filtered_df = streamlit_data.loc[(streamlit_data['posteam'].isin(teams)) &
                                 (list(qtr)[0] <= streamlit_data['qtr']) &
                                 (streamlit_data['qtr'] <= list(qtr)[-1]) &
                                 (streamlit_data['down'].isin(down)) &
                                 (streamlit_data['downs_label'].isin(togo))]

# group dataframe based on team and play type
grouped = filtered_df.groupby(['posteam', 'play_type'])['posteam'].count()
grouped = grouped.unstack()
grouped = grouped.reset_index()

# create a button that generates scatterplot after selections are made
if st.button('Press to Generate Scatterplot'):
    fig = px.scatter(grouped, x='pass', y='run', text='posteam')

    fig.update_traces(textposition='top center')

    fig.update_layout(title_text='2022 Run/Pass Mix by Team')

    st.plotly_chart(fig, use_container_width=True)
else:
    st.write('Please make your selections to generate the plot')

st.divider()

# new plot play types by down
st.subheader('NFL Play Types by Down')

# get unique teams for filter
team_options = streamlit_data['posteam'].unique()
team_options.sort()

# get unique quarters for filter
qtr_options = streamlit_data['qtr'].unique()
qtr_options.sort()

# get unique distance to go filter
distancetogo_options = streamlit_data['downs_label'].unique()
distancetogo_options.sort()

# get unique formation for filter
formation_options = streamlit_data['offense_formation'].unique()

# get filter if team is home or away
posteamtype_options = streamlit_data['posteam_type'].unique()

# create  new multiselects, defaults to all options
down_teams = st.multiselect('Select Team(s)', team_options, default=team_options, key=5)
down_qtr = st.slider('Select Quarter', min_value=1, max_value=5, value=(1, 5), key=6)
down_togo = st.multiselect('Select Distance to Go', distancetogo_options, default=distancetogo_options, key=7)
formation = st.multiselect('Select Formation', formation_options, default=formation_options, key=8)
homeaway = st.multiselect('Select Home/Away Team', posteamtype_options, default=posteamtype_options, key=9)

# filter dataframe to selected options
filtered_downs = streamlit_data.loc[(streamlit_data['posteam'].isin(down_teams)) &
                                    (list(down_qtr)[0] <= streamlit_data['qtr']) &
                                    (streamlit_data['qtr'] <= list(down_qtr)[-1]) &
                                    (streamlit_data['downs_label'].isin(down_togo)) &
                                    (streamlit_data['offense_formation'].isin(formation)) &
                                    (streamlit_data['posteam_type'].isin(homeaway))]


if st.button('Click to Generate Bar Chart'):
    fig = px.bar(filtered_downs, x='down', y='play_count',
                 color='play_type', barmode='group')
    st.plotly_chart(fig, use_container_width=True)
    # fig, ax = plt.subplots()
    #
    # down_grouped.plot('down', ['pass', 'run'], kind='bar', ax=ax)
    # plt.title('2022 NFL Play Types by Down')
    #
    # st.pyplot(fig)
else:
    st.write('Please make your selections to generate the plot')

st.divider()

# new plot play types by down
st.subheader('NFL Play Types by Quarter')

# get unique distance to go filter
distancetogo_options = streamlit_data['downs_label'].unique()
distancetogo_options.sort()

# get unique formation for filter
formation_options = streamlit_data['offense_formation'].unique()

# get filter if team is home or away
posteamtype_options = streamlit_data['posteam_type'].unique()

# create  new multiselects, defaults to all options
qtr_teams = st.multiselect('Select Team(s)', team_options, default=team_options, key=10)
qtr_down = st.multiselect('Select Down', down_options, default=down_options, key=11)
qtr_togo = st.multiselect('Select Distance to Go', distancetogo_options, default=distancetogo_options, key=12)
qtr_formation = st.multiselect('Select Formation', formation_options, default=formation_options, key=13)
qtr_homeaway = st.multiselect('Select Home/Away Team', posteamtype_options, default=posteamtype_options, key=14)

# filter dataframe to selected options
filtered_qtr = streamlit_data.loc[(streamlit_data['posteam'].isin(qtr_teams)) &
                                    (streamlit_data['downs_label'].isin(qtr_togo)) &
                                    (streamlit_data['down'].isin(qtr_down)) &
                                    (streamlit_data['offense_formation'].isin(qtr_formation)) &
                                    (streamlit_data['posteam_type'].isin(qtr_homeaway))]


if st.button('Click to Generate Bar Chart', key=15):
    fig = px.bar(filtered_qtr, x='qtr', y='play_count',
                 color='play_type', barmode='group')
    st.plotly_chart(fig, use_container_width=True)
    # fig, ax = plt.subplots()
    #
    # down_grouped.plot('down', ['pass', 'run'], kind='bar', ax=ax)
    # plt.title('2022 NFL Play Types by Down')
    #
    # st.pyplot(fig)
else:
    st.write('Please make your selections to generate the plot')

st.divider()