import pandas as pd
import matplotlib.pyplot as plt

# Load the CSV file (replace 'steps_data.csv' with your actual filename)
df = pd.read_csv('steps_data.csv')

# Convert date column to datetime
df['date'] = pd.to_datetime(df['date'])

# Sort by date
df = df.sort_values('date')

# Basic stats
print("Basic stats on steps:")
print(df['steps'].describe())

# Plot daily steps over time
plt.figure(figsize=(10, 5))
plt.plot(df['date'], df['steps'], marker='o', linestyle='-')
plt.title('Daily Steps Over Time')
plt.xlabel('Date')
plt.ylabel('Steps')
plt.grid(True)
plt.tight_layout()
plt.show()
