import os
from dotenv import load_dotenv
import pandas as pd
from openai import OpenAI
from feature import query_bayley_scores, query_primary_outcome, query_additional_scores,query_sample_scores
load_dotenv()  
def update_or_append_dataframe(df, new_data, unique_col):
    """Updates or appends rows in the dataframe based on the unique column."""
    if unique_col in df.columns:
        existing_row_idx = df[df[unique_col] == new_data[unique_col]].index
        if not existing_row_idx.empty:
            # If exists, replace the data
            df.loc[existing_row_idx, :] = pd.DataFrame([new_data], index=existing_row_idx)
        else:
            # If not exists, append the new data
            df = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)
    else:
        # First entry case, just append
        df = pd.DataFrame([new_data])
    return df
def setup_environment():
    api_key = os.getenv('OPENAI_API_KEY')
    if api_key is None:
        raise ValueError("API Key is not set in the environment variables")
    os.environ["OPENAI_API_KEY"] = api_key

def read_text_from_file(file_path):
    """Reads text from a file and returns it as a string."""
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

def main():
    setup_environment()
    
    client = OpenAI()
    
    text = read_text_from_file('paper.txt')
    disease = "Hypoxemic-Ischemic Encephalopathy"

    bayley_scores = query_bayley_scores(client, text, disease)
    sample_scores=query_sample_scores(client,text,disease)
    primary_outcome = query_primary_outcome(client, text, disease)
    additional_scores = query_additional_scores(client, text, disease)

    # Extract the parsed data from each result
    all_results = {
        **sample_scores.parsed.model_dump(),
        **primary_outcome.parsed.model_dump(),
        **bayley_scores.parsed.model_dump(),
        **additional_scores.parsed.model_dump()

    }

    # Replace None with 'N/A' for better readability in CSV
    all_results = {k: ('N/A' if v is None else v) for k, v in all_results.items()}

    df_all_results = pd.DataFrame([all_results])
   # Check if the CSV already exists
    csv_file_path = 'study_results.csv'
    if os.path.exists(csv_file_path):
        df_all_results = pd.read_csv(csv_file_path)
    else:
        df_all_results = pd.DataFrame()
    print("Combined Results:")
    print(df_all_results.to_string())

    df_all_results = update_or_append_dataframe(df_all_results, all_results, 'authorandyear')
    print("Results saved to study_results.csv")
    df_all_results.to_csv(csv_file_path, index=False)

if __name__ == "__main__":
    main()