# README

# PureHealth App

# Description
PureHealth is a health tracking web application that visualizes personal biomarkers such as steps, sleep, hydration, and calorie intake. Featuring a dynamic calendar view, date range filtering, and statistical insights, it helps users monitor their health goals. The app includes a machine learning model to predict weekly step counts, enhancing user planning with prior, current, and next week forecasts, plus prediction accuracy tracking.

Built with a sleek, user-friendly interface, PureHealth empowers health enthusiasts to stay on top of their wellness journey.

# Getting Started
These instructions will get you a copy of the project up and running on your local machine.

# Prerequisites
Before you begin, ensure you have met the following requirements:
   - Python version: 3.10 or higher
   - Flask version: 2.3.2 or higher
   - Node.js version: v22.2.0 (for JavaScript dependencies)
   - npm: 10.7.0 (for Chart.js)

# Technologies Used
  Backend:
    - Flask (Python web framework)
    - Pandas, Scikit-learn, NumPy (for ML predictions)

  Frontend:
    - HTML/CSS/JavaScript
    - Chart.js (for data visualization)

# Installation
  1. Clone the repository:
       git clone https://github.com/alcytorres/purehealth.git

  2. Navigate to the project directory:
      cd purehealth

  3. Install Python dependencies:
      pip install -r requirements.txt

      - (Note: Create a requirements.txt with flask, pandas, scikit-learn, numpy if not already present.)

  4. Install JavaScript dependencies (for Chart.js):
      npm install

  5. Prepare data files:
      - Place your health data CSVs (e.g., steps_data.csv, sleep_data.csv) in the project root.

      - Format: Columns date (YYYY-MM-DD) and relevant metric (e.g., steps, value).

# To Start the App:
  python3 app.py
  Access at http://localhost:5000.

# Usage
  1. Open the app in your browser.
  2. Navigate between Steps, Sleep, Hydration, and Calories via the dashboard.
  3. Use the calendar to view daily data for a selected month/year.
  4. Filter data by date range and group by day, week, or month.
  5. View stats and, for Steps, see ML-predicted step counts for prior, current, and next weeks.

# Key Features
  - Dynamic Calendar: Visualize daily health metrics with goal progress circles.

  - Date Range Filtering: Analyze data over custom periods with Chart.js graphs.

  - Statistics: Current period and all-time stats (max, min, avg, streaks).

  - ML Step Predictions: Predicts average steps for prior, current, and next weeks using linear regression.

  - Prediction Accuracy: Tracks Mean Absolute Error (MAE) as actual data is imported.

# Additional Configuration
   - Data Import: Manually update CSVs (e.g., steps_data.csv) to include new data for accurate stats and predictions.

   - Prediction Storage: Predictions are saved to step_predictions.csv—ensure write permissions in the project directory.
   
   - Error Handling: The app logs errors to the console; check logs if predictions fail.