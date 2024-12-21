import streamlit as st
import pandas as pd
import numpy as np
from datetime import date

# NEW: Load external CSS
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# NEW: Apply external CSS
local_css("styles.css")

st.title("My Personal Habits Dashboard")

# Load and prepare data
df = pd.read_csv("steps_data.csv")
df['date'] = pd.to_datetime(df['date'])
df = df.sort_values('date')
df['steps'] = df['steps'].astype(int)

# Basic Statistics
st.header("Basic Statistics")
col1, col2, col3 = st.columns(3)
col1.metric("Average Daily Steps", f"{df['steps'].mean():,.0f}")
col2.metric("Total Days Recorded", f"{df['date'].nunique():,}")
col3.metric("Max Daily Steps", f"{df['steps'].max():,}")

# Default start and end date
default_start = date(2024, 1, 1)
default_end = date(2024, 12, 18)

# Date range filter
st.subheader("Filter Data by Date Range")
date_range = st.date_input(
    "Select date range:",
    value=[default_start, default_end],
    min_value=min(df['date']).date(),
    max_value=max(df['date']).date()
)

start_date, end_date = date_range
filtered_df = df[(df['date'].dt.date >= start_date) & (df['date'].dt.date <= end_date)]

st.sidebar.header("View Steps By")
aggregation_level = st.sidebar.selectbox(
    "Aggregation Level",
    ["Daily", "Weekly", "Monthly", "Yearly"],
    index=2
)

if aggregation_level == "Monthly":
    filtered_df['year_month'] = filtered_df['date'].dt.to_period('M')
    current_month = filtered_df['date'].dt.month.iloc[0]
    month_start = pd.to_datetime(f"2024-{current_month:02d}-01")
    month_end = month_start + pd.offsets.MonthEnd(1)
    all_days = pd.date_range(month_start, month_end, freq='D')

    daily_data = filtered_df.set_index('date').reindex(all_days, fill_value=0)
    daily_goal = 10000

    calendar_html = "<div class='calendar-container'>"
    for date, steps in daily_data['steps'].items():
        progress = min(steps / daily_goal, 1.0)
        if steps == 0:
            day_class = "no-steps-day"
        elif progress < 1.0:
            day_class = "partial-day"
        else:
            day_class = "full-day"
        calendar_html += (
            f"<div class='day-circle-container'>"
            f"<div class='day-circle {day_class}' style='--progress:{progress};' title='{steps:,.0f} steps'>{date.day}</div>"
            f"</div>"
        )
    calendar_html += "</div>"
    st.markdown(calendar_html, unsafe_allow_html=True)
