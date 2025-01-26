CREATE TABLE parameters (
    sim_id INTEGER PRIMARY KEY,
    A0 REAL,
    L0 REAL,
    gamma REAL,
    research_productivity REAL,
    population_growth REAL,
    labor_allocation REAL,
    time_step REAL,
    simulation_time REAL,
    random_mean REAL,
    random_std REAL,
    propensity_to_consume REAL,
    aggregate_demand REAL,
    b_bar REAL,
    inflation_sensitivity REAL,
    cost_shock REAL,
    inflation_target REAL,
    initial_output_gap REAL,
    initial_inflation REAL,
    job_separation_rate REAL,
    job_finding_rate REAL,
    initial_unemployment_rate REAL
);

CREATE TABLE results (
    result_id INTEGER PRIMARY KEY AUTOINCREMENT,
    sim_id INTEGER NOT NULL,
    period INTEGER,
    output REAL,
    unemployment REAL,
    knowledge_stock REAL,
    output_gap REAL,
    FOREIGN KEY (sim_id) REFERENCES initial_parameters (sim_id)
    ON DELETE CASCADE
);