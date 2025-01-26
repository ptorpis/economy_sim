import lr
import config_gen
import pandas as pd
import sqlite3

def run():
    config_gen.generate_config()
    sim = lr.RomerModel()
    cycles = sim.generate_recessions_and_booms()
    retval = sim.simulate_model(cycles)

    return retval
    '''
    Data that comes in:
    output
    labor
    unemployment
    knowledge
    output_gap
    config
    '''

def gen_df(iter):
    rows = []
    for i in range(iter):
        data = run()
        param = data['config']
        rows.append(param)

    df_config = pd.DataFrame(rows)
    db = '../data/data.db'

    conn = sqlite3.connect(db)

    df_config.to_sql('parameters', conn, if_exists='replace')
    conn.commit()
    conn.close()



def main():
    gen_df(10000)

main()