import streamlit as st
import pandas as pd
import numpy as np

st.title("My Personal Habits Dashboard")

# Load and prepare data
df = pd.read_csv("steps_data.csv")  # Update path if needed
df['date'] = pd.to_datetime(df['date'])
df = df.sort_values('date')
df['steps'] = df['steps'].astype(int)
df = df[df['steps'] > 0]

# Basic Statistics
st.header("Basic Statistics")
col1, col2, col3 = st.columns(3)
col1.metric("Average Daily Steps", f"{df['steps'].mean():.0f}")
col2.metric("Total Days Recorded", f"{df['date'].nunique()}")
col3.metric("Max Daily Steps", f"{df['steps'].max():.0f}")

# Additional Activity Metrics
st.header("Additional Activity Metrics")
avg_duration = df['duration_seconds'].mean()
avg_distance = df['distance_meters'].mean()
avg_calories = df['calories'].mean()

col1, col2, col3 = st.columns(3)
col1.metric("Avg Duration (s)", f"{avg_duration:.1f}")
col2.metric("Avg Distance (m)", f"{avg_distance:.1f}")
col3.metric("Avg Calories", f"{avg_calories:.1f}")

# Date range filter
st.subheader("Filter Data by Date Range")
min_date = df['date'].min().date()
max_date = df['date'].max().date()
start_date, end_date = st.date_input(
    "Select date range:",
    value=[min_date, max_date],
    min_value=min_date,
    max_value=max_date
)

# Filter the DataFrame based on the selected range
filtered_df = df[(df['date'].dt.date >= start_date) & (df['date'].dt.date <= end_date)]

# Aggregation level selector
st.sidebar.header("View Steps By")
aggregation_level = st.sidebar.selectbox(
    "Aggregation Level",
    ["Daily", "Weekly", "Monthly", "Yearly"]
)

# Aggregate Data According to the Selected Level
if aggregation_level == "Daily":
    # Daily: Use the date as is. Ensure all days in range are shown.
    # Resample daily to fill any gaps if needed:
    daily_df = filtered_df.set_index('date').resample('D').mean()
    daily_df['steps'] = daily_df['steps'].fillna(0).round().astype(int)
    agg_df = daily_df.copy()
    chart_title = "Daily Average Steps"
    agg_df.index = agg_df.index.strftime('%Y-%m-%d')  # Optional formatting
elif aggregation_level == "Weekly":
    # Weekly: Group by ISO year and week
    filtered_df['year'] = filtered_df['date'].dt.isocalendar().year
    filtered_df['week'] = filtered_df['date'].dt.isocalendar().week
    weekly = filtered_df.groupby(['year', 'week'])['steps'].mean().reset_index()
    weekly['steps'] = weekly['steps'].round().astype(int)

    # Format year-week as YYYY - W##
    weekly['year_week_label'] = weekly.apply(lambda x: f"{x['year']} - W{int(x['week']):02d}", axis=1)
    agg_df = weekly[['year_week_label', 'steps']].set_index('year_week_label')
    chart_title = "Weekly Average Steps"
elif aggregation_level == "Monthly":
    # Monthly: Convert date to a year-month string formatted as YYYY - Mon
    filtered_df['year_month'] = filtered_df['date'].dt.to_period('M')
    monthly = filtered_df.groupby('year_month')['steps'].mean().reset_index()
    monthly['steps'] = monthly['steps'].round().astype(int)

    # Convert period to timestamp then format
    monthly['year_month_label'] = monthly['year_month'].dt.to_timestamp().dt.strftime('%Y - %b')
    agg_df = monthly[['year_month_label', 'steps']].set_index('year_month_label')
    chart_title = "Monthly Average Steps"
elif aggregation_level == "Yearly":
    # Yearly: Group by year
    filtered_df['year'] = filtered_df['date'].dt.year
    yearly = filtered_df.groupby('year')['steps'].mean().reset_index()
    yearly['steps'] = yearly['steps'].round().astype(int)
    # Year is already a nice integer like 2024
    agg_df = yearly.set_index('year')
    chart_title = "Yearly Average Steps"

# Display the Aggregated Chart
st.header(chart_title)
st.line_chart(agg_df['steps'])

# Insight of the Week
# We'll still base the weekly insight on the daily data
st.header("Insight of the Week")
filtered_df['year_week'] = filtered_df['date'].dt.isocalendar().year.astype(str) + '-W' + filtered_df['date'].dt.isocalendar().week.astype(str)

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
