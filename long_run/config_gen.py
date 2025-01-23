import lr
import json
import numpy as np

'''
Have a dict that has all the initial input parameters for the simulation

Dump the contents of that data into simconfig.json
'''

def generate_config():
    sim_config = {    
        "A0": 1,
        "L0": 1,
        "gamma": 1,
        "research_productivity": np.random.uniform(0.05, 0.15), # 0.1
        "population_growth": np.random.uniform(0, 0.03), # 0.1
        "labor_allocation": np.random.uniform(0.6, 0.9), # 0.8
        "time_step": 0.25,
        "simulation_time": 100,
        "random_mean": 0,
        "random_std": 0.025,
        "propensity_to_consume": np.random.uniform(0.1, 0.3), # 0.2
        "aggregate_demand": 0.0, # 0.0
        "b_bar": 0.1, # 0.1
        "inflation_sensitivity": 0.5, # 0.5
        "cost_shock": 0.0, # 0.0
        "m_policy": 0.1, # 0.1
        "inflation_target": 0.02,
        "initial_output_gap": 0,
        "initial_inflation": 0.02,
        "job_separation_rate": 0.015,
        "job_finding_rate": 0.40,
        "initial_unemployment_rate": 0.04 # 0.04
    }

    json_path = 'simconfig.json'
    with open(json_path, 'w') as jsonfile:
        json.dump(sim_config, jsonfile, indent=4)


