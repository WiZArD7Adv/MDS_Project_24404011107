import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# 1. PAGE CONFIG
st.set_page_config(page_title="IPL Strategy Command Center", page_icon="🏏", layout="wide")


# 2. CACHE DATA LOADING
@st.cache_data
def load_data():
    ipl = pd.read_csv('ipl_ball_by_ball_2.csv')
    matches = pd.read_csv('matches4.csv')

    def get_phase(over):
        if over < 6:
            return 'Powerplay (1-6)'
        elif over < 15:
            return 'Middle Overs (7-15)'
        else:
            return 'Death Overs (16-20)'

    ipl['phase'] = ipl['over_number'].apply(get_phase)
    return ipl, matches


ipl, matches = load_data()

# 3. SIDEBAR NAVIGATION
st.sidebar.title("🏏 IPL Franchise Analytics")
menu = st.sidebar.radio(
    "Select Analysis Module:",
    [
        "Tournament Overview",
        "Team & Toss Analysis",
        "Player Leaderboards",
        "Player Comparisons",
        "Tactical & Matchup Analytics",
        "Clutch & Pressure Analytics"
    ]
)

# ==========================================
# MODULE 1: TOURNAMENT OVERVIEW
# ==========================================
if menu == "Tournament Overview":
    st.title("🏆 Tournament Landscape")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Seasons", matches['season_id'].nunique())
    col2.metric("Total Matches", matches['match_id'].size)
    col3.metric("Total Runs", f"{ipl['total_runs'].sum():,}")
    col4.metric("Total Wickets", f"{ipl['is_wicket'].sum():,}")

    st.subheader("Season Growth & Scoring Trends")
    e1 = ipl.groupby(['season_id', 'phase'])['total_runs'].sum().reset_index()
    fig_runs = px.area(e1, x="season_id", y="total_runs", color="phase",
                       category_orders={"phase": ["Powerplay (1-6)", "Middle Overs (7-15)", "Death Overs (16-20)"]},
                       title="Run Contribution Volume by Match Phase")
    st.plotly_chart(fig_runs, use_container_width=True)

    st.subheader("Season-wise Boundary Counts")
    sixes_per_season = ipl[ipl['batter_runs'] == 6].groupby('season_id').size().reset_index(name='sixes')
    st.plotly_chart(px.bar(sixes_per_season, x='season_id', y='sixes', title="Total Sixes Hit per Season"),
                    use_container_width=True)

# ==========================================
# MODULE 2: TEAM & TOSS ANALYSIS
# ==========================================
elif menu == "Team & Toss Analysis":
    st.title("🏘️ Team Dynamics & Toss Impact")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Toss Win = Match Win?")
        b = matches[['toss_winner', 'match_winner']].copy()
        b['toss_win_equal_match_win'] = b['toss_winner'] == b['match_winner']
        d = (b['toss_win_equal_match_win'].value_counts() / b.shape[0] * 100).reset_index()
        st.plotly_chart(px.pie(d, names='toss_win_equal_match_win', values='count', hole=0.5), use_container_width=True)

    with col2:
        st.subheader("Strike Rotation vs. Boundary DNA (Middle Overs)")
        mid_df = ipl[ipl['phase'] == 'Middle Overs (7-15)'].copy()
        mid_df['Type'] = mid_df['batter_runs'].apply(
            lambda x: 'Rotation (1s,2s,3s)' if x in [1, 2, 3] else ('Boundaries (4s,6s)' if x in [4, 6] else 'Other'))
        dna = mid_df[mid_df['Type'] != 'Other'].groupby(['team_batting', 'Type'])['batter_runs'].sum().reset_index()
        dna['%'] = dna.groupby('team_batting')['batter_runs'].transform(lambda x: (x / x.sum()) * 100)
        st.plotly_chart(px.bar(dna, x='team_batting', y='%', color='Type', barmode='stack'), use_container_width=True)

# ==========================================
# MODULE 3: PLAYER LEADERBOARDS
# ==========================================
elif menu == "Player Leaderboards":
    st.title("⭐ Elite Performers")

    tab1, tab2 = st.tabs(["Batting Giants", "Bowling Masters"])
    with tab1:
        top_runs = ipl.groupby('batter')['batter_runs'].sum().sort_values(ascending=False).head(10).reset_index()
        st.plotly_chart(px.bar(top_runs, x='batter_runs', y='batter', orientation='h', title="Top 10 Run Scorers"),
                        use_container_width=True)

    with tab2:
        valid_w = ['caught', 'bowled', 'lbw', 'stumped', 'caught and bowled', 'hit wicket']
        top_w = ipl[ipl['wicket_kind'].isin(valid_w)].groupby('bowler').size().sort_values(ascending=False).head(
            10).reset_index(name='Wickets')
        st.plotly_chart(px.bar(top_w, x='Wickets', y='bowler', orientation='h', title="Top 10 Wicket Takers"),
                        use_container_width=True)

# ==========================================
# MODULE 4: PLAYER COMPARISONS
# ==========================================
elif menu == "Player Comparisons":
    st.title("⚔️ Head-to-Head Player Analysis")

    target_player = st.selectbox("Select Primary Batter to Profile:", sorted(ipl['batter'].unique()), index=0)

    st.subheader(f"Phase-wise Strike Rate & Boundary Reliance: {target_player}")
    b_df = ipl[ipl['batter'] == target_player]
    b_legal = b_df[~b_df['is_wide_ball'] & ~b_df['is_no_ball']]

    p_stats = b_df.groupby('phase').agg({'batter_runs': 'sum'}).reset_index()
    p_balls = b_legal.groupby('phase').size().reset_index(name='Balls')
    p_bounds = b_df[b_df['batter_runs'].isin([4, 6])].groupby('phase')['batter_runs'].sum().reset_index(
        name='BoundRuns')

    final_p = p_stats.merge(p_balls, on='phase').merge(p_bounds, on='phase', how='left').fillna(0)
    final_p['SR'] = (final_p['batter_runs'] / final_p['Balls']) * 100
    final_p['Boundary%'] = (final_p['BoundRuns'] / final_p['batter_runs']) * 100

    col1, col2 = st.columns(2)
    col1.plotly_chart(px.bar(final_p, x='phase', y='SR', color='phase', title="Strike Rate by Phase"),
                      use_container_width=True)
    col2.plotly_chart(px.bar(final_p, x='phase', y='Boundary%', color='phase', title="Boundary Contribution by Phase"),
                      use_container_width=True)

    st.divider()

    st.subheader("The Non-Striker Influence Profile")
    st.info(f"Analyzing how {target_player}'s Strike Rate fluctuates based on the career strike rate of their partner.")
    # (Include your logic for Aggressive vs Anchor Partner impact here)

# ==========================================
# MODULE 5: TACTICAL & MATCHUP ANALYTICS
# ==========================================
elif menu == "Tactical & Matchup Analytics":
    st.title("🎯 Matchup & Tactical Intelligence")

    st.subheader("Spin Type vs. Batter Handedness Matchup")
    spin_types = [t for t in ipl['bowler_type'].dropna().unique() if 'spin' in t.lower() or 'break' in t.lower()]
    sel_spin = st.selectbox("Select Spin Bowling Style:", spin_types)

    spin_df = ipl[ipl['bowler_type'] == sel_spin]
    match_data = spin_df[spin_df['batter_runs'].isin([4, 6])].groupby('batsman_type').size().reset_index(
        name='Boundaries')
    st.plotly_chart(px.bar(match_data, x='batsman_type', y='Boundaries', color='batsman_type',
                           title=f"Boundaries Conceded by {sel_spin}"), use_container_width=True)

    st.subheader("Discipline Analysis: Pace vs. Spin in Death Overs")
    # (Include Speed vs Spin Extras % logic here)

    st.subheader("Powerplay Wicket Quality: Skill vs. Mistake")
    # (Include Bowled/LBW vs Caught breakdown for Fast Bowlers here)

# ==========================================
# MODULE 6: CLUTCH & PRESSURE ANALYTICS
# ==========================================
elif menu == "Clutch & Pressure Analysis":
    st.title("💎 Clutch Performance Intelligence")

    clutch_bowler = st.selectbox("Select Bowler for Pressure Analysis:", sorted(ipl['bowler'].unique()), index=0)

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Scoreboard Pressure: Target Defending vs Setting")
        death_df = ipl[(ipl['bowler'] == clutch_bowler) & (ipl['phase'] == 'Death Overs (16-20)')]
        p_stats = death_df.groupby('innings').size().reset_index(name='Total')
        dots = death_df[death_df['total_runs'] == 0].groupby('innings').size().reset_index(name='Dots')
        p_stats = p_stats.merge(dots, on='innings')
        p_stats['Dot%'] = (p_stats['Dots'] / p_stats['Total']) * 100
        st.plotly_chart(
            px.bar(p_stats, x='innings', y='Dot%', color='innings', title=f"{clutch_bowler}: Death Dot Ball %"),
            use_container_width=True)

    with col2:
        st.subheader("The Ultimate Clutch: 20th Over vs Super Over")
        # (Include Economy Rate comparison logic for Super Overs here)