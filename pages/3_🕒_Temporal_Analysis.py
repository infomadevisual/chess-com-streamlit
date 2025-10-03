import streamlit as st
import pandas as pd
from utils.app_session import AppSession
from utils.ui import inject_page_styles, time_filter_controls 
import altair as alt

st.set_page_config(page_title="Temporal Analysis", page_icon="🕒", layout="wide")
st.header("Temporal Analysis")
inject_page_styles()

session = AppSession.from_streamlit()
if session.game_count == 0:
    st.warning("No data loaded. Go back to Home and load games.")
    st.stop()

df = session.games_df.copy()

# ---- Apply filters ----
df = time_filter_controls(df, key_prefix="temporal")

if df.empty:
    st.info("No games match filters.")
    st.stop()

# ---- Add temporal columns ----
df["year"] = df["end_time_local"].dt.year
df["month"] = df["end_time_local"].dt.month
df["weekday"] = df["end_time_local"].dt.day_name()
df["hour"] = df["end_time_local"].dt.hour

# ---- Aggregations ----
tabs = st.tabs(["By Hour", "By Weekday", "By Month", "By Year"])

with tabs[0]:
    tmp = (
        df.groupby("hour")["user_result_simple"]
        .value_counts(normalize=True)
        .rename("share")
        .reset_index()
    )

    counts = df.groupby("hour").size().rename("n").reset_index()
    tmp = tmp.merge(counts, on="hour", how="left")
    tmp["label"] = tmp["hour"].astype(str) + " (" + tmp["n"].astype(str) + ")"

    tmp["hour"] = tmp["hour"].astype("Int64").astype(str)
    tmp["share"] = tmp["share"]*100
    tmp = tmp[tmp["share"] > 0]

    chart = (
        alt.Chart(tmp)
        .mark_bar()
        .encode(
            x=alt.X("label:N", title="Hours", sort=None, axis=alt.Axis(labelAngle=0)),
            y=alt.Y("share:Q", title="Share (%)"),
            color=alt.Color("user_result_simple:N", sort=["win","draw","loss"])
        )
    )
    st.altair_chart(chart, use_container_width=True)

with tabs[1]:
    order = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]

    weekday_long = (
        df.groupby("weekday")["user_result_simple"]
        .value_counts(normalize=True)
        .rename("share")
        .reset_index()
    )

    # enforce order
    weekday_long["weekday"] = pd.Categorical(weekday_long["weekday"], categories=order, ordered=True)
    weekday_long = weekday_long.sort_values("weekday")

    # add counts per weekday
    counts = df.groupby("weekday").size().rename("n").reset_index()
    weekday_long = weekday_long.merge(counts, on="weekday", how="left")

    # build x labels and percentage
    weekday_long["label"] = weekday_long["weekday"].astype(str) + " (" + weekday_long["n"].astype(str) + ")"
    weekday_long["pct"] = weekday_long["share"] * 100

    chart = (
        alt.Chart(weekday_long)
        .mark_bar()
        .encode(
            x=alt.X("label:N", title="Weekdays", sort=None, axis=alt.Axis(labelAngle=0, title=None)),
            y=alt.Y("pct:Q", title="Share (%)"),
            color=alt.Color("user_result_simple:N", sort=["win","draw","loss"])
        )
    )

    st.altair_chart(chart, use_container_width=True)

with tabs[2]:
    tmp = (
        df.groupby("month")["user_result_simple"]
        .value_counts(normalize=True)
        .rename("share")
        .reset_index()
    )

    counts = df.groupby("month").size().rename("n").reset_index()
    tmp = tmp.merge(counts, on="month", how="left")
    tmp["label"] = tmp["month"].astype(str) + " (" + tmp["n"].astype(str) + ")"

    tmp["month"] = tmp["month"].astype("Int64").astype(str)
    tmp["share"] = tmp["share"]*100
    tmp = tmp[tmp["share"] > 0]

    chart = (
        alt.Chart(tmp)
        .mark_bar()
        .encode(
            x=alt.X("label:N", title="Months", sort=None, axis=alt.Axis(labelAngle=0)),
            y=alt.Y("share:Q", title="Share (%)"),
            color=alt.Color("user_result_simple:N", sort=["win","draw","loss"])
        )
    )
    st.altair_chart(chart, use_container_width=True)
    
with tabs[3]:
    tmp = (
        df.groupby("year")["user_result_simple"]
        .value_counts(normalize=True)
        .rename("share")
        .reset_index()
    )

    counts = df.groupby("year").size().rename("n").reset_index()
    tmp = tmp.merge(counts, on="year", how="left")
    tmp["label"] = tmp["year"].astype(str) + " (" + tmp["n"].astype(str) + ")"

    tmp["year"] = tmp["year"].astype("Int64").astype(str)
    tmp["share"] = tmp["share"]*100
    tmp = tmp[tmp["share"] > 0]

    chart = (
        alt.Chart(tmp)
        .mark_bar()
        .encode(
            x=alt.X("label:N", title="Years", sort=None, axis=alt.Axis(labelAngle=0)),
            y=alt.Y("share:Q", title="Share (%)"),
            color=alt.Color("user_result_simple:N", sort=["win","draw","loss"])
        )
    )
    st.altair_chart(chart, use_container_width=True)