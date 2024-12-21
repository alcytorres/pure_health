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
df = df[df['steps'] > 0]

# Basic Statistics
st.header("Basic Statistics")
col1, col2, col3 = st.columns(3)
col1.metric("Average Daily Steps", f"{df['steps'].mean():,.0f}")
col2.metric("Total Days Recorded", f"{df['date'].nunique():,}")
col3.metric("Max Daily Steps", f"{df['steps'].max():,}")

# Additional Activity Metrics
st.header("Additional Activity Metrics")
avg_duration = df['duration_seconds'].mean()
avg_distance = df['distance_meters'].mean()
avg_calories = df['calories'].mean()

col1, col2, col3 = st.columns(3)
col1.metric("Avg Duration (s)", f"{avg_duration:,.1f}")
col2.metric("Avg Distance (m)", f"{avg_distance:,.1f}")
col3.metric("Avg Calories", f"{avg_calories:,.1f}")

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

if len(date_range) == 1:
    start_date = date_range[0]
    end_date = default_end
elif len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date, end_date = default_start, default_end

start_date = max(start_date, min(df['date']).date())
end_date = min(end_date, max(df['date']).date())

filtered_df = df[(df['date'].dt.date >= start_date) & (df['date'].dt.date <= end_date)]

st.sidebar.header("View Steps By")
# NEW: Set the default aggregation level to "Monthly" by specifying index=2
aggregation_level = st.sidebar.selectbox(
    "Aggregation Level",
    ["Daily", "Weekly", "Monthly", "Yearly"],
    index=2  # NEW
)

if aggregation_level == "Daily":
    daily_df = filtered_df.set_index('date').resample('D').mean()
    daily_df['steps'] = daily_df['steps'].fillna(0).round().astype(int)
    agg_df = daily_df.copy()
    chart_title = "Daily Average Steps"
    agg_df.index = agg_df.index.strftime('%Y-%m-%d')

    st.header(chart_title)
    st.line_chart(agg_df['steps'])

elif aggregation_level == "Weekly":
    filtered_df['year'] = filtered_df['date'].dt.isocalendar().year
    filtered_df['week'] = filtered_df['date'].dt.isocalendar().week
    weekly = filtered_df.groupby(['year', 'week'])['steps'].mean().reset_index()
    weekly['steps'] = weekly['steps'].round().astype(int)
    weekly['year_week_label'] = weekly.apply(lambda x: f"{x['year']} - W{int(x['week']):02d}", axis=1)
    agg_df = weekly[['year_week_label', 'steps']].set_index('year_week_label')
    chart_title = "Weekly Average Steps"

    st.header(chart_title)
    st.line_chart(agg_df['steps'])

elif aggregation_level == "Monthly":
    filtered_df['year_month'] = filtered_df['date'].dt.to_period('M')
    monthly = filtered_df.groupby('year_month')['steps'].mean().reset_index()
    monthly['steps'] = monthly['steps'].round().astype(int)
    monthly['year_month_label'] = monthly['year_month'].dt.to_timestamp().dt.strftime('%Y - %b')
    agg_df = monthly[['year_month_label', 'steps']].set_index('year_month_label')
    chart_title = "Monthly Average Steps"

    if len(filtered_df) > 0:
        current_year = filtered_df['date'].dt.year.iloc[0]
        current_month = filtered_df['date'].dt.month.iloc[0]
    else:
        current_year = date.today().year
        current_month = date.today().month

    month_start = pd.to_datetime(f"{current_year}-{current_month:02d}-01")
    month_end = (month_start + pd.offsets.MonthEnd(1))
    all_days = pd.date_range(month_start, month_end, freq='D')

    daily_data = filtered_df.set_index('date').resample('D').sum(numeric_only=True)
    daily_data['steps'] = daily_data['steps'].fillna(0)
    daily_data = daily_data.reindex(all_days, fill_value=0)
    daily_data.index.name = 'date'
    daily_data.reset_index(inplace=True)

    total_steps_month = daily_data['steps'].sum()
    avg_steps_month = daily_data['steps'].mean()
    total_distance = filtered_df['distance_meters'].sum() if len(filtered_df) > 0 else 0
    total_calories = filtered_df['calories'].sum() if len(filtered_df) > 0 else 0

    st.markdown(f"<h2 class='monthly-header'>{month_start.strftime('%B %Y')}</h2>", unsafe_allow_html=True)

    st.markdown(
        f"""
        <div class='summary-container'>
            <div class='summary-item'>
                <div><strong>Total Steps</strong></div>
                <div>{total_steps_month:,.0f}</div>
            </div>
            <div class='summary-item'>
                <div><strong>Avg Steps/Day</strong></div>
                <div>{avg_steps_month:,.0f}</div>
            </div>
            <div class='summary-item'>
                <div><strong>Total Distance (m)</strong></div>
                <div>{total_distance:,.1f}</div>
            </div>
            <div class='summary-item'>
                <div><strong>Total Calories</strong></div>
                <div>{total_calories:,.1f}</div>
            </div>
        </div>
        """, unsafe_allow_html=True
    )

    st.markdown("""
    <div class='weekday-labels'>
      <div>S</div><div>M</div><div>T</div><div>W</div><div>T</div><div>F</div><div>S</div>
    </div>
    """, unsafe_allow_html=True)

    def desired_weekday(py_weekday):
        return (py_weekday + 1) % 7

    first_day_pos = desired_weekday(month_start.weekday())

    # NEW: Define daily goal and dynamic progress
    daily_goal = 10000  # NEW

    calendar_html = "<div class='calendar-container'>"
    for _ in range(first_day_pos):
        calendar_html += "<div></div>"

    for _, row in daily_data.iterrows():
        day_num = row['date'].day
        steps_for_day = row['steps']
        # NEW: Calculate progress and apply as a CSS variable
        progress = min(steps_for_day / daily_goal, 1.0)  # NEW
        calendar_html += (
            f"<div class='day-circle-container'>"
            f"<div class='day-circle' style='--progress:{progress};' title='{steps_for_day:,.0f} steps'>{day_num}</div>"
            f"</div>"
        )

    calendar_html += "</div>"
    st.markdown(calendar_html, unsafe_allow_html=True)

    st.header(chart_title)
    st.line_chart(agg_df['steps'])

elif aggregation_level == "Yearly":
    filtered_df['year'] = filtered_df['date'].dt.year
    yearly = filtered_df.groupby('year')['steps'].mean().reset_index()
    yearly['steps'] = yearly['steps'].round().astype(int)
    agg_df = yearly.set_index('year')
    chart_title = "Yearly Average Steps"

    st.header(chart_title)
    st.line_chart(agg_df['steps'])

st.header("Insight of the Week")
filtered_df['year_week'] = filtered_df['date'].dt.isocalendar().year.astype(str) + '-W' + filtered_df['date'].dt.isocalendar().week.astype(str)
all_weeks = filtered_df['year_week'].unique()
if len(all_weeks) >= 2:
    this_week = all_weeks[-1]
    last_week = all_weeks[-2]

    this_week_avg = filtered_df[filtered_df['year_week'] == this_week]['steps'].mean()
    last_week_avg = filtered_df[filtered_df['year_week'] == last_week]['steps'].mean()

    if this_week_avg > last_week_avg:
        insight = f"This week you averaged {this_week_avg:,.0f} steps/day, which is {(this_week_avg - last_week_avg):,} steps more than last week!"
    else:
        insight = f"This week you averaged {this_week_avg:,.0f} steps/day, which is {(last_week_avg - this_week_avg):,} steps fewer than last week. Consider adding a short walk this weekend to boost next week's total."
    st.write(insight)
else:
    st.write("Not enough data to generate a weekly insight. Keep logging your steps!")
