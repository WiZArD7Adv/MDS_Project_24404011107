import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="IPL Data Dashboard", page_icon="🏏", layout="wide")


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

st.sidebar.title("🏏 IPL Dashboard")
st.sidebar.markdown("Navigate through the analytics:")
menu = st.sidebar.radio(
    "Select a Page:",
    [
        "Tournament Overview",
        "Team & Toss Analysis",
        "Player Leaderboards",
        "Player Comparisons",
        "In-Depth Match Analytics",
        "Auction & Scouting Analytics",
        "Tactical & Matchup Analytics",
        "Broadcast & Narrative Analytics"
    ]
)

if menu == "Tournament Overview":
    st.title("🏆 Tournament Overview")
    total_seasons = matches['season_id'].nunique()
    total_matches = matches['match_id'].size
    total_runs = ipl['total_runs'].sum()
    total_wickets = ipl['is_wicket'].sum()

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Seasons", total_seasons)
    with col2:
        st.metric("Matches Played", total_matches)
    with col3:
        st.metric("Total Runs", f"{total_runs:,}")
    with col4:
        st.metric("Total Wickets", f"{total_wickets:,}")

    st.divider()
    st.subheader("Season VS Total matches played")
    no_of_matches = matches.groupby('season_id')['match_id'].count().reset_index()
    fig1 = px.line(no_of_matches, x='season_id', y='match_id', markers=True)
    st.plotly_chart(fig1, use_container_width=True, key="overview_matches")

    st.subheader("Tie/Super Over Frequency")
    a1 = matches[matches['result'] == 'tie'].groupby('season_id')['result'].size().reset_index()
    new_row = pd.DataFrame(
        {'season_id': [2008, 2011, 2012, 2016, 2018, 2022, 2023, 2024], 'result': [0, 0, 0, 0, 0, 0, 0, 0]})
    a2 = pd.concat([a1, new_row]).sort_values('season_id')
    fig2 = px.line(a2, x='season_id', y='result', markers=True)
    st.plotly_chart(fig2, use_container_width=True, key="overview_ties")

elif menu == "Team & Toss Analysis":
    st.title("🪙 Team & Toss Analysis")
    team_wins = matches['match_winner'].value_counts().reset_index()
    fig1 = px.bar(team_wins, x='match_winner', y='count')
    st.plotly_chart(fig1, use_container_width=True, key="team_performance")

    st.subheader("Toss Decision Timeline")
    a = matches.groupby(['season_id', 'toss_decision']).size().rename('count').reset_index()
    a['percentage'] = a.groupby('season_id')['count'].transform(lambda x: (x / x.sum()) * 100)
    fig2 = px.area(a, x="season_id", y="percentage", color="toss_decision")
    st.plotly_chart(fig2, use_container_width=True, key="toss_timeline")

elif menu == "Player Leaderboards":
    st.title("⭐ Player Leaderboards")
    st.subheader("Top 10 All-Time Run Scorers")
    df4 = ipl.groupby('batter')['batter_runs'].sum().sort_values(ascending=False).head(10).reset_index()
    fig1 = px.bar(df4, x='batter', y='batter_runs')
    st.plotly_chart(fig1, use_container_width=True, key="top_scorers")

    st.subheader("Top 10 All-Time Wicket Takers")
    b1 = ipl[~ipl['wicket_kind'].isin(['run out', 'obstructing the field', 'retired out', 'retired hurt'])]
    b6 = b1[b1['is_wicket'] == True].groupby('bowler')['wicket_kind'].count().reset_index().sort_values('wicket_kind',
                                                                                                        ascending=False).head(
        10)
    fig2 = px.bar(b6, x='bowler', y='wicket_kind')
    st.plotly_chart(fig2, use_container_width=True, key="top_bowlers")

elif menu == "Player Comparisons":
    st.title("⚔️ Player Comparisons")
    batter_list = sorted(ipl['batter'].unique())
    col1, col2 = st.columns(2)


    def get_stats(player_name):
        player_df = ipl[ipl['batter'] == player_name]
        total_balls = player_df[player_df['is_wide_ball'] == False].shape[0]
        total_runs = player_df['batter_runs'].sum()
        total_matches = player_df['match_id'].nunique()
        avg = total_runs / total_matches if total_matches > 0 else 0
        sr = (total_runs / total_balls) * 100 if total_balls > 0 else 0
        dist = player_df['batter_runs'].value_counts().reset_index()
        dist.columns = ['Run Type', 'Count']
        return {"runs": total_runs, "avg": avg, "sr": sr, "dist": dist}


    with col1:
        A = st.selectbox("Player A", batter_list, index=batter_list.index('V Kohli'), key="bat_a")
        res_a = get_stats(A)
        st.metric("Runs", res_a['runs'])
        st.metric("SR", round(res_a['sr'], 2))
        st.plotly_chart(px.pie(res_a['dist'], names='Run Type', values='Count', hole=0.5), use_container_width=True,
                        key="pie_a")

    with col2:
        B = st.selectbox("Player B", batter_list, index=batter_list.index('MS Dhoni'), key="bat_b")
        res_b = get_stats(B)
        st.metric("Runs", res_b['runs'])
        st.metric("SR", round(res_b['sr'], 2))
        st.plotly_chart(px.pie(res_b['dist'], names='Run Type', values='Count', hole=0.5), use_container_width=True,
                        key="pie_b")

elif menu == "In-Depth Match Analytics":
    st.title("📈 In-Depth Match Analytics")
    st.subheader("Extras Breakdown by Team")
    extras_df = ipl.groupby('team_bowling')[['is_wide_ball', 'is_no_ball', 'is_leg_bye', 'is_bye']].sum().reset_index()
    fig = px.bar(extras_df, x='team_bowling', y=['is_wide_ball', 'is_no_ball', 'is_leg_bye', 'is_bye'])
    st.plotly_chart(fig, use_container_width=True, key="extras_breakdown")

    st.subheader("Runs Scored by Phase")
    e1 = ipl.groupby(['season_id', 'phase'])['total_runs'].sum().reset_index()
    fig2 = px.area(e1, x="season_id", y="total_runs", color="phase")
    st.plotly_chart(fig2, use_container_width=True, key="runs_by_phase")

elif menu == "Auction & Scouting Analytics":
    st.title("💰 Auction & Scouting Analytics")

    st.header("Phase Specialist Profile")
    batter_list_adv = sorted(ipl['batter'].unique())
    selected_batter = st.selectbox("Select Batter:", batter_list_adv, index=batter_list_adv.index('V Kohli'),
                                   key="scout_batter")
    b_df = ipl[ipl['batter'] == selected_batter]
    b_legal = b_df[(b_df['is_wide_ball'] == False) & (b_df['is_no_ball'] == False)]
    phase_stats = pd.DataFrame({
        'Runs': b_df.groupby('phase')['batter_runs'].sum(),
        'Balls': b_legal.groupby('phase').size(),
        'Boundaries': b_df[b_df['batter_runs'].isin([4, 6])].groupby('phase')['batter_runs'].sum()
    }).fillna(0).reset_index()
    phase_stats['Strike Rate'] = (phase_stats['Runs'] / phase_stats['Balls']) * 100
    phase_stats['Boundary %'] = (phase_stats['Boundaries'] / phase_stats['Runs']) * 100

    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(px.bar(phase_stats, x='phase', y='Strike Rate', color='phase'), use_container_width=True,
                        key="scout_sr")
    with col2:
        st.plotly_chart(px.bar(phase_stats, x='phase', y='Boundary %', color='phase'), use_container_width=True,
                        key="scout_bp")

    st.header("Pace vs Spin Extras (Death Overs)")
    death_overs_df = ipl[ipl['phase'] == 'Death Overs (16-20)'].copy()


    def categorize_bowler(b_type):
        b_type = str(b_type).lower()
        if any(kw in b_type for kw in ['fast', 'medium', 'pace']): return 'Pace'
        return 'Spin'


    death_overs_df['Style'] = death_overs_df['bowler_type'].apply(categorize_bowler)
    extras = death_overs_df.groupby('Style').agg(Total=('Style', 'size'), Extras=('is_wide_ball', 'sum')).reset_index()
    extras['%'] = (extras['Extras'] / extras['Total']) * 100
    st.plotly_chart(px.bar(extras, x='Style', y='%', color='Style'), use_container_width=True,
                    key="scout_extras_pace_spin")

    st.header("Wicket Skill Assessment (Powerplay)")
    pp_wickets = ipl[(ipl['phase'] == 'Powerplay (1-6)') & (ipl['is_wicket'] == True)].copy()
    pp_wickets['Quality'] = pp_wickets['wicket_kind'].apply(
        lambda x: 'Bowled/LBW' if x in ['bowled', 'lbw'] else 'Caught')
    fast_bowlers = sorted(pp_wickets['bowler'].unique())
    b_sel = st.selectbox("Compare Bowler:", fast_bowlers, index=fast_bowlers.index('TA Boult'),
                         key="scout_skill_bowler")
    skill_df = pp_wickets[pp_wickets['bowler'] == b_sel]['Quality'].value_counts().reset_index()
    st.plotly_chart(px.pie(skill_df, names='Quality', values='count'), use_container_width=True, key="scout_skill_pie")

elif menu == "Tactical & Matchup Analytics":
    st.title("♟️ Tactical & Matchup Analytics")

    st.header("Spin vs Handedness Matchup")
    spin_types = [t for t in ipl['bowler_type'].dropna().unique() if 'spin' in t.lower() or 'break' in t.lower()]
    s_type = st.selectbox("Spin Type:", spin_types, key="tactical_spin_type")
    spin_match = ipl[ipl['bowler_type'] == s_type].groupby('batsman_type').agg(Runs=('total_runs', 'sum'),
                                                                               Balls=('ball_number',
                                                                                      'count')).reset_index()
    spin_match['Eco'] = spin_match['Runs'] / (spin_match['Balls'] / 6)
    st.plotly_chart(px.bar(spin_match, x='batsman_type', y='Eco', color='batsman_type'), use_container_width=True,
                    key="tactical_spin_match")

    st.header("Scoreboard Pressure: Dot Ball %")
    death_bowlers = sorted(ipl[ipl['phase'] == 'Death Overs (16-20)']['bowler'].unique())
    b_press = st.selectbox("Bowler:", death_bowlers, index=death_bowlers.index('JJ Bumrah'),
                           key="tactical_press_bowler")
    press_df = ipl[(ipl['bowler'] == b_press) & (ipl['phase'] == 'Death Overs (16-20)')]
    dots = press_df.groupby('innings').agg(Total=('total_runs', 'size'),
                                           Dots=('total_runs', lambda x: (x == 0).sum())).reset_index()
    dots['%'] = (dots['Dots'] / dots['Total']) * 100
    st.plotly_chart(px.bar(dots, x='innings', y='%', color='innings'), use_container_width=True, key="tactical_dots")

    st.header("Partner Influence on Strike Rate")
    batters_150 = career_balls[career_balls >= 150].index
    target_b = st.selectbox("Analyze Batter:", sorted(batters_150), key="tactical_partner_bat")
    part_df = ipl[ipl['batter'] == target_b].copy()
    part_df['Style'] = part_df['non_striker'].apply(lambda x: 'Aggressive' if x in aggressive_ns else 'Anchor')
    res = part_df.groupby('Style').agg(Runs=('batter_runs', 'sum'), Balls=('ball_number', 'count')).reset_index()
    res['SR'] = (res['Runs'] / res['Balls']) * 100
    st.plotly_chart(px.bar(res, x='Style', y='SR', color='Style'), use_container_width=True, key="tactical_partner_sr")

elif menu == "Broadcast & Narrative Analytics":
    st.title("📺 Broadcast & Narrative Analytics")
    st.header("Team Run DNA (Middle Overs)")
    mid_df = ipl[ipl['phase'] == 'Middle Overs (7-15)'].copy()
    mid_df['Type'] = mid_df['batter_runs'].apply(
        lambda x: 'Rotation' if x in [1, 2, 3] else 'Boundaries' if x in [4, 6] else 'Other')
    dna = mid_df[mid_df['Type'] != 'Other'].groupby(['team_batting', 'Type'])['batter_runs'].sum().reset_index()
    dna['%'] = dna.groupby('team_batting')['batter_runs'].transform(lambda x: (x / x.sum()) * 100)
    st.plotly_chart(px.bar(dna, x='team_batting', y='%', color='Type', barmode='stack'), use_container_width=True,
                    key="broadcast_dna")