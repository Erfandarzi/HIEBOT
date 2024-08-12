import time
import pandas as pd
import re
from env_setup import setup_environment
from db_setup import setup_database
from load_files_to_db import load_files_to_db
from langchain_openai import ChatOpenAI
from langchain_community.agent_toolkits import create_sql_agent
from langchain_community.utilities import SQLDatabase
import os

def time_function(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        return result, end_time - start_time
    return wrapper

@time_function
def setup_env():
    setup_environment()

@time_function
def load_files(db_name, file_path):
    load_files_to_db(db_name, file_path)

@time_function
def setup_db(db_path):
    return setup_database(db_path)

@time_function
def setup_llm_instance(model_name):
    llm = ChatOpenAI(model=model_name, temperature=0)
    return llm

class InvocationCounterDB(SQLDatabase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.invocation_count = 0

    def run(self, *args, **kwargs):
        self.invocation_count += 1
        return super().run(*args, **kwargs)

@time_function
def create_agent(llm, db, agent_type='tool-calling', top_k=10, max_iterations=100, max_execution_time=None):
    counter_db = InvocationCounterDB(engine=db._engine)
    agent = create_sql_agent(llm, db=counter_db, agent_type=agent_type, top_k=top_k, max_iterations=max_iterations, max_execution_time=max_execution_time, verbose=True)
    return agent, counter_db

@time_function
def invoke_agent_(agent_executor):
    response_text = "No response generated"
    sql_query = "No SQL Query Found"
    num_errors = 0

    try:
        response = agent_executor.invoke({
            "input": '''
            Calculate the odds ratio for poor outcomes (defined as MRI score > 2)
            based on cord blood pH levels. Also in your final output print the sql query you have used. Also print the number of errors in execution that was made as #errors:NUM e.g. #errors:3'''
        })
        response_text = str(response)
        sql_query = extract_sql_query(response_text) or "No SQL Query Found"
        num_errors = extract_errors(response_text)
    except Exception as e:
        print(f"An error occurred during agent invocation: {e}")

    return response_text, sql_query, num_errors

def extract_sql_query(response_text):
    match = re.search(r"```sql\s*(.*?)```", response_text, re.DOTALL)
    return match.group(1).strip() if match else None

def extract_errors(response_text):
    matches = list(re.finditer(r"#errors:(\d+)", response_text))
    return int(matches[-1].group(1)) if matches else 0

def run_experiment(options, exp_name, option_name, fixed_model, fixed_agent_type, fixed_top_k, fixed_max_iterations, fixed_max_execution_time, num_runs=1):
    db, _ = setup_db("Chinook.db")
    results = []
    
    for option in options:
        for run in range(num_runs):
            llm, llm_setup_time = setup_llm_instance(option)

            (agent, counter_db), agent_setup_time = create_agent(
                llm, 
                db, 
                agent_type=fixed_agent_type,
                top_k=fixed_top_k,
                max_iterations=fixed_max_iterations,
                max_execution_time=fixed_max_execution_time
            )
            
            (response_text, sql_query, num_errors), execution_time = invoke_agent_(agent)
            
            results.append({
                'Experiment': exp_name,
                'Run': run + 1,
                option_name: option,
                'Model': option,
                'Agent Type': fixed_agent_type,
                'Top K': fixed_top_k,
                'Max Iterations': fixed_max_iterations,
                'Max Execution Time (s)': fixed_max_execution_time,
                'LLM Setup Time (s)': llm_setup_time,
                'Agent Setup Time (s)': agent_setup_time,
                'Execution Time (s)': execution_time,
                'Total Time (s)': llm_setup_time + agent_setup_time + execution_time,
                'Response': response_text,
                'Extracted SQL': sql_query,
                'Number of Errors': num_errors,
                'SQL Query Length': len(sql_query) if sql_query != "No SQL Query Found" else 0,
                'SQL Query Complexity': calculate_sql_complexity(sql_query),
                'Number of DB Invocations': counter_db.invocation_count
            })

    df = pd.DataFrame(results)
    file_path = f'{exp_name}.csv'
    
    # Ensure correct headers
    headers = list(results[0].keys()) if results else []
    
    if not os.path.isfile(file_path):
        df.to_csv(file_path, index=False, columns=headers)
    else:
        # Check if existing file has the correct headers
        existing_df = pd.read_csv(file_path, nrows=0)
        if list(existing_df.columns) != headers:
            # If headers don't match, write a new file with correct headers
            df.to_csv(file_path, index=False, columns=headers)
        else:
            # Append without headers if they already match
            df.to_csv(file_path, mode='a', index=False, header=False)
def calculate_sql_complexity(sql_query):
    if sql_query == "No SQL Query Found":
        return 0
    complexity = 0
    complexity += sql_query.lower().count('join')
    complexity += sql_query.lower().count('where')
    complexity += sql_query.lower().count('group by')
    complexity += sql_query.lower().count('having')
    complexity += sql_query.lower().count('order by')
    complexity += sql_query.count('(')  # Count nested queries
    return complexity

def main():
    models = ['gpt-4o', 'gpt-4o-mini']
    agent_types = ['openai-tools', 'tool-calling']
    top_ks = [10, 50, 100]
    max_iterations = [10, 50, 100]
    max_execution_times = [10, 30,60]

    # Run all experiments
    run_experiment(models, 'llm_comparison', 'Model', models[0], agent_types[0], top_ks[0], max_iterations[0], None)
    # run_experiment(agent_types, 'agent_type_comparison', 'Agent Type', models[0], agent_types[0], top_ks[0], max_iterations[0], None)
    # run_experiment(top_ks, 'top_k_comparison', 'Top K', models[0], agent_types[0], top_ks[0], max_iterations[0], None)
    # run_experiment(max_iterations, 'max_iterations_comparison', 'Max Iterations', models[0], agent_types[0], top_ks[0], max_iterations[0], None)
    # run_experiment(max_execution_times, 'max_execution_time_comparison', 'Max Execution Time', models[0], agent_types[0], top_ks[0], max_iterations[0], None)

if __name__ == "__main__":
    main()