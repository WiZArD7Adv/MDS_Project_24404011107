import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# 1. PAGE CONFIG MUST BE THE VERY FIRST STREAMLIT COMMAND
st.set_page_config(page_title="IPL Data Dashboard", page_icon="🏏", layout="wide")


# 2. CACHE DATA LOADING SO IT DOESN'T FREEZE ON TAB SWITCHES
@st.cache_data
def load_data():
    ipl = pd.read_csv('ipl_ball_by_ball_2.csv')
    matches = pd.read_csv('matches4.csv')

    # Pre-calculate match phases to use later
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

# 3. SIDEBAR NAVIGATION SETUP
st.sidebar.title("🏏 IPL Dashboard")
st.sidebar.markdown("Navigate through the analytics:")
menu = st.sidebar.radio(
    "Select a Page:",
    [
        "Tournament Overview",
        "Team & Toss Analysis",
        "Player Leaderboards",
        "Player Comparisons",
        "In-Depth Match Analytics"

    ]
)

# ==========================================
# PAGE 1: TOURNAMENT OVERVIEW
# ==========================================
if menu == "Tournament Overview":
    st.title("🏆 Tournament Overview")
    st.markdown("A quick overview of all-time Indian Premier League statistics.")

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
    fig1 = px.line(no_of_matches, x='season_id', y='match_id', labels={'season_id': 'season', 'match_id': 'matches'},
                   markers=True)
    st.plotly_chart(fig1, use_container_width=True)

    st.subheader("Tie/Super Over Frequency")
    a1 = matches[matches['result'] == 'tie'].groupby('season_id')['result'].size().reset_index()
    new_row = pd.DataFrame(
        {'season_id': [2008, 2011, 2012, 2016, 2018, 2022, 2023, 2024], 'result': [0, 0, 0, 0, 0, 0, 0, 0]})
    a2 = pd.concat([a1, new_row]).sort_values('season_id')
    fig2 = px.line(a2, x='season_id', y='result', markers=True,
                   labels={'season_id': 'seasons', 'result': 'No. of super overs'})
    st.plotly_chart(fig2, use_container_width=True)

    st.subheader("Month-wise Match Distribution")
    matches['match_date'] = pd.to_datetime(matches['match_date'])
    matches['month_name'] = matches['match_date'].dt.month_name()
    month_dist = matches.groupby(['season_id', 'month_name']).size().reset_index(name='match_count')
    month_order = ['March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November']
    fig3 = px.bar(month_dist, x='season_id', y='match_count', color='month_name', barmode='group',
                  category_orders={"month_name": month_order})
    st.plotly_chart(fig3, use_container_width=True)


# ==========================================
# PAGE 2: TEAM & TOSS ANALYSIS
# ==========================================
elif menu == "Team & Toss Analysis":
    st.title("🪙 Team & Toss Analysis")

    st.subheader("Team Performance (Matches Won)")
    team_wins = matches['match_winner'].value_counts().reset_index()
    fig1 = px.bar(team_wins, x='match_winner', y='count', labels={'count': 'matches won', 'match_winner': 'team'})
    st.plotly_chart(fig1, use_container_width=True)

    st.subheader("Toss Decision Timeline")
    a = matches.groupby(['season_id', 'toss_decision']).size().rename('count').reset_index()
    a['percentage'] = a.groupby('season_id')['count'].transform(lambda x: (x / x.sum()) * 100)
    fig2 = px.area(a, x="season_id", y="percentage", color="toss_decision",
                   color_discrete_map={'field': '#1f77b4', 'bat': '#d62728'}, markers=True)
    st.plotly_chart(fig2, use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Toss Win = Match Win?")
        b = matches[['toss_winner', 'match_winner']].copy()
        b['toss_win_equal_match_win'] = b['toss_winner'] == b['match_winner']
        d = (b['toss_win_equal_match_win'].value_counts() / b.shape[0] * 100).reset_index()
        fig3 = px.pie(d, names='toss_win_equal_match_win', values='count', hole=0.5)
        st.plotly_chart(fig3, use_container_width=True)

    with col2:
        st.subheader("Batting 1st vs Chasing Win Rates")
        df1 = matches.groupby('match_winner')['win_by_runs'].count().reset_index().rename(
            columns={'win_by_runs': 'Batting First', 'match_winner': 'Team'})
        df2 = matches.groupby('match_winner')['win_by_wickets'].count().reset_index().rename(
            columns={'win_by_wickets': 'Chasing', 'match_winner': 'Team'})
        df3 = df1.merge(df2)
        fig4 = px.bar(df3, x='Team', y=['Batting First', 'Chasing'], barmode='stack')
        st.plotly_chart(fig4, use_container_width=True)

    st.subheader("Venue Fortresses")
    venue_wins = matches.groupby(['venue', 'match_winner']).size().reset_index(name='total_wins')
    pivot_df = venue_wins.pivot_table(index='venue', columns='match_winner', values='total_wins', fill_value=0)
    fig5 = px.imshow(pivot_df, text_auto=True, aspect="auto", color_continuous_scale='YlGnBu')
    fig5.update_layout(xaxis_tickangle=-45, height=800, margin=dict(l=200))
    st.plotly_chart(fig5, use_container_width=True)

    st.subheader("City Match Density")
    city_counts = matches['city'].value_counts().reset_index()
    city_counts.columns = ['City', 'Match Count']
    fig6 = px.treemap(city_counts, path=[px.Constant("All Host Cities"), 'City'], values='Match Count',
                      color='Match Count', color_continuous_scale='YlGnBu')
    st.plotly_chart(fig6, use_container_width=True)


# ==========================================
# PAGE 3: PLAYER LEADERBOARDS
# ==========================================
elif menu == "Player Leaderboards":
    st.title("⭐ Player Leaderboards")

    st.subheader("Top 10 All-Time Run Scorers")
    df4 = ipl.groupby('batter')['batter_runs'].sum().sort_values(ascending=False).head(10).reset_index()
    fig1 = px.bar(df4, x='batter', y='batter_runs')
    st.plotly_chart(fig1, use_container_width=True)

    st.subheader("Top 10 All-Time Wicket Takers")
    b1 = ipl[~ipl['wicket_kind'].isin(['run out', 'obstructing the field', 'retired out', 'retired hurt'])]
    b5 = b1[b1['is_wicket'] == True]
    b6 = b5.groupby('bowler')['wicket_kind'].count().rename('Wickets Taken').reset_index().rename(
        columns={'bowler': 'Bowler'}).sort_values('Wickets Taken', ascending=False).head(10)
    fig2 = px.bar(b6, x='Bowler', y='Wickets Taken')
    st.plotly_chart(fig2, use_container_width=True)

    st.subheader("Top 15 players with most POTM titles")
    e = matches['player_name'].value_counts().sort_values(ascending=False).head(15).reset_index()
    fig3 = px.bar(e, x='count', y='player_name', orientation='h')
    st.plotly_chart(fig3, use_container_width=True)


# ==========================================
# PAGE 4: PLAYER COMPARISONS
# ==========================================
elif menu == "Player Comparisons":
    st.title("⚔️ Player Comparisons")

    # --- BATTER COMPARISON ---
    st.header("Head-to-Head Batter Comparison")
    batter_list = sorted(ipl['batter'].unique())
    col1, col2 = st.columns(2)


    def get_stats(player_name):
        player_df = ipl[ipl['batter'] == player_name]
        total_balls = player_df[player_df['is_wide_ball'] == False].shape[0]
        total_runs = player_df['batter_runs'].sum()
        total_matches = player_df['match_id'].nunique()
        avg = total_runs / total_matches if total_matches > 0 else 0
        sr = (total_runs / total_balls) * 100 if total_balls > 0 else 0
        fours = player_df[player_df['batter_runs'] == 4].shape[0]
        sixes = player_df[player_df['batter_runs'] == 6].shape[0]
        top_10_scores = player_df.groupby(['match_id', 'season_id'])['batter_runs'].sum().reset_index().sort_values(
            by='batter_runs', ascending=False).head(10)
        scoring_dist = player_df['batter_runs'].value_counts().reset_index()
        scoring_dist.columns = ['Run Type', 'Count']
        return {"runs": total_runs, "avg": avg, "sr": sr, "fours": fours, "sixes": sixes, "top_10": top_10_scores,
                "dist": scoring_dist}


    with col1:
        A = st.selectbox("Select Player A", batter_list, index=batter_list.index('V Kohli'))
        res_a = get_stats(A)
        st.metric("Total Runs", res_a['runs'])
        st.metric("Average", round(res_a['avg'], 2))
        st.metric("Strike Rate", round(res_a['sr'], 2))
        st.write(f"**4s:** {res_a['fours']} | **6s:** {res_a['sixes']}")
        fig_a = px.pie(res_a['dist'], names='Run Type', values='Count', hole=0.5)
        st.plotly_chart(fig_a, use_container_width=True)
        st.dataframe(res_a['top_10'], hide_index=True)

    with col2:
        B = st.selectbox("Select Player B", batter_list, index=batter_list.index('MS Dhoni'))
        res_b = get_stats(B)
        st.metric("Total Runs", res_b['runs'])
        st.metric("Average", round(res_b['avg'], 2))
        st.metric("Strike Rate", round(res_b['sr'], 2))
        st.write(f"**4s:** {res_b['fours']} | **6s:** {res_b['sixes']}")
        fig_b = px.pie(res_b['dist'], names='Run Type', values='Count', hole=0.5)
        st.plotly_chart(fig_b, use_container_width=True)
        st.dataframe(res_b['top_10'], hide_index=True)

    st.divider()

    # --- BOWLER COMPARISON ---
    st.header("Head-to-Head Bowler Comparison")
    bowler_list = sorted(ipl['bowler'].unique())
    col3, col4 = st.columns(2)


    def get_bowler_stats(name):
        a = ipl[ipl['bowler'] == name]
        legal_deliveries = a[(a['is_wide_ball'] == False) & (a['is_no_ball'] == False)]
        total_legal_balls = legal_deliveries.shape[0]
        runs_conceded = a['total_runs'].sum()
        valid_wicket_kinds = ['caught', 'bowled', 'lbw', 'stumped', 'caught and bowled', 'hit wicket']
        wickets_taken = a[a['wicket_kind'].isin(valid_wicket_kinds)].shape[0]

        return {
            "overs": f"{total_legal_balls // 6}.{total_legal_balls % 6}",
            "wickets": wickets_taken,
            "economy": runs_conceded / (total_legal_balls / 6) if total_legal_balls > 0 else 0,
            "avg": runs_conceded / wickets_taken if wickets_taken > 0 else 0,
            "dot_percent": (a[a['total_runs'] == 0].shape[0] / a.shape[0]) * 100 if a.shape[0] > 0 else 0,
            "phase_dist": a[a['is_wicket'] == True]['phase'].value_counts().reset_index().rename(
                columns={'count': 'Wickets', 'phase': 'Phase'}),
            "boundary_dist": a[a['batter_runs'].isin([4, 6])]['batter_runs'].value_counts().reset_index().rename(
                columns={'count': 'Count', 'batter_runs': 'Boundary Type'})
        }


    with col3:
        A_name = st.selectbox("Select Bowler A", bowler_list, index=bowler_list.index('Z Khan'))
        res_a_bowl = get_bowler_stats(A_name)
        st.metric("Overs", res_a_bowl['overs'])
        st.metric("Wickets", res_a_bowl['wickets'])
        st.metric("Economy", round(res_a_bowl['economy'], 2))
        st.write(f"**Dot Ball %:** {round(res_a_bowl['dot_percent'], 1)}%")

    with col4:
        B_name = st.selectbox("Select Bowler B", bowler_list, index=bowler_list.index('Rashid Khan'))
        res_b_bowl = get_bowler_stats(B_name)
        st.metric("Overs", res_b_bowl['overs'])
        st.metric("Wickets", res_b_bowl['wickets'])
        st.metric("Economy", round(res_b_bowl['economy'], 2))
        st.write(f"**Dot Ball %:** {round(res_b_bowl['dot_percent'], 1)}%")


# ==========================================
# PAGE 5: IN-DEPTH MATCH ANALYTICS
# ==========================================
elif menu == "In-Depth Match Analytics":
    st.title("📈 In-Depth Match Analytics")

    st.subheader("Total Sixes Hit per Season")
    sixes_in_each_season = ipl[ipl['batter_runs'] == 6].groupby('season_id').size().rename('sixes')
    chart_col, data_col = st.columns([3, 1])
    with chart_col:
        st.bar_chart(sixes_in_each_season, color="#FF4B4B")
    with data_col:
        st.dataframe(sixes_in_each_season, use_container_width=True)

    st.subheader("Extras Breakdown by Team")
    extras_df = ipl.groupby('team_bowling')[
        ['is_wide_ball', 'is_no_ball', 'is_leg_bye', 'is_bye', 'is_penalty']].sum().reset_index()
    extras_df.columns = ['Team', 'Wide Balls', 'No Balls', 'Leg Byes', 'Byes', 'Penalty Balls']
    extras_df['Total'] = extras_df[['Wide Balls', 'No Balls', 'Leg Byes', 'Byes', 'Penalty Balls']].sum(axis=1)
    for col in ['Wide Balls', 'No Balls', 'Leg Byes', 'Byes', 'Penalty Balls']:
        extras_df[col] = (extras_df[col] / extras_df['Total']) * 100
    fig = px.bar(extras_df, x='Team', y=['Wide Balls', 'No Balls', 'Leg Byes', 'Byes'],
                 color_discrete_sequence=px.colors.qualitative.Set1)
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Runs Scored by Phase")
    e1 = ipl.groupby(['season_id', 'phase'])['total_runs'].sum().reset_index()
    fig2 = px.area(e1, x="season_id", y="total_runs", color="phase",
                   category_orders={"phase": ["Powerplay (1-6)", "Middle Overs (7-15)", "Death Overs (16-20)"]},
                   color_discrete_map={"Powerplay (1-6)": "#1f77b4", "Middle Overs (7-15)": "#ff7f0e",
                                       "Death Overs (16-20)": "#2ca02c"})
    st.plotly_chart(fig2, use_container_width=True)





    st.header("The 'Phase Specialist' Premium")


    batter_list_adv = sorted(ipl['batter'].unique())
    selected_batter = st.selectbox("Select a Batter to analyze their Phase profile:", batter_list_adv, index=batter_list_adv.index('V Kohli'))

    b_df = ipl[ipl['batter'] == selected_batter]
    b_legal = b_df[(b_df['is_wide_ball'] == False) & (b_df['is_no_ball'] == False)]

    phase_runs = b_df.groupby('phase')['batter_runs'].sum()
    phase_balls = b_legal.groupby('phase').size()

    boundaries_df = b_df[b_df['batter_runs'].isin([4, 6])]
    phase_boundaries = boundaries_df.groupby('phase')['batter_runs'].sum()

    phase_stats = pd.DataFrame({
        'Runs': phase_runs,
        'Legal Balls': phase_balls,
        'Boundary Runs': phase_boundaries
    }).fillna(0).reset_index()

    phase_stats['Strike Rate'] = (phase_stats['Runs'] / phase_stats['Legal Balls']) * 100
    phase_stats['Boundary %'] = (phase_stats['Boundary Runs'] / phase_stats['Runs']) * 100

    phase_stats = phase_stats.dropna(subset=['Strike Rate'])

    col1, col2 = st.columns(2)

    with col1:
        fig_sr = px.bar(
            phase_stats,
            x='phase',
            y='Strike Rate',
            color='phase',
            category_orders={"phase": ["Powerplay (1-6)", "Middle Overs (7-15)", "Death Overs (16-20)"]},
            color_discrete_map={"Powerplay (1-6)": "#1f77b4", "Middle Overs (7-15)": "#ff7f0e", "Death Overs (16-20)": "#2ca02c"},
            text_auto='.1f',
            title=f"{selected_batter}: Strike Rate by Phase"
        )
        fig_sr.update_layout(showlegend=False, xaxis_title="Match Phase", yaxis_title="Strike Rate")
        st.plotly_chart(fig_sr, use_container_width=True)

    with col2:
        fig_bp = px.bar(
            phase_stats,
            x='phase',
            y='Boundary %',
            color='phase',
            category_orders={"phase": ["Powerplay (1-6)", "Middle Overs (7-15)", "Death Overs (16-20)"]},
            color_discrete_map={"Powerplay (1-6)": "#1f77b4", "Middle Overs (7-15)": "#ff7f0e", "Death Overs (16-20)": "#2ca02c"},
            text_auto='.1f',
            title=f"{selected_batter}: Boundary Percentage by Phase"
        )
        fig_bp.update_layout(showlegend=False, xaxis_title="Match Phase", yaxis_title="% of Runs from Boundaries")
        st.plotly_chart(fig_bp, use_container_width=True)




    st.header("The Cost of Speed vs. Spin (Death Overs)")


    death_overs_df = ipl[ipl['phase'] == 'Death Overs (16-20)'].copy()

    def categorize_bowler(b_type):
        b_type = str(b_type).lower()
        if any(keyword in b_type for keyword in ['fast', 'medium', 'pace']):
            return 'Pace Bowlers'
        elif any(keyword in b_type for keyword in ['spin', 'break', 'orthodox', 'chinaman', 'googly']):
            return 'Spinners'
        else:
            return 'Other'

    death_overs_df['Broad Style'] = death_overs_df['bowler_type'].apply(categorize_bowler)
    death_overs_filtered = death_overs_df[death_overs_df['Broad Style'] != 'Other']

    total_balls = death_overs_filtered.groupby('Broad Style').size().reset_index(name='Total Deliveries')

    extras_condition = (death_overs_filtered['is_wide_ball'] == True) | (death_overs_filtered['is_no_ball'] == True)
    extras_bowled = death_overs_filtered[extras_condition].groupby('Broad Style').size().reset_index(name='Total Extras')

    speed_vs_spin = pd.merge(total_balls, extras_bowled, on='Broad Style')
    speed_vs_spin['Extras Percentage'] = (speed_vs_spin['Total Extras'] / speed_vs_spin['Total Deliveries']) * 100

    fig_speed_spin = px.bar(
        speed_vs_spin,
        x='Broad Style',
        y='Extras Percentage',
        color='Broad Style',
        text_auto='.2f',
        color_discrete_sequence=['#d62728', '#1f77b4'],
        title="Frequency of Extras in Death Overs: Pace vs Spin",
        labels={'Extras Percentage': 'Extras % (Wides & No Balls)'}
    )

    fig_speed_spin.update_layout(showlegend=False, xaxis_title="Bowling Style", yaxis_title="Percentage of Deliveries (%)")
    st.plotly_chart(fig_speed_spin, use_container_width=True)








    st.header("The Scoreboard Pressure Effect")


    death_bowlers = sorted(ipl[ipl['phase'] == 'Death Overs (16-20)']['bowler'].unique())
    selected_pressure_bowler = st.selectbox(
        "Select a Bowler:",
        death_bowlers,
        index=death_bowlers.index('JJ Bumrah') if 'JJ Bumrah' in death_bowlers else 0,
        key='pressure_bowler_selectbox'
    )

    pressure_df = ipl[(ipl['bowler'] == selected_pressure_bowler) &
                      (ipl['phase'] == 'Death Overs (16-20)') &
                      (ipl['innings'].isin([1, 2]))]

    total_death_balls = pressure_df.groupby('innings').size().reset_index(name='Total Balls')
    dot_balls = pressure_df[pressure_df['total_runs'] == 0].groupby('innings').size().reset_index(name='Dot Balls')

    pressure_stats = pd.merge(total_death_balls, dot_balls, on='innings', how='left').fillna(0)
    pressure_stats['Dot Ball %'] = (pressure_stats['Dot Balls'] / pressure_stats['Total Balls']) * 100

    pressure_stats['Innings Context'] = pressure_stats['innings'].map({
        1: 'Setting Target (Innings 1)',
        2: 'Defending Target (Innings 2)'
    })

    fig_pressure = px.bar(
        pressure_stats,
        x='Innings Context',
        y='Dot Ball %',
        color='Innings Context',
        text_auto='.1f',
        color_discrete_sequence=['#1f77b4', '#d62728'],
        title=f"{selected_pressure_bowler}: Death Overs Dot Ball Percentage"
    )

    fig_pressure.update_layout(
        showlegend=False,
        xaxis_title="Match Context",
        yaxis_title="Dot Ball Percentage (%)"
    )

    st.plotly_chart(fig_pressure, use_container_width=True, key='scoreboard_pressure_dot_ball_chart')




    st.header("Strike Rotation vs. Boundary Reliance")


    middle_overs_df = ipl[ipl['phase'] == 'Middle Overs (7-15)'].copy()

    def categorize_runs(runs):
        if runs in [1, 2, 3]:
            return 'Strike Rotation (1s, 2s, 3s)'
        elif runs in [4, 6]:
            return 'Boundaries (4s, 6s)'
        else:
            return 'Other'

    middle_overs_df['Run Type'] = middle_overs_df['batter_runs'].apply(categorize_runs)

    valid_runs_df = middle_overs_df[middle_overs_df['Run Type'] != 'Other']

    team_run_totals = valid_runs_df.groupby(['team_batting', 'Run Type'])['batter_runs'].sum().reset_index()

    team_run_totals['Percentage'] = team_run_totals.groupby('team_batting')['batter_runs'].transform(lambda x: (x / x.sum()) * 100)

    fig_dna = px.bar(
        team_run_totals,
        x='team_batting',
        y='Percentage',
        color='Run Type',
        barmode='stack',
        color_discrete_sequence=['#ff7f0e', '#1f77b4'],
        text_auto='.1f',
        title="Middle Overs (7-15): Run Source DNA by Team"
    )

    fig_dna.update_layout(
        xaxis_title="Batting Team",
        yaxis_title="Percentage of Runs Scored (%)",
        xaxis_tickangle=-45
    )

    st.plotly_chart(fig_dna, use_container_width=True, key='strike_rotation_boundary_reliance_chart')



    st.header("The 'Quality' of Wickets (Head-to-Head)")


    valid_wickets = ['caught', 'bowled', 'lbw', 'stumped', 'caught and bowled', 'hit wicket']
    wicket_df = ipl[(ipl['is_wicket'] == True) & (ipl['wicket_kind'].isin(valid_wickets))]

    bowler_list_q = sorted(wicket_df['bowler'].unique())

    col1, col2 = st.columns(2)
    with col1:
        bowler_a = st.selectbox(
            "Select Bowler A:",
            bowler_list_q,
            index=bowler_list_q.index('TA Boult') if 'TA Boult' in bowler_list_q else 0,
            key='q_bowler_a'
        )
    with col2:
        bowler_b = st.selectbox(
            "Select Bowler B:",
            bowler_list_q,
            index=bowler_list_q.index('YS Chahal') if 'YS Chahal' in bowler_list_q else 1,
            key='q_bowler_b'
        )

    def get_wicket_dist(name):
        df = wicket_df[wicket_df['bowler'] == name]
        dist = df['phase'].value_counts().reset_index()
        dist.columns = ['Phase', 'Wickets']
        dist['Player'] = name
        return dist

    dist_a = get_wicket_dist(bowler_a)
    dist_b = get_wicket_dist(bowler_b)
    combined_dist = pd.concat([dist_a, dist_b])

    fig_quality = px.bar(
        combined_dist,
        x='Phase',
        y='Wickets',
        color='Player',
        barmode='group',
        category_orders={"Phase": ["Powerplay (1-6)", "Middle Overs (7-15)", "Death Overs (16-20)"]},
        color_discrete_sequence=['#1f77b4', '#ff7f0e'],
        text_auto=True,
        title="Wicket Distribution by Phase: Powerplay (Top Order) vs Death (Tail-enders)"
    )

    fig_quality.update_layout(
        xaxis_title="Match Phase",
        yaxis_title="Total Wickets Taken"
    )

    st.plotly_chart(fig_quality, use_container_width=True, key='quality_of_wickets_chart')



    st.header("Matchup: Spin Direction vs. Batter Handedness")


    spin_types = [type for type in ipl['bowler_type'].dropna().unique() if 'spin' in type.lower() or 'break' in type.lower() or 'orthodox' in type.lower()]

    selected_spin_type = st.selectbox(
        "Select Spin Bowling Type:",
        spin_types,
        index=spin_types.index('Right-arm offbreak') if 'Right-arm offbreak' in spin_types else 0,
        key='spin_matchup_selectbox'
    )

    spin_df = ipl[ipl['bowler_type'] == selected_spin_type]

    legal_deliveries = spin_df[(spin_df['is_wide_ball'] == False) & (spin_df['is_no_ball'] == False)]
    balls_faced = legal_deliveries.groupby('batsman_type').size().reset_index(name='Legal Balls')

    boundaries_hit = spin_df[spin_df['batter_runs'].isin([4, 6])].groupby('batsman_type').size().reset_index(name='Boundaries')

    matchup_stats = pd.merge(balls_faced, boundaries_hit, on='batsman_type', how='left').fillna(0)
    matchup_stats['Boundary Frequency (%)'] = (matchup_stats['Boundaries'] / matchup_stats['Legal Balls']) * 100

    matchup_stats = matchup_stats[matchup_stats['Legal Balls'] > 30]

    fig_matchup = px.bar(
        matchup_stats,
        x='batsman_type',
        y='Boundary Frequency (%)',
        color='batsman_type',
        text_auto='.1f',
        color_discrete_sequence=['#1f77b4', '#ff7f0e'],
        title=f"Boundary Frequency Conceded by {selected_spin_type}: LHB vs RHB"
    )

    fig_matchup.update_layout(
        showlegend=False,
        xaxis_title="Batter Handedness",
        yaxis_title="Deliveries Hit for Boundary (%)"
    )

    st.plotly_chart(fig_matchup, use_container_width=True, key='spin_direction_batter_handedness_chart')


    st.header("Wicket Quality Assessment (Powerplay)")


    pp_wickets = ipl[(ipl['phase'] == 'Powerplay (1-6)') & (ipl['is_wicket'] == True)].copy()

    pp_wickets['is_fast'] = pp_wickets['bowler_type'].astype(str).str.lower().str.contains('fast|medium|pace', na=False)
    fast_pp_wickets = pp_wickets[pp_wickets['is_fast']].copy()

    def categorize_wicket(w_kind):
        if w_kind in ['bowled', 'lbw']:
            return 'Bowled / LBW'
        elif w_kind in ['caught', 'caught and bowled']:
            return 'Caught'
        else:
            return 'Other'

    fast_pp_wickets['Wicket Quality'] = fast_pp_wickets['wicket_kind'].apply(categorize_wicket)
    fast_pp_wickets = fast_pp_wickets[fast_pp_wickets['Wicket Quality'] != 'Other']

    fast_bowlers = sorted(fast_pp_wickets['bowler'].unique())

    col1, col2 = st.columns(2)
    with col1:
        bowler_a = st.selectbox(
            "Select Fast Bowler A:",
            fast_bowlers,
            index=fast_bowlers.index('TA Boult') if 'TA Boult' in fast_bowlers else 0,
            key='wq_bowler_a'
        )
    with col2:
        bowler_b = st.selectbox(
            "Select Fast Bowler B:",
            fast_bowlers,
            index=fast_bowlers.index('Mohammed Shami') if 'Mohammed Shami' in fast_bowlers else 1,
            key='wq_bowler_b'
        )

    def get_wicket_quality(name):
        df = fast_pp_wickets[fast_pp_wickets['bowler'] == name]
        quality_counts = df['Wicket Quality'].value_counts().reset_index()
        quality_counts.columns = ['Wicket Quality', 'Count']
        quality_counts['Player'] = name
        if quality_counts['Count'].sum() > 0:
            quality_counts['Percentage'] = (quality_counts['Count'] / quality_counts['Count'].sum()) * 100
        else:
            quality_counts['Percentage'] = 0
        return quality_counts

    wq_a = get_wicket_quality(bowler_a)
    wq_b = get_wicket_quality(bowler_b)
    combined_wq = pd.concat([wq_a, wq_b])

    fig_wq = px.bar(
        combined_wq,
        x='Player',
        y='Percentage',
        color='Wicket Quality',
        barmode='stack',
        text_auto='.1f',
        color_discrete_sequence=['#d62728', '#1f77b4'],
        title="Powerplay Wickets: Pure Skill (Bowled/LBW) vs Mistake-Driven (Caught)"
    )

    fig_wq.update_layout(
        xaxis_title="Fast Bowler",
        yaxis_title="Percentage of Powerplay Wickets (%)"
    )

    st.plotly_chart(fig_wq, use_container_width=True, key='wicket_quality_assessment_chart')

    st.header("The 20th Over vs. Super Over: Ultimate Clutch Test")


    super_over_mask = ipl['is_super_over'].astype(bool) == True
    so_bowlers = sorted(ipl[super_over_mask]['bowler'].unique())

    col1, col2 = st.columns(2)
    with col1:
        bowler_a = st.selectbox(
            "Select Bowler A:",
            so_bowlers,
            index=so_bowlers.index('JJ Bumrah') if 'JJ Bumrah' in so_bowlers else 0,
            key='so_bowler_a'
        )
    with col2:
        bowler_b = st.selectbox(
            "Select Bowler B:",
            so_bowlers,
            index=so_bowlers.index('K Rabada') if 'K Rabada' in so_bowlers else 1 if len(so_bowlers) > 1 else 0,
            key='so_bowler_b'
        )


    def get_clutch_stats(name):
        b_df = ipl[ipl['bowler'] == name]

        df_20 = b_df[(b_df['over_number'] >= 19) & (~b_df['is_super_over'].astype(bool))]
        df_so = b_df[b_df['is_super_over'].astype(bool)]

        def calc_eco(df, situation):
            if df.empty:
                return pd.DataFrame({'Player': [name], 'Situation': [situation], 'Economy Rate': [0.0]})

            legal_balls = df[(df['is_wide_ball'] == False) & (df['is_no_ball'] == False)].shape[0]
            runs = df['total_runs'].sum()
            eco = (runs / legal_balls) * 6 if legal_balls > 0 else 0.0

            return pd.DataFrame({'Player': [name], 'Situation': [situation], 'Economy Rate': [eco]})

        stat_20 = calc_eco(df_20, '20th Over (Regular)')
        stat_so = calc_eco(df_so, 'Super Over')

        return pd.concat([stat_20, stat_so])


    clutch_a = get_clutch_stats(bowler_a)
    clutch_b = get_clutch_stats(bowler_b)
    combined_clutch = pd.concat([clutch_a, clutch_b])

    fig_clutch = px.bar(
        combined_clutch,
        x='Situation',
        y='Economy Rate',
        color='Player',
        barmode='group',
        text_auto='.2f',
        color_discrete_sequence=['#1f77b4', '#ff7f0e'],
        title="Economy Rate Comparison: 20th Over vs Super Over"
    )

    fig_clutch.update_layout(
        xaxis_title="Match Situation",
        yaxis_title="Economy Rate (Runs per Over)"
    )

    st.plotly_chart(fig_clutch, use_container_width=True, key='20th_vs_super_over_chart')


    st.header("Non-Striker Influence: The Partnership Effect")


    legal_balls_all = ipl[(ipl['is_wide_ball'] == False) & (ipl['is_no_ball'] == False)]
    career_runs = ipl.groupby('batter')['batter_runs'].sum()
    career_balls = legal_balls_all.groupby('batter').size()

    valid_batters = career_balls[career_balls >= 150].index
    career_sr = ((career_runs / career_balls) * 100).dropna()
    career_sr = career_sr[career_sr.index.isin(valid_batters)]

    aggressive_ns = career_sr[career_sr >= 140].index
    anchor_ns = career_sr[career_sr < 140].index

    dropdown_batters = sorted(valid_batters.tolist())
    selected_target_batter = st.selectbox(
        "Select a Batter to Analyze:",
        dropdown_batters,
        index=dropdown_batters.index('V Kohli') if 'V Kohli' in dropdown_batters else 0,
        key='non_striker_influence_selectbox'
    )

    partnership_df = ipl[(ipl['batter'] == selected_target_batter) & (ipl['non_striker'].isin(valid_batters))].copy()

    def classify_partner(partner_name):
        if partner_name in aggressive_ns:
            return 'Aggressive Partner (Career SR ≥ 140)'
        elif partner_name in anchor_ns:
            return 'Anchor Partner (Career SR < 140)'
        return 'Other'

    partnership_df['Partner Style'] = partnership_df['non_striker'].apply(classify_partner)
    partnership_df = partnership_df[partnership_df['Partner Style'] != 'Other']

    partner_legal_balls = partnership_df[(partnership_df['is_wide_ball'] == False) & (partnership_df['is_no_ball'] == False)]

    runs_by_partner = partnership_df.groupby('Partner Style')['batter_runs'].sum()
    balls_by_partner = partner_legal_balls.groupby('Partner Style').size()

    influence_stats = pd.DataFrame({'Runs': runs_by_partner, 'Legal Balls': balls_by_partner}).reset_index()
    influence_stats['Strike Rate'] = (influence_stats['Runs'] / influence_stats['Legal Balls']) * 100

    influence_stats = influence_stats[influence_stats['Legal Balls'] > 30]

    fig_influence = px.bar(
        influence_stats,
        x='Partner Style',
        y='Strike Rate',
        color='Partner Style',
        text_auto='.1f',
        color_discrete_sequence=['#ff7f0e', '#1f77b4'],
        title=f"How {selected_target_batter}'s Strike Rate Changes Based on the Non-Striker"
    )

    fig_influence.update_layout(
        showlegend=False,
        xaxis_title="Non-Striker Playstyle",
        yaxis_title=f"{selected_target_batter}'s Strike Rate"
    )

    st.plotly_chart(fig_influence, use_container_width=True, key='non_striker_influence_chart')
