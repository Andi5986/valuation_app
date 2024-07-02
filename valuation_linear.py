import streamlit as st
import numpy as np
import pandas as pd

class ValuationModel:
    """
    This class handles the valuation calculations based on EBIT and Revenue.
    It uses a linear regression model to calculate the valuation based on given data points.
    """
    def __init__(self, ebit_values, revenue_values, valuation_values, seller_income=220, base_price=800, valuation_ceiling=2020, ebit_ceiling=750, revenue_ceiling=5500):
        self.ebit_values = ebit_values
        self.revenue_values = revenue_values
        self.valuation_values = valuation_values
        self.seller_income = seller_income
        self.base_price = base_price
        self.valuation_ceiling = valuation_ceiling
        self.ebit_ceiling = ebit_ceiling
        self.revenue_ceiling = revenue_ceiling
        self.m_ebit, self.c_ebit = self.calculate_slope_intercept(ebit_values, valuation_values)
        self.m_revenue, self.c_revenue = self.calculate_slope_intercept(revenue_values, valuation_values)

    def calculate_slope_intercept(self, x, y):
        n = len(x)
        m = (n * np.sum(x * y) - np.sum(x) * np.sum(y)) / (n * np.sum(x**2) - np.sum(x)**2)
        c = (np.sum(y) - m * np.sum(x)) / n
        return m, c

    def calculate_valuation(self, ebit, revenue):
        ebit = min(ebit, self.ebit_ceiling)  # Apply EBIT ceiling
        revenue = min(revenue, self.revenue_ceiling)  # Apply Revenue ceiling
        valuation_ebit = self.m_ebit * ebit + self.c_ebit
        valuation_revenue = self.m_revenue * revenue + self.c_revenue
        valuation = (valuation_ebit + valuation_revenue) / 2
        return int(min(valuation, self.valuation_ceiling))  # Apply value ceiling and convert to integer

class PaymentBreakdown:
    """
    This class handles the payment breakdown calculations.
    It splits the base price and the earnout payments over different time periods.
    """
    def __init__(self, base_price):
        self.base_price = base_price

    def calculate(self, valuation):
        base_payment_t0 = int(self.base_price / 2)
        base_payment_t1 = int(self.base_price / 2)
        difference = int(valuation - self.base_price)
        diff_payment_t1 = int(difference / 2)
        diff_payment_t2 = int(difference / 2)
        return base_payment_t0, base_payment_t1, diff_payment_t1, diff_payment_t2, difference

    def create_dataframe(self, base_payment_t0, base_payment_t1, diff_payment_t1, diff_payment_t2, valuation):
        data = {
            'Item': ['Base price', 'Earnout', 'Total'],
            'T0': [base_payment_t0, 0, base_payment_t0],
            'T1': [base_payment_t1, diff_payment_t1, base_payment_t1 + diff_payment_t1],
            'T2': [0, diff_payment_t2, diff_payment_t2],
            'Total': [self.base_price, valuation - self.base_price, valuation]
        }
        return pd.DataFrame(data)

class BuyBackTable:
    """
    This class handles the creation of the buy-back table.
    It calculates the earnings, payments, and differences over different time periods.
    """
    def __init__(self, ebit, seller_income):
        self.ebit = ebit
        self.seller_income = seller_income

    def create_dataframe(self, payment_df):
        earnings_t0 = 0
        earnings_t1 = self.ebit
        earnings_t2 = self.ebit + self.seller_income
        earnings_t3 = earnings_t2

        payments = payment_df.iloc[2, 1:4].values  # Take the 'Total' row from payment_df, exclude T3

        earnings = [earnings_t0, earnings_t1, earnings_t2, earnings_t3]
        difference = [earnings[i] - payments[i] if i < len(payments) else earnings[i] for i in range(4)]
        
        cumulative_earnings = np.cumsum(earnings)
        cumulative_payments = np.cumsum(np.append(payments, 0))  # Add 0 for T3 payment
        cumulative_difference = np.cumsum(difference)

        data = {
            'Item': ['Earnings', 'Payments', 'Difference', 'Cumulative Earnings', 'Cumulative Payments', 'Cumulative Difference'],
            'T0': [earnings_t0, payments[0], difference[0], cumulative_earnings[0], cumulative_payments[0], cumulative_difference[0]],
            'T1': [earnings_t1, payments[1], difference[1], cumulative_earnings[1], cumulative_payments[1], cumulative_difference[1]],
            'T2': [earnings_t2, payments[2], difference[2], cumulative_earnings[2], cumulative_payments[2], cumulative_difference[2]],
            'T3': [earnings_t3, 0, difference[3], cumulative_earnings[3], cumulative_payments[3], cumulative_difference[3]]
        }
        return pd.DataFrame(data)

def main():
    # Input values and constants
    ebit_values = np.array([220, 350, 550])
    revenue_values = np.array([2200, 3500, 5500])
    valuation_values = np.array([800, 1350, 2020])
    seller_income = 220
    base_price = 800
    valuation_ceiling = 2020
    ebit_ceiling = 750
    revenue_ceiling = 5500

    # Instantiate the models
    valuation_model = ValuationModel(ebit_values, revenue_values, valuation_values, seller_income, base_price, valuation_ceiling, ebit_ceiling, revenue_ceiling)
    payment_breakdown = PaymentBreakdown(base_price)

    # Streamlit App
    st.title("Earnout Model")

    # Sidebar inputs
    st.sidebar.header("Input Parameters")
    ebit = st.sidebar.number_input("Enter EBIT", min_value=0)
    revenue = st.sidebar.number_input("Enter Revenue", min_value=0)

    # Description of the model
    st.sidebar.markdown(f"""
    ## Model Description
    This model calculates the valuation based on EBIT and Revenue using linear regression from the following data points
    Revenue: {revenue_values}, EBIT: {ebit_values} and interspecting this valuation: {valuation_values}.
    
    The valuation is then used to determine the payment breakdown and buy-back calculations.
    """)

    # Calculate button
    if st.sidebar.button("Calculate"):
        # Calculate valuation
        valuation = valuation_model.calculate_valuation(ebit, revenue)

        # Calculate EBIT multiple
        ebit_multiple = round(valuation / ebit, 2) if ebit != 0 else 0

        # Calculate SDI
        sdi = round(valuation / (ebit + seller_income), 2) if (ebit + seller_income) != 0 else 0

        # Calculate payment breakdown
        base_payment_t0, base_payment_t1, diff_payment_t1, diff_payment_t2, difference = payment_breakdown.calculate(valuation)

        # Create dataframes for displaying results
        payment_df = payment_breakdown.create_dataframe(base_payment_t0, base_payment_t1, diff_payment_t1, diff_payment_t2, valuation)
        buy_back_table = BuyBackTable(ebit, seller_income)
        buy_back_df = buy_back_table.create_dataframe(payment_df)

        # Display the results
        st.write(f"EBIT: {ebit}")
        st.write(f"Revenue: {revenue}")
        st.write(f"Calculated Valuation: {valuation}")
        st.write(f"**EBIT Multiple: {ebit_multiple}**")
        st.write(f"**SDI: {sdi}**")

        st.write("### Payment Breakdown")
        st.table(payment_df.applymap(lambda x: int(x) if isinstance(x, (int, float)) else x))

        st.write("### Buy-Back Table")
        st.table(buy_back_df.applymap(lambda x: int(x) if isinstance(x, (int, float)) else x))

        # Display the calculated slope and intercept for both EBIT and Revenue
        st.write("### Linear Relationship for Valuation")
        st.write(f"Slope (EBIT): {round(valuation_model.m_ebit, 2)}")
        st.write(f"Intercept (EBIT): {round(valuation_model.c_ebit, 2)}")
        st.write(f"Slope (Revenue): {round(valuation_model.m_revenue, 2)}")
        st.write(f"Intercept (Revenue): {round(valuation_model.c_revenue, 2)}")

if __name__ == "__main__":
    main()
