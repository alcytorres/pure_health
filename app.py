from flask import Flask, render_template, request
import csv
from datetime import datetime

import calendar  # NEW: needed for day-of-week logic

app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
    # Read month/year from query parameters (default to November 2024)
    year_str = request.args.get('year', '2024')
    month_str = request.args.get('month', '11')
    
    # Convert to integers
    try:
        year = int(year_str)
        month = int(month_str)
    except:
        year = 2024
        month = 11

    # Enforce the allowed range (Jan 2016 - Dec 2024)
    if year < 2016:
        year = 2016
    if year > 2024:
        year = 2024
    if month < 1:
        month = 1
    if month > 12:
        month = 12

    # Compute number of days in the selected month/year
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
        # fallback
        end_date = datetime(year, month, 31)
    days_in_month = (end_date - start_date).days

    # Read steps data from CSV
    steps_data = {}
    with open('steps_data.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                d = datetime.strptime(row['date'], '%Y-%m-%d').date()
                if d.year == year and d.month == month:
                    steps = int(row['steps'])
                    steps_data[d.day] = steps
            except:
                pass

    # For days not in steps_data, assume 0 steps
    month_data = []
    for day in range(1, days_in_month + 1):
        day_steps = steps_data.get(day, 0)
        month_data.append((day, day_steps))

    # NEW: Calculate how many placeholder days to show if the month
    #      doesn't start on Sunday. (Python's Monday=0, Sunday=6.)
    #      We'll shift so that Sunday=0, Monday=1, ..., Saturday=6.
    calendar.setfirstweekday(calendar.SUNDAY)  # NEW
    start_dow_python = start_date.weekday()    # Monday=0, Tuesday=1, ... Sunday=6
    start_dow_sunday = (start_dow_python + 1) % 7  # Sunday=0, Monday=1, etc. # NEW

    # NEW: Build a single list that includes placeholders + real days
    #      Each item is a tuple: (day_number, steps, is_placeholder)
    #      For placeholders, day_number=0, steps=0, is_placeholder=True
    month_grid = []  # NEW

    # NEW: Add placeholders for days before the first day of the month
    for _ in range(start_dow_sunday):
        month_grid.append((0, 0, True))  # day=0 => placeholder

    # NEW: Add actual days
    for day, steps in month_data:
        month_grid.append((day, steps, False))

    return render_template(
        'index.html',
        month_data=month_data,  # existing data (still passed for consistency)
        goal=10000,
        selected_year=year,
        selected_month=month,
        month_grid=month_grid  # NEW: the combined placeholders + real days
    )

if __name__ == '__main__':
    app.run(debug=True)
