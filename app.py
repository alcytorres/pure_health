from flask import Flask, render_template, request  # NEW: added request import
import csv
from datetime import datetime

app = Flask(__name__)

@app.route('/', methods=['GET'])  # NEW: specify GET method
def index():
    # NEW: Read month/year from query parameters (default to November 2024)
    year_str = request.args.get('year', '2024')   # NEW
    month_str = request.args.get('month', '11')   # NEW
    
    # NEW: Convert to integers
    try:
        year = int(year_str)
        month = int(month_str)
    except:
        year = 2024
        month = 11

    # Enforce the allowed range (Jan 2016 - Dec 2024)  # NEW
    if year < 2016: 
        year = 2016
    if year > 2024:
        year = 2024
    if month < 1:
        month = 1
    if month > 12:
        month = 12

    # Figure out how many days in the selected month/year
    # For simplicity, handle leap years manually or let datetime do it
    # We'll do a trick: use datetime to compute next month & subtract
    if month == 12:
        next_month = 1
        next_year = year + 1
    else:
        next_month = month + 1
        next_year = year

    # Compute the first day of the current month and next month, then difference
    start_date = datetime(year, month, 1)
    try:
        end_date = datetime(next_year, next_month, 1)
    except:
        # fallback if year was 2024 and month was 12 for some reason
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
    for day in range(1, days_in_month+1):
        day_steps = steps_data.get(day, 0)
        month_data.append((day, day_steps))

    # Pass the current year/month + month_data + possible year/month lists
    # to the template for rendering
    return render_template(
        'index.html',
        month_data=month_data,
        goal=10000,
        selected_year=year,    # NEW
        selected_month=month,  # NEW
    )

if __name__ == '__main__':
    app.run(debug=True)
