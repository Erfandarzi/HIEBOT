import os
import pandas as pd
import sqlite3


def load_files_to_db(directory, db_path):
    # Connect to the SQLite database (or create a new one)
    conn = sqlite3.connect(db_path)
    
    # Iterate over all files in the directory
    for filename in os.listdir(directory):
        if filename.endswith('.csv') or filename.endswith('.xlsx'):
            file_path = os.path.join(directory, filename)
            table_name = os.path.splitext(filename)[0]  # Use the filename (without extension) as the table name
            
            # Load the file into a DataFrame based on extension
            if filename.endswith('.csv'):
                df = pd.read_csv(file_path)
            elif filename.endswith('.xlsx'):
                df = pd.read_excel(file_path)
            
            # Drop the problematic column if it exists in DataFrame
            if 'postNormoNeuroExamlevelConsciousness' in df.columns:
                df = df.drop(columns=['postNormoNeuroExamlevelConsciousness', 'postNormoNeuroExamlevelConsciousness:orig'])
            
            # Print to confirm the column is removed
            print(f"Columns after removal: {df.columns}")

            # Convert the DataFrame to a SQL table within the database
            df.to_sql(table_name, conn, if_exists='replace', index=False)
            print(f"Loaded {filename} into {table_name} table.")
    
    # Close the database connection
    conn.close()

# Example usage
# load_files_to_db('Database', 'Chinook.db')