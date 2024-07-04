import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

class Config:
    def __init__(self):
        self.ebit_values = np.array([220, 350, 550])
        self.revenue_values = np.array([2200, 3500, 5500])
        self.valuation_values = np.array([800, 1350, 2020])
        self.base_price = 800
        self.valuation_ceiling = 2020
        self.ebit_ceiling = 750
        self.revenue_ceiling = 5500
        self.specific_combinations = {(550, 5500): 2020, (350, 3500): 1350, (220, 2200): 800, (0, 0): 750}
        self.ebit_ratio_threshold = 0.09
        self.valuation_multiplier = 3.7

    def generate_linear_relations_table(self):
        rows = [0] + list(self.ebit_values)
        columns = [0] + list(self.revenue_values)
        table = []

        for row in rows:
            row_data = []
            for col in columns:
                value = self.specific_combinations.get((row, col), 0)
                row_data.append(value)
            table.append(row_data)

        linear_relations_data = {'EBIT / Revenue': columns}
        for i, row in enumerate(table):
            linear_relations_data[str(rows[i])] = row

        return pd.DataFrame(linear_relations_data)

class ValuationModel:
    """
    This class handles the valuation calculations based on EBIT and Revenue.
    It uses a linear regression model to calculate the valuation based on given data points.
    """
    def __init__(self, config: Config):
        self.config = config
        self.m_ebit, self.c_ebit = self.calculate_slope_intercept(config.ebit_values, config.valuation_values)
        self.m_revenue, self.c_revenue = self.calculate_slope_intercept(config.revenue_values, config.valuation_values)

    def calculate_slope_intercept(self, x, y):
        n = len(x)
        m = (n * np.sum(x * y) - np.sum(x) * np.sum(y)) / (n * np.sum(x**2) - np.sum(x)**2)
        c = (np.sum(y) - m * np.sum(x)) / n
        return m, c

    def calculate_valuation(self, ebit, revenue):
        # Specific checks for given EBIT and Revenue values
        if (ebit, revenue) in self.config.specific_combinations:
            return self.config.specific_combinations[(ebit, revenue)]
        
        ebit = min(ebit, self.config.ebit_ceiling)  # Apply EBIT ceiling
        revenue = min(revenue, self.config.revenue_ceiling)  # Apply Revenue ceiling
        valuation_ebit = self.m_ebit * ebit + self.c_ebit
        valuation_revenue = self.m_revenue * revenue + self.c_revenue
        valuation = (valuation_ebit + valuation_revenue) / 2

        ebit_ratio = ebit / revenue if revenue != 0 else 0
        if ebit_ratio < self.config.ebit_ratio_threshold:
            valuation = min(valuation, self.config.valuation_multiplier * ebit)
        
        return max(750, int(min(valuation, self.config.valuation_ceiling)))  # Apply floor price and ceiling

    def plot_linear_relationships(self, ebit, revenue, valuation):
        value_slope = np.linspace(0, self.config.ebit_ceiling, 100) 

        revenue_for_ebit_valuation = (self.m_ebit * value_slope + self.c_ebit - self.c_revenue) / self.m_revenue

        plt.figure(figsize=(10, 6))
        plt.plot(revenue_for_ebit_valuation, value_slope, label='Valuation Slope', color='blue')

        plt.scatter(revenue, ebit, color='red', s=100, label=f'Valuation: Revenue = {revenue}, EBIT = {ebit}')

        plt.xlabel('Revenue')
        plt.ylabel('EBIT')
        plt.title('EBIT vs. Revenue: Valuation based on Revenue and EBIT')

        plt.xlim(0, self.config.revenue_ceiling)
        plt.ylim(0, self.config.ebit_ceiling)

        plt.legend()
        plt.grid(True)
        st.pyplot(plt)

class PaymentBreakdown:
    """
    This class handles the payment breakdown calculations.
    It splits the base price and the earnout payments over different time periods.
    """
    def __init__(self, config: Config):
        self.config = config

    def calculate(self, valuation):
        base_payment_t0 = int(self.config.base_price / 2)
        base_payment_t1 = int(self.config.base_price / 2)
        difference = int(valuation - self.config.base_price)
        diff_payment_t1 = difference // 2
        diff_payment_t2 = difference // 2
        return base_payment_t0, base_payment_t1, diff_payment_t1, diff_payment_t2, difference

    def create_dataframe(self, base_payment_t0, base_payment_t1, diff_payment_t1, diff_payment_t2, valuation):
        data = {
            'Item': ['Base price', 'Earnout', 'Total'],
            'T0': [base_payment_t0, 0, base_payment_t0],
            'T1': [base_payment_t1, diff_payment_t1, base_payment_t1 + diff_payment_t1],
            'T2': [0, diff_payment_t2, diff_payment_t2],
            'Total': [self.config.base_price, valuation - self.config.base_price, valuation]
        }
        return pd.DataFrame(data)

def main():
    # Instantiate the config
    config = Config()

    # Generate the linear relations table from specific combinations
    linear_relations_df = config.generate_linear_relations_table()

    # Instantiate the models
    valuation_model = ValuationModel(config)
    payment_breakdown = PaymentBreakdown(config)

    # Streamlit App
    st.title("Earnout Model")

    # Sidebar inputs
    st.sidebar.header("Input Parameters")
    ebit = st.sidebar.number_input("Enter EBIT", min_value=0)
    revenue = st.sidebar.number_input("Enter Revenue", min_value=0)

    # Description of the model
    st.sidebar.markdown("""
    ## Model Description
    This model calculates the valuation based on EBIT and Revenue using linear regression. 
    The values for the linear slope are taken from the Linear Relations Table.
    In case the EBIT is lower than 9% valuation is calculated using EBIT 3.7 multiplier.
    
    The valuation is then used to determine the payment breakdown and buy-back calculations.
    """)

    # Display the linear relations table
    st.write("### Linear Relations Table")
    st.table(linear_relations_df)

    # Calculate button
    if st.sidebar.button("Calculate"):
        # Calculate valuation
        valuation = valuation_model.calculate_valuation(ebit, revenue)

        # Calculate EBIT multiple
        ebit_multiple = round(valuation / ebit, 2) if ebit != 0 else 0

        # Calculate payment breakdown
        base_payment_t0, base_payment_t1, diff_payment_t1, diff_payment_t2, difference = payment_breakdown.calculate(valuation)

        # Create dataframes for displaying results
        payment_df = payment_breakdown.create_dataframe(base_payment_t0, base_payment_t1, diff_payment_t1, diff_payment_t2, valuation)

        # Display the results
        st.write("### Results")
        st.write(f"**Calculated Valuation: {valuation}**")
        st.write(f"**EBIT Ratio: {ebit/revenue:.2%}**" if revenue != 0 else "**EBIT Ratio: 0.00%**")
        st.write(f"**EBIT Multiple: {ebit_multiple}x**")

        st.write("### Payment Breakdown")
        st.table(payment_df.map(lambda x: int(x) if isinstance(x, (int, float)) else x))

        # Display the calculated slope and intercept for both EBIT and Revenue
        st.write("### Linear Relationship for Valuation")
        st.write(f"Slope (EBIT): {round(valuation_model.m_ebit, 2)}")
        st.write(f"Intercept (EBIT): {round(valuation_model.c_ebit, 2)}")
        st.write(f"Slope (Revenue): {round(valuation_model.m_revenue, 2)}")
        st.write(f"Intercept (Revenue): {round(valuation_model.c_revenue, 2)}")

        # Plot the linear relationships
        st.write("### Linear Relationships Plot")
        valuation_model.plot_linear_relationships(ebit, revenue, valuation)

if __name__ == "__main__":
    main()
