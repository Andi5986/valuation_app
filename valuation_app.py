import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches

def calculate_scaling_factor(examples):
    computed_prices = [0.3 * ebit + 0.7 * revenue for ebit, revenue, _ in examples]
    scale_factors = [price / computed for computed, (_, _, price) in zip(computed_prices, examples)]
    return sum(scale_factors) / len(scale_factors)

def calculate_price(ebit, revenue, scale_factor):
    ebit_percentage = (ebit / revenue) * 100
    if ebit_percentage < 3:
        ebit_weight = 0.9
        revenue_weight = 0.1
    elif ebit_percentage < 5:
        ebit_weight = 0.7
        revenue_weight = 0.3
    elif ebit_percentage < 10:
        ebit_weight = 0.5
        revenue_weight = 0.5
    elif ebit_percentage > 50:
        ebit_weight = 0.05
        revenue_weight = 0.95
    elif ebit_percentage > 40:
        ebit_weight = 0.1
        revenue_weight = 0.9
    elif ebit_percentage > 30:
        ebit_weight = 0.2
        revenue_weight = 0.8
    else:
        ebit_weight = 0.3
        revenue_weight = 0.7
    price = (ebit_weight * ebit + revenue_weight * revenue) * scale_factor
    price = max(300, min(price, 2025))
    return round(price, 2)

def plot_data(ebit, revenue, examples):
    fig, ax = plt.subplots()

    # Set reasonable axis limits
    max_revenue = max([ex[1] for ex in examples] + [revenue]) * 1.1
    max_ebit = max([ex[0] for ex in examples] + [ebit]) * 1.1
    ax.set_xlim(0, max_revenue)
    ax.set_ylim(0, max_ebit)

    # Minimum zone
    min_zone = patches.Rectangle((0, 0), 2200, 220, linewidth=1, edgecolor='red', facecolor='none', hatch='//')
    ax.add_patch(min_zone)

    # Ceiling zone
    ceiling_zone = patches.Rectangle((5300, 0), max_revenue - 5300, max_ebit, linewidth=1, edgecolor='blue', facecolor='none', hatch='//')
    ebit_ceiling_zone = patches.Rectangle((0, 532), max_revenue, max_ebit - 532, linewidth=1, edgecolor='blue', facecolor='none', hatch='//')
    ax.add_patch(ceiling_zone)
    ax.add_patch(ebit_ceiling_zone)
    
    xs, ys, prices = [], [], []
    for ex_ebit, ex_revenue, ex_price in examples:
        data_point = ax.scatter(ex_revenue, ex_ebit, color='blue')
        ax.text(ex_revenue, ex_ebit, f'${round(ex_price, 2)}', fontsize=12, ha='right')
        xs.append(ex_revenue)
        ys.append(ex_ebit)
        prices.append(ex_price)
        ax.plot([0, ex_revenue], [ex_ebit, ex_ebit], 'gray', linestyle=':', alpha=0.5)  # Lines to Revenue axis
        ax.plot([ex_revenue, ex_revenue], [0, ex_ebit], 'gray', linestyle=':', alpha=0.5)  # Lines to EBIT axis

    # Prepare to connect predefined price points
    filtered_xs = [x for x, p in zip(xs, prices) if p in {900, 1350, 2025}]
    filtered_ys = [y for y, p in zip(ys, prices) if p in {900, 1350, 2025}]
    price_line = ax.plot(filtered_xs, filtered_ys, 'green', linestyle='--')[0]

    # Highlight selected point
    selected_point = ax.scatter(revenue, ebit, color='red')
    calculated_price = calculate_price(ebit, revenue, calculate_scaling_factor(examples))
    ax.text(revenue, ebit, f'${calculated_price}', fontsize=12, ha='right')

    # Set labels and title
    ax.set_xlabel('Revenue')
    ax.set_ylabel('EBIT')
    ax.set_title('EBIT vs Revenue with Price Annotations')

    # Adding legend below the chart
    ax.legend(
        [data_point, min_zone, ceiling_zone, price_line, selected_point],
        ['Data Point', 'Minimum Zone', 'Ceiling Zone', 'Price Connection Line', 'Selected Point'],
        loc='upper center', bbox_to_anchor=(0.5, -0.15), fancybox=True, shadow=True, ncol=3
    )

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

            This valuation model calculates the price of a company by considering both EBIT (Earnings Before Interest and Taxes) and Revenue, using dynamic weightings that adjust based on the proportion of EBIT relative to Revenue. This approach ensures that the price reflects the company's operational efficiency and size. 

            The model incorporates scaling factors to adjust these weightings within specified EBIT ranges, enhancing the sensitivity of the model to operational performance. Additionally, the plot visually demarcates 'minimum' and 'ceiling' zones through distinct hatching patterns, indicating predefined thresholds where valuation adjustments become necessary. These visual cues aid in quickly identifying where the input values lie relative to these critical zones.

            Prices are adjusted through a calculated scaling factor that ensures alignment with historical pricing data, maintaining accuracy within established minimum and maximum price thresholds. This controlled range prevents overvaluation or undervaluation based on extreme input values.

            ## Scaling Factor Calculation

            The scaling factor is a critical component of this valuation model. It is computed by comparing known historical prices with prices generated by an initial pricing model based on a set of example data points. Each data point consists of an EBIT, Revenue, and an associated historical price. The scaling factor is then applied uniformly across the pricing calculations to ensure that the model outputs prices that align closely with market realities, thereby improving the reliability and credibility of the model.
            """)

if __name__ == "__main__":
    main()
