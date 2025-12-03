

import streamlit as st
import pandas as pd
import plotly.express as px

# ---------- Load Data ----------
@st.cache_data
def load_data():
    df = pd.read_csv("NFL_Combined_2025.csv")
    return df

df = load_data()

st.title("NFL Matchup Predictor ")
st.write("Compare two teams using your power metrics and get a simple winner prediction.")

# ---------- Sidebar Controls ----------
st.sidebar.header("Settings")

metric_options = {
    "PSR Points (overall power)": "PSR_POINTS",
    "PSR QB (QB impact)": "PSR_QB",
    "Offense grade": "OFF",
    "Defense grade": "DEF",
    "Projected Wins": "PROJ_WINS",
    "Playoff Probability": "PROJ_PLAYOFFS",
    "Division Title Probability": "PROJ_DIV",
    "Conference Title Probability": "PROJ_CONF",
    "Super Bowl Probability": "PROJ_SB",
    "Strength of Schedule To Date": "SOS_TO_DATE",
    "Strength of Schedule Remaining": "SOS_REMAIN",
}

mode = st.sidebar.radio(
    "Rating mode",
    ["Single metric", "Offense + Defense blend"]
)

if mode == "Single metric":
    metric_label = st.sidebar.selectbox("Choose metric", list(metric_options.keys()))
    metric_col = metric_options[metric_label]
else:
    # For blend mode, we build a synthetic metric: score = w_off * OFF + w_def * DEF
    off_weight = st.sidebar.slider("Offense weight", 0.0, 2.0, 1.0, 0.1)
    def_weight = st.sidebar.slider("Defense weight", 0.0, 2.0, 1.0, 0.1)
    metric_label = f"Blend: {off_weight} × OFF + {def_weight} × DEF"
    metric_col = None  # We'll compute on the fly

st.sidebar.markdown("---")
st.sidebar.write("Higher score = better team for prediction.")

# ---------- Team Selection ----------
teams = df["TEAM"].unique()

col1, col2 = st.columns(2)
with col1:
    team1 = st.selectbox("Team 1", teams, index=0)
with col2:
    team2 = st.selectbox("Team 2", teams, index=1)

if team1 == team2:
    st.warning("Please pick two different teams.")
    st.stop()

# ---------- Extract Team Rows ----------
row1 = df[df["TEAM"] == team1].iloc[0]
row2 = df[df["TEAM"] == team2].iloc[0]

# Compute rating
if mode == "Single metric":
    rating1 = float(row1[metric_col])
    rating2 = float(row2[metric_col])
else:
    rating1 = off_weight * float(row1["OFF"]) + def_weight * float(row1["DEF"])
    rating2 = off_weight * float(row2["OFF"]) + def_weight * float(row2["DEF"])

# ---------- Show Basic Info ----------
st.subheader("Team Snapshot")

info_cols = ["TEAM", "RECORD", "PF", "PA", "OFF", "DEF", "PROJ_WINS"]
summary_df = pd.DataFrame(
    [
        {col: row1[col] for col in info_cols},
        {col: row2[col] for col in info_cols},
    ]
)

st.dataframe(summary_df.set_index("TEAM"))

# ---------- Rating Comparison ----------
st.subheader("Rating Comparison")

comparison_df = pd.DataFrame({
    "TEAM": [team1, team2],
    metric_label: [rating1, rating2],
})

st.dataframe(comparison_df.set_index("TEAM"))

fig = px.bar(
    comparison_df,
    x="TEAM",
    y=metric_label,
    title="Rating Bar Chart",
    text=metric_label
)
fig.update_traces(texttemplate="%{text:.2f}", textposition="outside")
fig.update_layout(yaxis_title="Rating", xaxis_title="Team")
st.plotly_chart(fig, use_container_width=True)

# ---------- Prediction ----------
st.subheader("Prediction")

# Higher rating = better team in this model
if rating1 > rating2:
    winner = team1
    loser = team2
    edge = rating1 - rating2
else:
    winner = team2
    loser = team1
    edge = rating2 - rating1

st.success(
    f"**Predicted winner: {winner}**\n\n"
    f"Edge over {loser}: **{edge:.2f} {metric_label} points**"
)

# ---------- Extra Metrics ----------
with st.expander("Show more advanced comparison"):
    extra_cols = [
        "OVER", "PAS", "PBLK", "RECV", "RUN", "RBLK",
        "RDEF", "TACK", "PRSH", "COV", "SPEC",
        "SOS_TO_DATE", "SOS_REMAIN",
        "PROJ_PLAYOFFS", "PROJ_DIV", "PROJ_CONF", "PROJ_SB"
    ]

    adv_df = pd.DataFrame(
        [
            {"TEAM": team1, **{c: row1[c] for c in extra_cols}},
            {"TEAM": team2, **{c: row2[c] for c in extra_cols}},
        ]
    ).set_index("TEAM")

    st.dataframe(adv_df)
