import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

st.header('EDA on IPL dataset')
ipl = pd.read_csv('ipl_ball_by_ball_2.csv')
matches = pd.read_csv('matches4.csv')

st.set_page_config(page_title="IPL Data Dashboard", page_icon="🏏", layout="wide")

st.title("🏏 IPL Historical Data Dashboard")
st.markdown("A quick overview of all-time Indian Premier League statistics.")

total_seasons_of_ipl = matches['season_id'].nunique()
total_matches_played_in_ipl = matches['match_id'].size
total_runs_in_ipl = ipl['total_runs'].sum()
total_wickets_in_ipl = ipl['is_wicket'].sum()

st.header("Overall Tournament Stats")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(label="Total Seasons", value=total_seasons_of_ipl)
with col2:
    st.metric(label="Matches Played", value=total_matches_played_in_ipl)
with col3:
    st.metric(label="Total Runs", value=f"{total_runs_in_ipl:,}")
with col4:
    st.metric(label="Total Wickets", value=f"{total_wickets_in_ipl:,}")

st.divider()

st.header("Boundary Analysis")
st.subheader("Total Sixes Hit per Season")

sixes_in_each_season = ipl[ipl['batter_runs'] == 6].groupby('season_id').size().rename('sixes')

chart_col, data_col = st.columns([3, 1])

with chart_col:

    st.bar_chart(sixes_in_each_season, color="#FF4B4B")

with data_col:

    st.dataframe(sixes_in_each_season, use_container_width=True)


st.subheader("Season VS Total matches played")

no_of_matches_in_each_season = matches.groupby('season_id')['match_id'].count().reset_index()

fig = px.line(
    no_of_matches_in_each_season,
    x='season_id',
    y='match_id',
    labels={'season_id':'season', 'match_id':'matches'},
    title='Season VS Total matches played',
    markers=True
)

st.plotly_chart(fig, use_container_width=True)


st.subheader("Team Performance")

team_wins = matches['match_winner'].value_counts().reset_index()

fig = px.bar(
    team_wins,
    x='match_winner',
    y='count',
    labels={'count': 'matches won', 'match_winner': 'team'},
    title='Team vs Matches Won'
)

st.plotly_chart(fig, use_container_width=True)


st.subheader("Toss Decision Timeline")

a = matches.groupby(['season_id','toss_decision']).size().rename('count').reset_index()
a['percentage'] = a.groupby('season_id')['count'].transform(lambda x: (x / x.sum()) * 100)

fig = px.area(
    a,
    x="season_id",
    y="percentage",
    color="toss_decision",
    color_discrete_map={'field': '#1f77b4', 'bat': '#d62728'},
    markers=True,
    title="Toss Decision Timeline: Evolution of Field vs. Bat Strategy",
    labels={
        "season_id": "Match Year",
        "percentage": "Share of Decisions (%)",
        "toss_decision": "Decision"
    }
)

st.plotly_chart(fig, use_container_width=True)

st.subheader("Toss Win = Match Win?")

b = matches[['toss_winner', 'match_winner']].copy()
b['toss_win_equal_match_win'] = b['toss_winner'] == b['match_winner']
c = b['toss_win_equal_match_win'].value_counts() / b.shape[0] * 100
d = c.reset_index()

fig = px.pie(
    d,
    names='toss_win_equal_match_win',
    values='count',
    hole=0.5,
    title='Toss Win = Match Win? Correlation Analysis'
)

st.plotly_chart(fig, use_container_width=True)

st.subheader("Top 15 players with most POTM titles")

e = matches['player_name'].value_counts().sort_values(ascending=False).head(15).reset_index()

fig = px.bar(
    e,
    x='count',
    y='player_name',
    orientation='h',
    labels={'count': 'total_POTM'},
    title='Top 15 players with most POTM titles'
)

st.plotly_chart(fig, use_container_width=True)

st.subheader("Venue Fortresses")

venue_wins = matches.groupby(['venue', 'match_winner']).size().reset_index(name='total_wins')

pivot_df = venue_wins.pivot_table(
    index='venue',
    columns='match_winner',
    values='total_wins',
    fill_value=0
)

fig = px.imshow(
    pivot_df,
    text_auto=True,
    aspect="auto",
    color_continuous_scale='YlGnBu',
    title="Venue Fortresses: Total Wins by Team per Stadium",
    labels=dict(x="Winning Team", y="Stadium", color="Wins"),
)

fig.update_layout(
    xaxis_tickangle=-45,
    height=800,
    margin=dict(l=200),
)

st.plotly_chart(fig, use_container_width=True)

st.subheader("Tie/Super Over Frequency")

a1 = matches[matches['result'] == 'tie'].groupby('season_id')['result'].size().reset_index()
new_row = pd.DataFrame({'season_id': [2008, 2011, 2012, 2016, 2018, 2022, 2023, 2024], 'result': [0, 0, 0, 0, 0, 0, 0, 0]})
a2 = pd.concat([a1, new_row]).sort_values('season_id')

fig = px.line(
    a2,
    x='season_id',
    y='result',
    markers=True,
    labels={'season_id': 'seasons', 'result': 'No. of super overs'},
    title='Tie/Super Over Frequency'
)

st.plotly_chart(fig, use_container_width=True)

st.subheader("Batting 1st vs Chasing Win Rates")

df1 = matches.groupby('match_winner')['win_by_runs'].count().reset_index().rename(columns={'win_by_runs':'Matches Won While Batting First','match_winner':'Team'})
df2 = matches.groupby('match_winner')['win_by_wickets'].count().reset_index().rename(columns={'win_by_wickets':'Matches Won While Chasing','match_winner':'Team'})

df3 = df1.merge(df2)

fig = px.bar(
    df3,
    x='Team',
    y=['Matches Won While Batting First', 'Matches Won While Chasing'],
    title="Matches Won: Batting First vs Chasing",
    labels={'value': 'Total Wins', 'variable': 'Win Type'},
    barmode='stack',
    text_auto=True
)

st.plotly_chart(fig, use_container_width=True)


st.subheader("City Match Density")

city_counts = matches['city'].value_counts().reset_index()
city_counts.columns = ['City', 'Match Count']

fig = px.treemap(
    city_counts,
    path=[px.Constant("All Host Cities"), 'City'],
    values='Match Count',
    color='Match Count',
    color_continuous_scale='YlGnBu',
    title="City Match Density"
)

st.plotly_chart(fig, use_container_width=True)


st.subheader("Month-wise Match Distribution")

matches['match_date'] = pd.to_datetime(matches['match_date'])
matches['month_name'] = matches['match_date'].dt.month_name()

month_dist = matches.groupby(['season_id', 'month_name']).size().reset_index(name='match_count')
month_order = ['March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November']

fig = px.bar(
    month_dist,
    x='season_id',
    y='match_count',
    color='month_name',
    barmode='group',
    category_orders={"month_name": month_order},
    title="Month-wise Match Distribution Over the Years"
)

st.plotly_chart(fig, use_container_width=True)

st.subheader("Top 10 All-Time Run Scorers")

df4 = ipl.groupby('batter')['batter_runs'].sum().sort_values(ascending=False).head(10).reset_index()

fig = px.bar(
    df4,
    x='batter',
    y='batter_runs',
    labels={'batter': 'Batsmen', 'batter_runs': 'Total Runs'},
    title='Top 10 Batsmen of IPL'
)

st.plotly_chart(fig, use_container_width=True)

st.subheader("Top 10 All-Time Wicket Takers")

b1 = ipl[~(ipl['wicket_kind']=='run out')]
b2 = b1[~(b1['wicket_kind']=='obstructing the field')]
b3 = b2[~(b2['wicket_kind']=='retired out')]
b4 = b3[~(b3['wicket_kind']=='retired hurt')]
b5 = b4[b4['is_wicket']==True]

b6 = b5.groupby('bowler')['wicket_kind'].count().rename('Wickets Taken').reset_index().rename(columns={'bowler':'Bowler'}).sort_values('Wickets Taken',ascending=False).head(10)

fig = px.bar(
    b6,
    x='Bowler',
    y='Wickets Taken',
    title='Top 10 All-Time Wicket Takers (Excluding Non-Bowler Wickets)'
)

st.plotly_chart(fig, use_container_width=True)

st.subheader("Head-to-Head Batter Comparison")

batter_list = sorted(ipl['batter'].unique())

col1, col2 = st.columns(2)


def get_stats(player_name):
    player_df = ipl[ipl['batter'] == player_name]

    total_balls = player_df[player_df['is_wide_ball'] == False].shape[0]
    total_runs = player_df['batter_runs'].sum()
    total_matches = player_df['match_id'].unique().shape[0]

    avg = total_runs / total_matches if total_matches > 0 else 0
    sr = (total_runs / total_balls) * 100 if total_balls > 0 else 0

    fours = player_df[player_df['batter_runs'] == 4].shape[0]
    sixes = player_df[player_df['batter_runs'] == 6].shape[0]

    top_10_scores = player_df.groupby(['match_id', 'season_id'])['batter_runs'].sum().reset_index().sort_values(
        by='batter_runs', ascending=False).head(10)

    scoring_dist = player_df['batter_runs'].value_counts().reset_index()
    scoring_dist.columns = ['Run Type', 'Count']

    return {
        "runs": total_runs,
        "balls": total_balls,
        "avg": avg,
        "sr": sr,
        "fours": fours,
        "sixes": sixes,
        "top_10": top_10_scores,
        "dist": scoring_dist
    }



with col1:
    A = st.selectbox("Select Player A", batter_list, index=batter_list.index('V Kohli'))
    res_a = get_stats(A)

    st.metric("Total Runs", res_a['runs'])
    st.metric("Average", round(res_a['avg'], 2))
    st.metric("Strike Rate", round(res_a['sr'], 2))
    st.write("**Boundary Count:**")
    st.write(f"4s: {res_a['fours']} | 6s: {res_a['sixes']}")

    fig_a = px.pie(res_a['dist'], names='Run Type', values='Count', hole=0.5, title=f"{A} Boundary Distribution")
    st.plotly_chart(fig_a, use_container_width=True)

    st.write("**Top 10 Scores:**")
    st.dataframe(res_a['top_10'], hide_index=True)

with col2:
    B = st.selectbox("Select Player B", batter_list, index=batter_list.index('MS Dhoni'))
    res_b = get_stats(B)

    st.metric("Total Runs", res_b['runs'])
    st.metric("Average", round(res_b['avg'], 2))
    st.metric("Strike Rate", round(res_b['sr'], 2))
    st.write("**Boundary Count:**")
    st.write(f"4s: {res_b['fours']} | 6s: {res_b['sixes']}")

    fig_b = px.pie(res_b['dist'], names='Run Type', values='Count', hole=0.5, title=f"{B} Boundary Distribution")
    st.plotly_chart(fig_b, use_container_width=True)

    st.write("**Top 10 Scores:**")
    st.dataframe(res_b['top_10'], hide_index=True)

    st.set_page_config(page_title="IPL Analytics", layout="wide")

st.subheader("Head-to-Head Bowler Comparison")

bowler_list = sorted(ipl['bowler'].unique())

col1, col2 = st.columns(2)


def get_bowler_stats(name):
    a = ipl[ipl['bowler'] == name]

    balls_bowled = a.shape[0]
    legal_deliveries = a[(a['is_wide_ball'] == False) & (a['is_no_ball'] == False)]
    total_legal_balls = legal_deliveries.shape[0]

    overs_notation = f"{total_legal_balls // 6}.{total_legal_balls % 6}"

    runs_conceded = a['total_runs'].sum()

    valid_wicket_kinds = ['caught', 'bowled', 'lbw', 'stumped', 'caught and bowled', 'hit wicket']
    wickets_taken = a[a['wicket_kind'].isin(valid_wicket_kinds)].shape[0]

    avg = runs_conceded / wickets_taken if wickets_taken > 0 else 0
    economy = runs_conceded / (total_legal_balls / 6) if total_legal_balls > 0 else 0
    sr = total_legal_balls / wickets_taken if wickets_taken > 0 else 0
    dot_ball_percent = (a[a['total_runs'] == 0].shape[0] / balls_bowled) * 100 if balls_bowled > 0 else 0

    wickets_distribution = a[a['is_wicket'] == True]['phase'].value_counts().reset_index()
    wickets_distribution.columns = ['Phase', 'Wickets']

    boundaries_conceded = a[a['batter_runs'].isin([4, 6])]['batter_runs'].value_counts().reset_index()
    boundaries_conceded.columns = ['Boundary Type', 'Count']

    return {
        "overs": overs_notation,
        "runs": runs_conceded,
        "wickets": wickets_taken,
        "avg": avg,
        "economy": economy,
        "sr": sr,
        "dot_percent": dot_ball_percent,
        "phase_dist": wickets_distribution,
        "boundary_dist": boundaries_conceded

    }


with col1:
    A_name = st.selectbox("Select Bowler A", bowler_list, index=bowler_list.index('Z Khan'))
    res_a = get_bowler_stats(A_name)

    st.metric("Overs", res_a['overs'])
    st.metric("Wickets", res_a['wickets'])
    st.metric("Economy", round(res_a['economy'], 2))
    st.metric("Average", round(res_a['avg'], 2))
    st.write(f"**Dot Ball %:** {round(res_a['dot_percent'], 1)}%")

    fig_a = px.pie(res_a['boundary_dist'], names='Boundary Type', values='Count',
                   title=f"{A_name} Boundaries Conceded", hole=0.4)
    st.plotly_chart(fig_a, use_container_width=True)

with col2:
    B_name = st.selectbox("Select Bowler B", bowler_list, index=bowler_list.index('Rashid Khan'))
    res_b = get_bowler_stats(B_name)

    st.metric("Overs", res_b['overs'])
    st.metric("Wickets", res_b['wickets'])
    st.metric("Economy", round(res_b['economy'], 2))
    st.metric("Average", round(res_b['avg'], 2))
    st.write(f"**Dot Ball %:** {round(res_b['dot_percent'], 1)}%")

    fig_b = px.pie(res_b['boundary_dist'], names='Boundary Type', values='Count',
                   title=f"{B_name} Boundaries Conceded", hole=0.4)
    st.plotly_chart(fig_b, use_container_width=True)

st.write("### Wickets by Match Phase")
phase_data = pd.concat([
    res_a['phase_dist'].assign(Bowler=A_name),
    res_b['phase_dist'].assign(Bowler=B_name)
])
fig_phase = px.bar(phase_data, x='Phase', y='Wickets', color='Bowler', barmode='group')
st.plotly_chart(fig_phase, use_container_width=True)


st.subheader("Extras Breakdown by Team")

extras_df = ipl.groupby('team_bowling')[['is_wide_ball', 'is_no_ball', 'is_leg_bye', 'is_bye', 'is_penalty']].sum().reset_index()

extras_df.columns = ['Team', 'Wide Balls', 'No Balls', 'Leg Byes', 'Byes', 'Penalty Balls']

extras_df['Total'] = extras_df[['Wide Balls', 'No Balls', 'Leg Byes', 'Byes', 'Penalty Balls']].sum(axis=1)

for col in ['Wide Balls', 'No Balls', 'Leg Byes', 'Byes', 'Penalty Balls']:
    extras_df[col] = (extras_df[col] / extras_df['Total']) * 100

fig = px.bar(
    extras_df,
    x='Team',
    y=['Wide Balls', 'No Balls', 'Leg Byes', 'Byes'],
    labels={'value': 'Percentage (%)', 'variable': 'Extra Type', 'Team': 'Bowling Team'},
    title='Extras Breakdown by Team',
    color_discrete_sequence=px.colors.qualitative.Set1
)

fig.update_layout(
    xaxis_tickangle=-45,
    legend_title_text='Type of Extra'
)

st.plotly_chart(fig, use_container_width=True)


st.subheader("Runs Scored by Phase")

def get_phase(over):
    if over < 6:
        return 'Powerplay (1-6)'
    elif over < 15:
        return 'Middle Overs (7-15)'
    else:
        return 'Death Overs (16-20)'

ipl['phase'] = ipl['over_number'].apply(get_phase)

e1 = ipl.groupby(['season_id', 'phase'])['total_runs'].sum().reset_index()

fig = px.area(
    e1,
    x="season_id",
    y="total_runs",
    color="phase",
    title="Runs Scored by Phase (Powerplay, Middle, Death Overs)",
    category_orders={"phase": ["Powerplay (1-6)", "Middle Overs (7-15)", "Death Overs (16-20)"]},
    color_discrete_map={
        "Powerplay (1-6)": "#1f77b4",
        "Middle Overs (7-15)": "#ff7f0e",
        "Death Overs (16-20)": "#2ca02c"
    },
    labels={
        "season_id": "Season",
        "total_runs": "Total Runs Scored",
        "phase": "Match Phase"
    }
)

st.plotly_chart(fig, use_container_width=True)