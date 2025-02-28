from flask import Flask, render_template, request
import csv
from datetime import datetime, timedelta
import calendar
import pandas as pd
from sklearn.linear_model import LinearRegression
import numpy as np
# NEW: For file operations
import os

app = Flask(__name__)

# Existing data_types dictionary (unchanged)
data_types = {
    'steps': {'goal': 8000, 'unit': 'steps', 'csv': 'steps_data.csv', 'label': 'Steps', 'column': 'steps'},
    'sleep': {'goal': 8, 'unit': 'hours', 'csv': 'sleep_data.csv', 'label': 'Sleep Hours', 'column': 'value'},
    'hydration': {'goal': 2, 'unit': 'liters', 'csv': 'hydration_data.csv', 'label': 'Hydration (liters)', 'column': 'value'},
    'calories': {'goal': 2300, 'unit': 'calories', 'csv': 'calorie_intake_data.csv', 'label': 'Calorie Intake', 'column': 'value'},
}

# Existing month_names (unchanged)
month_names = [
    'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December'
]

# NEW: Function to save prediction to CSV
def save_prediction(prediction, week_start, week_end):
    file_exists = os.path.isfile('step_predictions.csv')
    with open('step_predictions.csv', 'a', newline='') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(['week_start', 'week_end', 'predicted_steps'])
        writer.writerow([week_start.strftime('%Y-%m-%d'), week_end.strftime('%Y-%m-%d'), prediction])

# NEW: Function to evaluate predictions
def evaluate_predictions():
    try:
        # Load actual steps and predictions
        steps_df = pd.read_csv('steps_data.csv', parse_dates=['date'])
        preds_df = pd.read_csv('step_predictions.csv', parse_dates=['week_start', 'week_end'])
        
        # Calculate weekly averages from actual data
        steps_df['week_start'] = steps_df['date'] - pd.to_timedelta(steps_df['date'].dt.weekday + 1, unit='D') + pd.offsets.Week(weekday=6)
        weekly_actual = steps_df.groupby('week_start')['steps'].mean().reset_index()
        
        # Merge with predictions where actual data exists
        merged = preds_df.merge(weekly_actual, left_on='week_start', right_on='week_start', how='inner')
        if merged.empty:
            return None  # No overlapping data yet
        
        # Calculate Mean Absolute Error
        mae = abs(merged['predicted_steps'] - merged['steps']).mean()
        return round(mae, 0)
    except Exception as e:
        print(f"Evaluation error: {e}")
        return None

# NEW: Updated function to predict and save
def predict_next_week_steps():
    try:
        # Load and filter data (exclude 2024, include 2016-2023 and 2025 up to Feb 28)
        df = pd.read_csv('steps_data.csv', parse_dates=['date'])
        df = df[(df['date'].dt.year <= 2023) | ((df['date'].dt.year == 2025) & (df['date'] <= '2025-02-28'))]
        
        # Group by week and calculate average steps
        df['week'] = df['date'].dt.isocalendar().week
        df['year'] = df['date'].dt.year
        weekly_avg = df.groupby(['year', 'week'])['steps'].mean().reset_index()
        
        # Weight 2025 data higher
        weekly_avg['weight'] = np.where(weekly_avg['year'] == 2025, 1.2, 1.0)
        
        # Prepare features and target
        X = weekly_avg[['year', 'week']]
        y = weekly_avg['steps']
        weights = weekly_avg['weight']
        
        # Train model
        model = LinearRegression()
        model.fit(X, y, sample_weight=weights)
        
        # Use current date dynamically
        current_date = datetime.now()
        current_week = current_date.isocalendar()[1]
        current_year = current_date.year
        next_week = current_week + 1
        next_year = current_year if next_week <= 52 else current_year + 1
        next_week = next_week % 52 if next_week > 52 else next_week
        
        # Calculate next week's date range
        days_to_sunday = (6 - current_date.weekday() + 1) % 7
        week_start = current_date + timedelta(days=days_to_sunday)
        week_end = week_start + timedelta(days=6)
        week_range = f"{week_start.strftime('%b %-d')} - {week_end.strftime('%b %-d')}"
        
        # Predict steps for next week
        prediction = model.predict([[next_year, next_week]])[0]
        prediction = round(prediction, 0)
        
        # NEW: Save the prediction
        save_prediction(prediction, week_start, week_end)
        
        return prediction, week_range
    except Exception as e:
        print(f"Prediction error: {e}")
        return 0, "N/A"

@app.route('/', methods=['GET'])
def index():
    # Existing logic (unchanged)
    data_type = request.args.get('data_type', 'steps')
    if data_type not in data_types:
        data_type = 'steps'
    
    csv_file = data_types[data_type]['csv']
    goal = data_types[data_type]['goal']
    unit = data_types[data_type]['unit']
    label = data_types[data_type]['label']
    column = data_types[data_type]['column']

    year_str = request.args.get('year', '2024')
    month_str = request.args.get('month', '12')
    
    try:
        year = int(year_str)
        month = int(month_str)
    except:
        year = 2024
        month = 12

    if year < 2016:
        year = 2016
    if year > 2024:
        year = 2024
    if month < 1:
        month = 1
    if month > 12:
        month = 12

    if month == 12:
        next_month = 1
        next_year = year + 1
    else:
        next_month = month + 1
        next_year = year

    start_date = datetime(year, month, 1)
    try:
        end_date = datetime(next_year, next_month, 1)
    except:
        end_date = datetime(year, month, 31)
    days_in_month = (end_date - start_date).days

    all_data = {}
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                d = datetime.strptime(row['date'], '%Y-%m-%d').date()
                all_data[d] = float(row[column])
            except:
                pass

    data_month = {}
    for day_num in range(1, days_in_month + 1):
        date_key = datetime(year, month, day_num).date()
        data_month[day_num] = all_data.get(date_key, 0)

    month_data = [(day, data_month[day]) for day in data_month]

    calendar.setfirstweekday(calendar.SUNDAY)
    start_dow_python = start_date.weekday()
    start_dow_sunday = (start_dow_python + 1) % 7

    month_grid = []
    for _ in range(start_dow_sunday):
        month_grid.append((0, 0, True))
    for day, value in month_data:
        month_grid.append((day, value, False))

    start_date_str = request.args.get('start_date', '')
    end_date_str = request.args.get('end_date', '')
    group_by = request.args.get('group_by', 'day')

    if not start_date_str or not end_date_str:
        default_start = datetime(2024, 12, 1).date()
        default_end = datetime(2024, 12, 31).date()
        start_date_str = default_start.strftime('%Y-%m-%d')
        end_date_str = default_end.strftime('%Y-%m-%d')

    try:
        range_start = datetime.strptime(start_date_str, '%Y-%m-%d').date()
    except:
        range_start = datetime(2024, 1, 1).date()
        start_date_str = range_start.strftime('%Y-%m-%d')
    try:
        range_end = datetime.strptime(end_date_str, '%Y-%m-%d').date()
    except:
        range_end = datetime(2024, 12, 31).date()
        end_date_str = range_end.strftime('%Y-%m-%d')

    if range_start > range_end:
        range_start, range_end = range_end, range_start

    date_cursor = range_start
    date_value_list = []
    while date_cursor <= range_end:
        date_value = all_data.get(date_cursor, 0)
        date_value_list.append((date_cursor, date_value))
        date_cursor += timedelta(days=1)

    grouped_data = []
    if group_by == 'day':
        for d, val in date_value_list:
            label = d.strftime('%m-%d')
            grouped_data.append((label, val))
    elif group_by == 'week':
        week_sums = {}
        week_counts = {}
        for d, val in date_value_list:
            yw = d.isocalendar()[0:2]
            if yw not in week_sums:
                week_sums[yw] = 0
                week_counts[yw] = 0
            week_sums[yw] += val
            week_counts[yw] += 1
        for yw in sorted(week_sums.keys()):
            y_val, w_val = yw
            label = f'{y_val}-W{w_val}'
            avg = week_sums[yw] / week_counts[yw]
            grouped_data.append((label, avg))
    else:
        month_sums = {}
        month_counts = {}
        for d, val in date_value_list:
            ym = (d.year, d.month)
            if ym not in month_sums:
                month_sums[ym] = 0
                month_counts[ym] = 0
            month_sums[ym] += val
            month_counts[ym] += 1
        for ym in sorted(month_sums.keys()):
            y_val, m_val = ym
            label = f'{y_val}-{m_val:02d}'
            avg = month_sums[ym] / month_counts[ym]
            grouped_data.append((label, avg))

    chart_labels = [t[0] for t in grouped_data]
    chart_values = [round(t[1], 2) for t in grouped_data]

    def calculate_stats(data_list, goal):
        if not data_list:
            return {
                'max': 0, 'min': 0, 'avg': 0, 'highest_streak': 0,
                'current_streak': 0, 'goal_percent': 0
            }
        values = [v for _, v in data_list if v > 0]
        if not values:
            return {
                'max': 0, 'min': 0, 'avg': 0, 'highest_streak': 0,
                'current_streak': 0, 'goal_percent': 0
            }
        max_val = max(values)
        min_val = min(values)
        avg_val = sum(values) / len(values)
        
        current_streak = 0
        highest_streak = 0
        for i in range(len(data_list)):
            if data_list[i][1] >= goal:
                current_streak += 1
                highest_streak = max(highest_streak, current_streak)
            else:
                current_streak = 0
        if data_list and data_list[-1][1] >= goal:
            current_streak = sum(1 for d, v in data_list[-30:] if v >= goal)

        goal_met = sum(1 for _, v in data_list if v >= goal)
        goal_percent = (goal_met / len(data_list) * 100) if data_list else 0

        return {
            'max': max_val, 'min': min_val, 'avg': round(avg_val, 1),
            'highest_streak': highest_streak, 'current_streak': current_streak,
            'goal_percent': round(goal_percent, 1)
        }

    current_stats = calculate_stats(date_value_list, goal)
    all_time_stats = calculate_stats([(d, v) for d, v in all_data.items()], goal)

    start_display = range_start.strftime('%b') + " " + str(range_start.day)
    end_display = range_end.strftime('%b') + " " + str(range_end.day)
    stats_range = start_display + " - " + end_display

    # NEW: Get prediction, week range, and evaluation for steps only
    prediction, week_range = predict_next_week_steps() if data_type == 'steps' else (None, None)
    prediction_error = evaluate_predictions() if data_type == 'steps' else None

    # Existing render_template with updated variables
    return render_template(
        'index.html',
        month_data=month_data,
        goal=goal,
        selected_year=year,
        selected_month=month,
        month_grid=month_grid,
        data_type=data_type,
        unit=unit,
        label=label,
        month_names=month_names,
        start_date_str=start_date_str,
        end_date_str=end_date_str,
        group_by=group_by,
        chart_labels=chart_labels,
        chart_values=chart_values,
        stats_range=stats_range,
        current_stats=current_stats,
        all_time_stats=all_time_stats,
        prediction=prediction,
        week_range=week_range,
        prediction_error=prediction_error  # NEW: Pass error to template
    )

if __name__ == '__main__':
    app.run(debug=True)