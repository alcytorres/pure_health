from flask import Flask, render_template, request
import csv
from datetime import datetime, timedelta
import calendar

app = Flask(__name__)

# NEW: Define data types with their goals, units, CSV files, and labels
data_types = {
    'steps': {'goal': 8000, 'unit': 'steps', 'csv': 'steps_data.csv', 'label': 'Steps', 'column': 'steps'},
    'sleep': {'goal': 8, 'unit': 'hours', 'csv': 'sleep_data.csv', 'label': 'Sleep Hours', 'column': 'value'},
    'hydration': {'goal': 2, 'unit': 'liters', 'csv': 'hydration_data.csv', 'label': 'Hydration (liters)', 'column': 'value'},
    'calories': {'goal': 2300, 'unit': 'calories', 'csv': 'calorie_intake_data.csv', 'label': 'Calorie Intake', 'column': 'value'},
}

# NEW: Define month_names to pass to template (moved from index.html)
month_names = [
    'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December'
]

@app.route('/', methods=['GET'])
def index():
    # NEW: Get data_type from query parameters, default to 'steps'
    data_type = request.args.get('data_type', 'steps')
    if data_type not in data_types:
        data_type = 'steps'
    
    # NEW: Set variables based on selected data type
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
        month = 11

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

    # NEW: Read data dynamically based on data_type column
    all_data = {}
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                d = datetime.strptime(row['date'], '%Y-%m-%d').date()
                all_data[d] = float(row[column])  # Use float to handle both steps (int) and sleep/hydration (decimal)
            except:
                pass

    # NEW: Generalized from steps_data_month to data_month
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
    for day, value in month_data:  # NEW: Changed 'steps' to 'value'
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

    # NEW: Generalized from date_steps_list to date_value_list
    date_cursor = range_start
    date_value_list = []
    while date_cursor <= range_end:
        date_value = all_data.get(date_cursor, 0)
        date_value_list.append((date_cursor, date_value))
        date_cursor += timedelta(days=1)

    grouped_data = []
    if group_by == 'day':
        for d, val in date_value_list:  # NEW: Changed 'st' to 'val'
            label = d.strftime('%m-%d')
            grouped_data.append((label, val))
    elif group_by == 'week':
        week_sums = {}
        week_counts = {}
        for d, val in date_value_list:  # NEW: Changed 'st' to 'val'
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
        for d, val in date_value_list:  # NEW: Changed 'st' to 'val'
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

    # NEW: Helper function to calculate stats
    def calculate_stats(data_list, goal):
        if not data_list:
            return {
                'max': 0, 'min': 0, 'avg': 0, 'highest_streak': 0,
                'current_streak': 0, 'goal_percent': 0
            }
        values = [v for _, v in data_list if v > 0]  # Exclude zeros for min
        if not values:
            return {
                'max': 0, 'min': 0, 'avg': 0, 'highest_streak': 0,
                'current_streak': 0, 'goal_percent': 0
            }
        max_val = max(values)
        min_val = min(values)
        avg_val = sum(values) / len(values)
        
        # Calculate streaks
        current_streak = 0
        highest_streak = 0
        for i in range(len(data_list)):
            if data_list[i][1] >= goal:
                current_streak += 1
                highest_streak = max(highest_streak, current_streak)
            else:
                current_streak = 0
        # For current streak, assume it continues to today if at the end
        if data_list and data_list[-1][1] >= goal:
            current_streak = sum(1 for d, v in data_list[-30:] if v >= goal)  # Last 30 days as proxy

        # Percentage of days meeting goal
        goal_met = sum(1 for _, v in data_list if v >= goal)
        goal_percent = (goal_met / len(data_list) * 100) if data_list else 0

        return {
            'max': max_val, 'min': min_val, 'avg': round(avg_val, 1),
            'highest_streak': highest_streak, 'current_streak': current_streak,
            'goal_percent': round(goal_percent, 1)
        }

    # NEW: Calculate stats for filtered range (current period)
    current_stats = calculate_stats(date_value_list, goal)

    # NEW: Calculate stats for all-time (full dataset)
    all_time_stats = calculate_stats([(d, v) for d, v in all_data.items()], goal)

    # NEW: Create stats_range string for the stats header based on the selected date range
    start_display = range_start.strftime('%b') + " " + str(range_start.day)  # e.g., "Dec 1"
    end_display = range_end.strftime('%b') + " " + str(range_end.day)          # e.g., "Dec 31"
    stats_range = start_display + " - " + end_display

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
        # NEW: Pass stats_range to the template for dynamic stats header
        stats_range=stats_range,
        current_stats=current_stats,
        all_time_stats=all_time_stats
    )


if __name__ == '__main__':
    app.run(debug=True)