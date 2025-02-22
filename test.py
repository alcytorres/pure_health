# ... (rest of the file remains unchanged until after chart_values)

@app.route('/', methods=['GET'])
def index():
    # ... (previous code unchanged: data_type, month/year, CSV reading, calendar, date range, chart data)

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
        # NEW: Pass stats to template
        current_stats=current_stats,
        all_time_stats=all_time_stats
    )

# ... (rest of the file remains unchanged)