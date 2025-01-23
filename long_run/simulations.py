import lr
import config_gen

def run():
    config_gen.generate_config()
    sim = lr.RomerModel()
    cycles = sim.generate_recessions_and_booms()
    retval = sim.simulate_model(cycles)

    return retval

if __name__ == "__main__":
    run()