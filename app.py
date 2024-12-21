from flask import Flask, render_template
import csv
from datetime import datetime

app = Flask(__name__)

@app.route('/')
def index():
    # Define the month and year we want to display
    year = 2024
    month = 11
    # Number of days in November 2024 = 30
    days_in_month = 30

    # Read steps data from CSV
    steps_data = {}
    with open('steps_data.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Parse date and steps
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

    return render_template('index.html', month_data=month_data, goal=10000)
    

if __name__ == '__main__':
    app.run(debug=True)
