# app.py

import streamlit as st
import pandas as pd
import numpy as np

# Title and Header
st.title("My Personal Habits Dashboard")

# 1. Load and Prepare Data 
df = pd.read_csv("steps_data.csv")  # Replace with your actual file path
df['date'] = pd.to_datetime(df['date'])  # Convert date column to datetime
df = df.sort_values('date')  # Sort by date
df['steps'] = df['steps'].astype(int)  # Ensure steps are integers
df = df[df['steps'] > 0]  # Filter out rows with zero or negative steps

# 2. Display Basic Stats 
st.header("Basic Statistics")
col1, col2, col3 = st.columns(3)
col1.metric("Average Daily Steps", f"{df['steps'].mean():.0f}")
col2.metric("Total Days Recorded", f"{df['date'].nunique()}")
col3.metric("Max Daily Steps", f"{df['steps'].max():.0f}")

# 3. Time-Series Visualization 
st.header("Daily Steps Over Time")
st.line_chart(data=df.set_index('date')['steps'])

# 4. Additional Metrics
st.header("Additional Activity Metrics")
avg_duration = df['duration_seconds'].mean()
avg_distance = df['distance_meters'].mean()
avg_calories = df['calories'].mean()

col1, col2, col3 = st.columns(3)
col1.metric("Avg Duration (s)", f"{avg_duration:.1f}")
col2.metric("Avg Distance (m)", f"{avg_distance:.1f}")
col3.metric("Avg Calories", f"{avg_calories:.1f}")

# 5. Date Range Filter
st.subheader("Filter Data by Date Range")
min_date = df['date'].min().date()
max_date = df['date'].max().date()
start_date, end_date = st.date_input(
    "Select date range:",
    value=[min_date, max_date],
    min_value=min_date,
    max_value=max_date
)

# Filter the data based on the selected date range
filtered_df = df[(df['date'].dt.date >= start_date) & (df['date'].dt.date <= end_date)]

# 6. Insight of the Week (Step 6)
st.header("Insight of the Week")

# Add a year-week column for weekly insights
filtered_df['year_week'] = filtered_df['date'].dt.isocalendar().year.astype(str) + '-W' + filtered_df['date'].dt.isocalendar().week.astype(str)

# Generate insights based on weekly data
all_weeks = filtered_df['year_week'].unique()
if len(all_weeks) >= 2:
    this_week = all_weeks[-1]
    last_week = all_weeks[-2]

    this_week_avg = filtered_df[filtered_df['year_week'] == this_week]['steps'].mean()
    last_week_avg = filtered_df[filtered_df['year_week'] == last_week]['steps'].mean()

    if this_week_avg > last_week_avg:
        insight = f"This week you averaged {this_week_avg:.0f} steps/day, which is {(this_week_avg - last_week_avg):.0f} steps more than last week!"
    else:
        insight = f"This week you averaged {this_week_avg:.0f} steps/day, which is {(last_week_avg - this_week_avg):.0f} steps fewer than last week. Consider adding a short walk this weekend to boost next week's total."

    st.write(insight)
else:
    st.write("Not enough data to generate a weekly insight. Keep logging your steps!")
