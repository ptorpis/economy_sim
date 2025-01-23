import numpy as np
import matplotlib.pyplot as plt
import json

# Initialize variables

class RomerModel():
    def __init__(self):
        with open('../config/config.json', 'r') as file: 
            config = json.load(file)

        A0 = config["A0"]
        L0 = config["L0"]
        self.gamma = config["gamma"]
        self.research_productivity = config["research_productivity"] # How productive is the economy in generating ideas
        self.population_growth = config["population_growth"]
        self.labor_allocation = config["labor_allocation"]
        self.research_labor_allocation = 1 - self.labor_allocation
        self.time_step = config["time_step"] # Quarters
        self.simulation_time = config["simulation_time"] # Years
        self.random_mean = config["random_mean"]
        self.random_std = config["random_std"] # Standard dev of the noise, adjust to control variability
        self.propensity_to_consume = config["propensity_to_consume"]
        self.aggregate_demand = config["aggregate_demand"] # Initial demand shock to the economy
        self.b_bar = config["b_bar"]
        self.inflation_sensitivity = config["inflation_sensitivity"]
        self.cost_shock = config["cost_shock"]
        self.m_policy = config["m_policy"]
        self.inflation_target = config["inflation_target"]
        self.base_job_separation_rate = config["job_separation_rate"]
        self.base_job_finding_rate = config["job_finding_rate"]

        # Initialize arrays and initial values
        self.time = np.arange(0, self.simulation_time, self.time_step)
        self.knowledge_stock = np.zeros(len(self.time))
        self.total_labor = np.zeros(len(self.time))
        self.output = np.zeros(len(self.time))
        self.output_gap = np.zeros(len(self.time))
        self.inflation = np.zeros(len(self.time))

        self.knowledge_stock[0] = A0
        self.total_labor[0] = L0
        self.output_gap[0] = config["initial_output_gap"]
        self.inflation[0] = config["initial_inflation"]

        self.unemployment = np.zeros(len(self.time))
        self.unemployment[0] = config["initial_unemployment_rate"] * L0

        

    def generate_recessions_and_booms(self):
        """
        Interval and durations are treated as quarters.
        """
        recession_interval_min = 6 * 4
        recession_interval_max = 12 * 4
        recession_duration_min = 0.5 * 4
        recession_duration_max = 2 * 4

        boom_interval_min = 3 * 4
        boom_interval_max = 10 * 4
        boom_duration = 3 * 4

        total_steps = self.simulation_time / self.time_step
        recessions = []
        booms = []
        current_time = 0
        
        # Generate Recessions
        while current_time < total_steps: # The time stamps are multiplies by 4 to get the amount of steps, since we are counting in quearters
            current_time += np.random.randint(recession_interval_min, recession_interval_max)
            if current_time < total_steps:
                duration = np.random.randint(recession_duration_min, recession_duration_max)
                recessions.append((current_time, current_time + duration)) # [starting step][end step]
        
        # Create a list of all periods that are recessions
        recession_count = 0
        recession_periods = set()
        for t in range(int(total_steps)):

            if recessions[recession_count][0] <= t <= recessions[recession_count][1]:
                recession_periods.add(t)
                if t == recessions[recession_count][1] and recession_count + 1 != len(recessions):
                    recession_count += 1

        # Generate Booms
        current_time = 0
        while current_time < total_steps:
            boom_start = current_time + np.random.randint(boom_interval_min, boom_interval_max)
            boom_end = boom_start + boom_duration

            while any(boom_start <= recession_end and boom_end >= recession_start for recession_start, recession_end in recessions):
                boom_start += 1
                boom_end = boom_start + boom_duration

            booms.append((boom_start, boom_end))

            current_time = boom_end

        return {
            'recessions': recessions,
            'recession_periods': recession_periods,
            'booms': booms
        }

    
    def simulate_model(self, recessions_and_booms):
        job_separation_rate = self.base_job_separation_rate
        job_finding_rate = self.base_job_finding_rate
        
        for t in range(1, len(self.time)):
            recession_job_dynamics = self.recession_job_market(recessions_and_booms['recessions'], t)
            job_separation_rate = recession_job_dynamics['job_separation_rate']
            job_finding_rate = recession_job_dynamics['job_finding_rate']


            if t not in recessions_and_booms['recession_periods']:
                boom_job_dynamics = self.boom_job_market(recessions_and_booms['booms'], t)
                job_separation_rate = boom_job_dynamics['job_separation_rate']
                job_finding_rate = boom_job_dynamics['job_finding_rate']

            self.total_labor[t] = np.exp(self.population_growth * self.time[t]) - self.unemployment[t - 1]

            self.unemployment[t] = self.total_labor[t] * (job_separation_rate / (job_separation_rate + job_finding_rate))

            self.output_gap[t], self.inflation[t] = self.as_ds(self.output_gap[t - 1], self.inflation[t - 1])
            # Labor allocation
            output_labor = self.labor_allocation * self.total_labor[t]
            research_labor = self.research_labor_allocation * self.total_labor[t]

            # Knowledge stock growth
            d_knowledge = self.research_productivity * self.knowledge_stock[t - 1] * research_labor
            self.knowledge_stock[t] = self.knowledge_stock[t - 1] + d_knowledge * self.time_step

            # Output growth with randomness
            noise = np.random.normal(self.random_mean, self.random_std) # Accounting for everything the model can't capture
            self.output[t] = (self.knowledge_stock[t]**self.gamma) * output_labor * (1 + noise) + (self.output_gap[t] * self.output[t-1])
        
    
    def as_ds(self, Y_tilde, previous_inflation):
        output_gap = (self.aggregate_demand/(1 - self.propensity_to_consume)) - (self.b_bar * self.m_policy / (1 - self.propensity_to_consume)) * (previous_inflation - self.inflation_target)
        inflation = previous_inflation + self.inflation_sensitivity * Y_tilde + self.cost_shock
        
        return output_gap, inflation
    

    def recession_job_market(self, recession_dates, t):
        separation_rate = self.base_job_separation_rate
        finding_rate = self.base_job_finding_rate

        for start, end in recession_dates:
            if start <= t <= end:
                period_in_recession = t - start

                if period_in_recession < 2:
                    separation_rate += np.random.normal(0.05, 0.01)
                    finding_rate -= np.random.normal(0.05, 0.01)
                else:
                    decay_factor = 0.9 ** (period_in_recession - 2)
                    separation_rate += decay_factor * np.random.normal(0.05, 0.01)
                    finding_rate += decay_factor * (self.base_job_finding_rate - finding_rate) + np.random.normal(0.02, 0.005)

                break
        return {
            'job_separation_rate': separation_rate,
            'job_finding_rate': finding_rate
        }
    

    def boom_job_market(self, boom_dates, t):
        separation_rate = self.base_job_separation_rate
        finding_rate = self.base_job_finding_rate

        for start, end in boom_dates:
            if start <= t <= end:
                separation_rate -= np.random.normal(0.02, 0.005)
                finding_rate += np.random.normal(0.03, 0.008)
                break

        return {
            'job_separation_rate': separation_rate,
            'job_finding_rate': finding_rate
        }
      

    def plot(self):
        self.output[0] = self.output[1] # The first element will always be 0 because of the way the loop is set up
        plt.plot(self.output)
        plt.yscale('log')
        plt.title("Output Over Time")
        plt.xlabel("Time")
        plt.ylabel("Output")
        plt.savefig('../plots/output.png')
        plt.show()



if __name__ == "__main__":
    model = RomerModel()
    recessions_and_booms = model.generate_recessions_and_booms()
    model.simulate_model(recessions_and_booms)
    model.plot()