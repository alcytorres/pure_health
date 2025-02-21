from flask import Flask, render_template, request
import csv
from datetime import datetime, timedelta
import calendar

app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
    # Existing code for Month/Year calendar
    year_str = request.args.get('year', '2024')
    month_str = request.args.get('month', '11')
    
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

    # Compute days in selected month
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

    # Read steps data from CSV (entire dataset)
    all_steps_data = {}
    with open('steps_data.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                d = datetime.strptime(row['date'], '%Y-%m-%d').date()
                all_steps_data[d] = int(row['steps'])
            except:
                pass

    # Build dictionary of day->steps for selected month
    steps_data_month = {}
    for day_num in range(1, days_in_month + 1):
        date_key = datetime(year, month, day_num).date()
        steps_data_month[day_num] = all_steps_data.get(date_key, 0)

    month_data = [(day, steps_data_month[day]) for day in steps_data_month]

    # Prepare placeholders if the month doesn’t start on Sunday
    calendar.setfirstweekday(calendar.SUNDAY)
    start_dow_python = start_date.weekday()  # Monday=0...Sunday=6
    start_dow_sunday = (start_dow_python + 1) % 7  # shift to Sunday=0

    # Combine placeholders + real days into month_grid
    month_grid = []
    for _ in range(start_dow_sunday):
        month_grid.append((0, 0, True))  # (day=0, steps=0, is_placeholder=True)
    for day, steps in month_data:
        month_grid.append((day, steps, False))

    # ----------------------------------------------------------------------
    # NEW: Handle custom date range filtering for the line graph below
    # ----------------------------------------------------------------------
    # 1) Parse query parameters for date range + grouping
    start_date_str = request.args.get('start_date', '')
    end_date_str = request.args.get('end_date', '')
    group_by = request.args.get('group_by', 'day')  # can be 'day', 'week', 'month'

    # 2) Provide defaults if no range specified (changed to full year 2024)
    if not start_date_str or not end_date_str:
        default_start = datetime(2024, 1, 1).date()
        default_end = datetime(2024, 12, 31).date()
        start_date_str = default_start.strftime('%Y-%m-%d')
        end_date_str = default_end.strftime('%Y-%m-%d')

    # 3) Convert strings to date objects
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
        # If user picks an inverted range, swap
        range_start, range_end = range_end, range_start

    # 4) Filter all_steps_data for this date range
    date_cursor = range_start
    date_steps_list = []  # Will hold (date, steps)
    while date_cursor <= range_end:
        date_steps = all_steps_data.get(date_cursor, 0)
        date_steps_list.append((date_cursor, date_steps))
        date_cursor += timedelta(days=1)

    # 5) Group by day/week/month & compute average steps
    #    We'll build a list of (label, avg_steps).
    grouped_data = []  # (label, avg_steps)

    if group_by == 'day':
        # One data point per day
        for d, st in date_steps_list:
            label = d.strftime('%Y-%m-%d')
            grouped_data.append((label, st))
    elif group_by == 'week':
        # Aggregate each Monday-Sunday (or Sunday-Saturday) chunk
        # Simpler approach: group by iso-calendar week number
        # (But it can vary by year. We'll just do an approximate approach.)
        # We will store sums in a dict keyed by (year, week).
        week_sums = {}
        week_counts = {}
        for d, st in date_steps_list:
            # isocalendar() -> (year, weeknum, weekday)
            yw = d.isocalendar()[0:2]  # (ISOyear, ISOweeknumber)
            if yw not in week_sums:
                week_sums[yw] = 0
                week_counts[yw] = 0
            week_sums[yw] += st
            week_counts[yw] += 1
        # Build grouped_data
        for yw in sorted(week_sums.keys()):
            y_val, w_val = yw
            label = f'{y_val}-W{w_val}'
            avg = week_sums[yw] / week_counts[yw]
            grouped_data.append((label, avg))
    else:
        # group_by == 'month'
        # We'll group by (year, month)
        month_sums = {}
        month_counts = {}
        for d, st in date_steps_list:
            ym = (d.year, d.month)
            if ym not in month_sums:
                month_sums[ym] = 0
                month_counts[ym] = 0
            month_sums[ym] += st
            month_counts[ym] += 1
        for ym in sorted(month_sums.keys()):
            y_val, m_val = ym
            label = f'{y_val}-{m_val:02d}'
            avg = month_sums[ym] / month_counts[ym]
            grouped_data.append((label, avg))

    # 6) Prepare data for chart (X labels + Y values)
    #    We'll pass to the template
    chart_labels = [t[0] for t in grouped_data]
    chart_values = [round(t[1], 2) for t in grouped_data]

    # Render template
    return render_template(
        'index.html',
        # Existing:
        month_data=month_data,
        goal=10000,
        selected_year=year,
        selected_month=month,
        month_grid=month_grid,

        # NEW: date range, grouping, chart data
        start_date_str=start_date_str,  # NEW
        end_date_str=end_date_str,      # NEW
        group_by=group_by,              # NEW
        chart_labels=chart_labels,      # NEW
        chart_values=chart_values       # NEW
    )

if __name__ == '__main__':
    app.run(debug=True)