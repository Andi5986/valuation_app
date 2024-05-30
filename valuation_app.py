import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

def calculate_scaling_factor(examples):
    computed_prices = [0.3 * ebit + 0.7 * revenue for ebit, revenue, _ in examples]
    scale_factors = [price / computed for computed, (_, _, price) in zip(computed_prices, examples)]
    return sum(scale_factors) / len(scale_factors)

def calculate_price(ebit, revenue, scale_factor):
    ebit_percentage = (ebit / revenue) * 100
    if ebit_percentage < 10:
        ebit_weight = 0.7
        revenue_weight = 0.3
    elif ebit_percentage > 40:
        ebit_weight = 0.1
        revenue_weight = 0.9
    else:
        ebit_weight = 0.3
        revenue_weight = 0.7
    price = (ebit_weight * ebit + revenue_weight * revenue) * scale_factor
    price = max(300, min(price, 2025))
    return round(price, 2)

def plot_data(ebit, revenue, examples):
    fig, ax = plt.subplots()
    # Collect coordinates for lines
    xs, ys = [], []

    # Plot predefined points
    for ex_ebit, ex_revenue, ex_price in examples:
        ax.scatter(ex_revenue, ex_ebit, color='blue')  # Revenue as x, EBIT as y
        ax.text(ex_revenue, ex_ebit, f'${round(ex_price, 2)}', fontsize=12, ha='right')
        xs.append(ex_revenue)
        ys.append(ex_ebit)

    # Draw lines between predefined points
    ax.plot(xs, ys, 'b--')  # Blue dashed line
    
    # Highlight selected point
    ax.scatter(revenue, ebit, color='red')
    calculated_price = calculate_price(ebit, revenue, calculate_scaling_factor(examples))
    ax.text(revenue, ebit, f'${calculated_price}', fontsize=12, ha='right')
    ax.set_xlabel('Revenue')
    ax.set_ylabel('EBIT')
    ax.set_title('EBIT vs Revenue with Price Annotations')
    st.pyplot(fig)

def main():
    st.title('Company Valuation App')

    examples = [(230, 2300, 900), (350, 3500, 1350), (525, 5250, 2025)]
    scale_factor = calculate_scaling_factor(examples)

    st.sidebar.header('Input Parameters')
    ebit = st.sidebar.number_input('Enter EBIT:', value=230)
    revenue = st.sidebar.number_input('Enter Revenue:', value=2300)

    if st.sidebar.button('Calculate Price'):
        price = calculate_price(ebit, revenue, scale_factor)
        st.write(f"Calculated Company Price: ${price:.2f}")
        plot_data(ebit, revenue, examples)

    st.sidebar.markdown("""
## Model Explanation

The price of the company is calculated based on EBIT and Revenue with dynamic weighting:
- **Base weights**: EBIT (30%) and Revenue (70%).
- If EBIT is less than 10% of Revenue, the weights shift to EBIT (70%) and Revenue (30%).
- If EBIT is more than 40% of Revenue, the weights shift to EBIT (10%) and Revenue (90%).

Prices are adjusted by a scaling factor, calculated from predefined example data, to align with historical valuations. The computed prices are constrained to a minimum of 300 and a maximum of 2025. The chart displays the relationship between EBIT and Revenue, highlighting the selected values and the calculated price at their intersection, connected by dashed lines.

## Scaling Factor Calculation

The **scaling factor** is used to align the computed prices from the model with pre-determine prices 900, 1350 and 2025. It's computed as follows:
1. Compute the prices for a set of data points using a preliminary pricing model.
2. Compare these computed prices to actual known prices for the same data points.
3. Calculate the scaling factor as the average ratio of known prices to computed prices.

Given a set of example data points where each includes EBIT, Revenue, and a known historical price, the formula to calculate the scaling factor \(S\) is:

S = (1/N) * sum((P_i / C_i) for i = 1 to N)

Where:
- N is the number of example data points.
- P_i is the known price (actual price) for the i-th data point.
- C_i is the computed price for the i-th data point using the initial pricing model formula, which in this case is (0.3 * EBIT + 0.7 * Revenue).

This method ensures that the model's output is adjusted to better match real-world pricing scenarios, enhancing its accuracy and reliability.
""")



if __name__ == "__main__":
    main()
