import time
import pandas as pd
import re
from env_setup import setup_environment
from db_setup import setup_database
from load_files_to_db import load_files_to_db
from langchain_openai import ChatOpenAI
from langchain_community.agent_toolkits import create_sql_agent

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

@time_function
def create_agent(llm, db, agent_type='tool-calling', top_k=10, max_iterations=100, max_execution_time=None):
    return create_sql_agent(llm, db=db, agent_type=agent_type, top_k=top_k, max_iterations=max_iterations, max_execution_time=max_execution_time, verbose=True)

@time_function
def invoke_agent(agent_executor):
    response = agent_executor.invoke({
        "input": '''
        Calculate the odds ratio for poor outcomes (defined as MRI score > 2)
        based on cord blood pH levels'''
    })
    # Assuming response is a structured object; adapt extraction based on actual response format
    response_text = str(response)  # Convert response to string if necessary
    sql_query = extract_sql_query(response_text)
    return response_text, sql_query

def extract_sql_query(response_text):
    match = re.search(r"(SELECT .*?;)", response_text, re.S)
    if match:
        return match.group(1)
    return "No SQL Query Found"

def run_experiment(options, exp_name, option_name, fixed_model, fixed_agent_type, fixed_top_k, fixed_max_iterations, fixed_max_execution_time):
    db, _ = setup_db("Chinook.db")
    results = []
    for option in options:
        max_execution = fixed_max_execution_time if exp_name != 'max_execution_time_comparison' else option
        if exp_name == 'llm_comparison':
            llm, _ = setup_llm_instance(option)
        else:
            llm, _ = setup_llm_instance(fixed_model)

        agent, _ = create_agent(llm, db, agent_type=fixed_agent_type if exp_name != 'agent_type_comparison' else option,
                                top_k=fixed_top_k if exp_name != 'top_k_comparison' else option,
                                max_iterations=fixed_max_iterations if exp_name != 'max_iterations_comparison' else option,
                                max_execution_time=max_execution)
        response_text, sql_query = invoke_agent(agent)
        results.append({
            option_name: option,
            'Max Execution Time (s)': max_execution,
            'Response': response_text,
            'Extracted SQL': sql_query
        })

    df = pd.DataFrame(results)
    df.to_csv(f'{exp_name}.csv', index=False)

 

def main():
    models = ['gpt-4o', 'gpt-4o-mini']
    agent_types = ['openai-tools', 'tool-calling']
    top_ks = [10, 50, 100]
    max_iterations = [10, 50, 100]
    max_execution_times = [10, 20, 30]

    # Run LLM comparison experiment
    run_experiment(models, 'llm_comparison', 'Model', models[0], agent_types[0], top_ks[0], max_iterations[0], None)
    # Additional experiments can be uncommented as needed
    # run_experiment(agent_types, 'agent_type_comparison', 'Agent Type', models[0], agent_types[0], top_ks[0], max_iterations[0], None)
    # run_experiment(top_ks, 'top_k_comparison', 'Top K', models[0], agent_types[0], top_ks[0], max_iterations[0], None)
    # run_experiment(max_iterations, 'max_iterations_comparison', 'Max Iterations', models[0], agent_types[0], top_ks[0], max_iterations[0], None)
    # run_experiment(max_execution_times, 'max_execution_time_comparison', 'Max Execution Time', models[0], agent_types[0], top_ks[0], max_iterations[0], None)

if __name__ == "__main__":
    main()
