import pandas as pd

# Load your data from CSV files
df_main = pd.read_csv('Database/01-main.csv')
df_mri = pd.read_csv('Database/08-1-mri-overall.csv')
# Assuming 'subjectID' is a common identifier between the tables
# Rename columns in df_mri that end with '_x' or '_y'
df_mri.rename(columns={col: col.replace('_x', '_mri') for col in df_mri.columns if col.endswith('_x')}, inplace=True)
df_mri.rename(columns={col: col.replace('_y', '_mri') for col in df_mri.columns if col.endswith('_y')}, inplace=True)

# Now perform the merge
df = pd.merge(df_main, df_mri, on='subjectID', how='inner', suffixes=('_main', '_mri'))


columns_of_interest = [
    'APGAR5min', 'APGAR10min', 'MRIScore', 'cordBloodGasPH', 
    'birthGestationalAgeWeek', 'motherAgeYear', 'infantSex', 
    'birthWeight', 'motherEducation', 'screenSeizure'
]

# Select these columns from the merged DataFrame
df_selected = df[columns_of_interest]

# # Add missing columns with NaNs or default values
# df_selected['HouseholdIncome'] = pd.NA  # Assuming no data available
# df_selected['BayleyScores'] = pd.NA    # Placeholder for actual data if available later
# df_selected['Outcome'] = pd.NA         # Placeholder for actual data if available later

df_selected.to_csv('reduced_dataset.csv', index=False)
