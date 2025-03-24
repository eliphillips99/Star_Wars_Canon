import pandas as pd

# Load the CSV file into a DataFrame
df = pd.read_csv('C:\\Users\\eligp\\OneDrive\\Documents\\Coding Projects\\Star_Wars_Canon\\data\\Timeline.csv')

# Iterate through the "Full Summary" column
for summary in df['Full Summary']:
    # Process each summary
    print(summary)