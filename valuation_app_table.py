import streamlit as st
import pandas as pd

class EarnoutModel:
    def __init__(self, examples):
        self.examples = examples
        self.scale_factor = self.calculate_scaling_factor()

    def calculate_scaling_factor(self):
        computed_prices = [0.3 * ebit + 0.7 * revenue for ebit, revenue, _ in self.examples]
        scale_factors = [price / computed for computed, (_, _, price) in zip(computed_prices, self.examples)]
        return sum(scale_factors) / len(scale_factors)

    def calculate_price(self, ebit, revenue):
        ebit_percentage = (ebit / revenue) * 100
        ebit_weight, revenue_weight = self.determine_weights(ebit_percentage)
        base_price = (ebit_weight * ebit + revenue_weight * revenue) * self.scale_factor
        price = self.apply_price_constraints(base_price, ebit, revenue)
        return round(price)

    def apply_price_constraints(self, price, ebit, revenue):
        min_price = max(300, price)  # Ensure that price does not fall below 300
        return max(min(price, 2025), min_price)

    @staticmethod
    def calculate_variation(current, minimum):
        return abs(current - minimum) / minimum

    @staticmethod
    def determine_weights(ebit_percentage):
        if ebit_percentage < 3:
            return 0.9, 0.1
        elif ebit_percentage < 5:
            return 0.7, 0.3
        elif ebit_percentage < 10:
            return 0.5, 0.5
        elif ebit_percentage < 30:
            return 0.3, 0.7
        elif ebit_percentage < 40:
            return 0.2, 0.8
        elif ebit_percentage < 50:
            return 0.1, 0.9
        else:
            return 0.05, 0.95

def main():
    st.title('Earnout Model')
    examples = [(230, 2300, 900), (350, 3500, 1350), (525, 5250, 2025)]
    model = EarnoutModel(examples)
    ebit1 = st.sidebar.number_input("Enter Year 1 EBIT in USD'000:", value=230)
    revenue1 = st.sidebar.number_input("Enter Year 1 Revenue in USD'000:", value=2300)
    ebit2 = st.sidebar.number_input("Enter Year 2 EBIT in USD'000:", value=350)
    revenue2 = st.sidebar.number_input("Enter Year 2 Revenue in USD'000:", value=3500)

    if st.sidebar.button('Calculate Price'):
        price1 = model.calculate_price(ebit1, revenue1)
        price2 = model.calculate_price(ebit2, revenue2)

        initial_payment = 300
        year1_earnout = price1 - initial_payment * 3
        year2_earnout = price2 - price1

        year1_split = round(year1_earnout / 2)
        year1_earnout = round(year1_earnout)
        year2_earnout = round(year2_earnout)

        details = pd.DataFrame({
            'Initial Price': [initial_payment, initial_payment, initial_payment, initial_payment * 3],
            'Earnout Year 1': [0, year1_split, year1_split, year1_split * 2],
            'Earnout Year 2': [0, 0, year2_earnout, year2_earnout],
            'TOTAL': [
                initial_payment, 
                initial_payment + year1_split, 
                initial_payment + year1_split + year2_earnout,
                initial_payment * 3 + year1_earnout + year2_earnout
            ]
        }, index=['Year 0', 'Year 1', 'Year 2', 'Total'])

        st.table(details)

    st.sidebar.markdown(model_description())

def model_description():
    return """
        ## Model Explanation

        The company price is USD'000 900 and the eranout potential is for a valuation of USD'000 2025.
        This valuation model calculates the earnout mechanism by evaluating both 
        EBIT (Earnings Before Interest and Taxes) and Revenue. The model dynamically adjusts the weightings 
        based on the EBIT to Revenue ratio, ensuring the calculated price accurately reflects the company's 
        operational efficiency and scale.
        
        The companyt price of USD'000 900 can decrease if variations to minimum Revenue and EBIT exceed 15% from EBIT USD'000 230
        and Revenue USD'000 2300 respectively. The price will not fall below USD'000 300.

        The model adapts the weightings between EBIT and Revenue within specified EBIT percentage ranges to enhance sensitivity to operational performance fluctuations:
        
        The weightings are adjusted to respond to variations in EBIT as follows:

        - **EBIT less than 3% of Revenue:** EBIT receives a significant focus with a 90% weight, contrasting with Revenue at 10%.
        - **EBIT between 3% and 5% of Revenue:** Weights are adjusted to 70% for EBIT and 30% for Revenue.
        - **EBIT between 5% and 10% of Revenue:** EBIT and Revenue are equally weighted at 50% each.
        - **EBIT between 10% and 30% of Revenue (Normal Range):** EBIT is weighted at 30%, and Revenue at 70%.
        - **EBIT between 30% and 40% of Revenue:** The model shifts emphasis to Revenue with a weighting of 20% for EBIT and 80% for Revenue.
        - **EBIT between 40% and 50% of Revenue:** The weight on EBIT further decreases to 10%, with Revenue at 90%.
        - **EBIT above 50% of Revenue:** EBIT has a minimal weighting of 5%, and Revenue dominates at 95%.

        This mechanism ensures that the model can flexibly and accurately account for varying operational contexts and performance levels.

        ## Price Constraints

        The model sets a maximum price cap of USD'000 2025 to prevent overvaluation. For the minimum price, it is configured to not fall below USD'000 900 unless significant variances (greater than 15%) from the minimum EBIT of USD'000 230 and minimum Revenue of USD'000 2300 are observed. In cases of such significant deviations, the price may be further reduced but will not drop below USD'000 300.

        ## Scaling Factor Calculation

        The scaling factor is a critical component of this valuation model. It is determined by comparing known earnout prices with prices generated by an initial model using a set of example data points. Each data point includes EBIT, Revenue, and an associated earnout price. The scaling factor is applied uniformly across all pricing calculations to ensure that the model's outputs closely align with market realities, thus enhancing the model's reliability and credibility.
    """


if __name__ == '__main__':
    main()
