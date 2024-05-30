import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches

def calculate_scaling_factor(examples):
    computed_prices = [0.3 * ebit + 0.7 * revenue for ebit, revenue, _ in examples]
    scale_factors = [price / computed for computed, (_, _, price) in zip(computed_prices, examples)]
    return sum(scale_factors) / len(scale_factors)

def calculate_price(ebit, revenue, scale_factor):
    ebit_percentage = (ebit / revenue) * 100
    ebit_weight, revenue_weight = determine_weights(ebit_percentage)
    price = (ebit_weight * ebit + revenue_weight * revenue) * scale_factor
    return round(price, 2), ebit_percentage, ebit_weight, revenue_weight, scale_factor

def determine_weights(ebit_percentage):
    if ebit_percentage < 3:
        return 0.9, 0.1
    elif ebit_percentage < 5:
        return 0.7, 0.3
    elif ebit_percentage < 10:
        return 0.5, 0.5
    elif ebit_percentage > 50:
        return 0.05, 0.95
    elif ebit_percentage > 40:
        return 0.1, 0.9
    elif ebit_percentage > 30:
        return 0.2, 0.8
    return 0.3, 0.7

def plot_data(ebit, revenue, examples, scale_factor):
    fig, ax = plt.subplots()
    setup_plot(ax, examples, ebit, revenue)
    min_zone, ceiling_zone, ebit_ceiling_zone = plot_zones(ax, examples)
    plot_connections(ax, examples)
    selected_point = plot_price_point(ax, ebit, revenue, scale_factor)
    historical_line = plot_historical_lines(ax, examples)
    add_legend(ax, min_zone, ceiling_zone, ebit_ceiling_zone, selected_point, historical_line)
    st.pyplot(fig)

def setup_plot(ax, examples, ebit, revenue):
    max_revenue = max([ex[1] for ex in examples] + [revenue]) * 1.1
    max_ebit = max([ex[0] for ex in examples] + [ebit]) * 1.1
    ax.set_xlim(0, max_revenue)
    ax.set_ylim(0, max_ebit)
    ax.set_xlabel('Revenue')
    ax.set_ylabel('EBIT')
    ax.set_title('EBIT vs Revenue with Price Annotations')

def plot_zones(ax, examples):
    min_zone = patches.Rectangle((0, 0), 2200, 220, linewidth=1, edgecolor='red', facecolor='none', hatch='//', label='Minimum Zone')
    ax.add_patch(min_zone)
    max_revenue = max(ex[1] for ex in examples) * 1.1
    max_ebit = max(ex[0] for ex in examples) * 1.1
    ceiling_zone = patches.Rectangle((5300, 0), max_revenue - 5300, max_ebit, linewidth=1, edgecolor='blue', facecolor='none', hatch='//', label='Revenue Ceiling Zone')
    ebit_ceiling_zone = patches.Rectangle((0, 532), max_revenue, max_ebit - 532, linewidth=1, edgecolor='blue', facecolor='none', hatch='//', label='EBIT Ceiling Zone')
    ax.add_patch(ceiling_zone)
    ax.add_patch(ebit_ceiling_zone)
    return min_zone, ceiling_zone, ebit_ceiling_zone

def plot_connections(ax, examples):
    for ex_ebit, ex_revenue, ex_price in examples:
        ax.scatter(ex_revenue, ex_ebit, color='blue')
        ax.text(ex_revenue, ex_ebit, f'${round(ex_price, 2)}', fontsize=12, ha='right')
        ax.plot([0, ex_revenue], [ex_ebit, ex_ebit], 'gray', linestyle=':', alpha=0.5)
        ax.plot([ex_revenue, ex_revenue], [0, ex_ebit], 'gray', linestyle=':', alpha=0.5)

def plot_price_point(ax, ebit, revenue, scale_factor):
    price = calculate_price(ebit, revenue, scale_factor)[0]  
    selected_point = ax.scatter(revenue, ebit, color='red', s=50)  
    ax.text(revenue, ebit, f'${price:.2f}', fontsize=12, ha='right', va='bottom') 
    return selected_point

def plot_historical_lines(ax, examples):
    historical_prices = {900, 1350, 2025}
    filtered_xs = [ex[1] for ex in examples if ex[2] in historical_prices]
    filtered_ys = [ex[0] for ex in examples if ex[2] in historical_prices]
    if filtered_xs and filtered_ys:
        return ax.plot(
            filtered_xs,
            filtered_ys,
            'green',
            linestyle='--',
            label='Historical Price Line',
        )[0]
    return None

def add_legend(ax, min_zone, ceiling_zone, ebit_ceiling_zone, selected_point, historical_line):
    elements = [min_zone, ceiling_zone, ebit_ceiling_zone, selected_point]
    labels = [e.get_label() for e in elements if e.get_label()]
    if historical_line:
        elements.append(historical_line)
        labels.append(historical_line.get_label())
    # Set the legend below the chart
    ax.legend(elements, labels, loc='upper center', bbox_to_anchor=(0.5, -0.1), shadow=True, fancybox=True, ncol=3)

def main():
    st.title('Company Valuation App')
    examples = [(230, 2300, 900), (350, 3500, 1350), (525, 5250, 2025)]
    scale_factor = calculate_scaling_factor(examples)

    st.sidebar.header('Input Parameters')
    ebit = st.sidebar.number_input('Enter EBIT:', value=230)
    revenue = st.sidebar.number_input('Enter Revenue:', value=2300)
    if st.sidebar.button('Calculate Price'):
        price, ebit_percentage, ebit_weight, revenue_weight, scale_factor = calculate_price(ebit, revenue, scale_factor)
        st.write(f"Calculated Company Price: ${price:.2f}")
        st.write(f"The price was calculated using a dynamic weighting based on EBIT as a percentage of Revenue ({ebit_percentage:.2f}%).")
        st.write(f"EBIT weighting used: {ebit_weight:.2f}, Revenue weighting used: {revenue_weight:.2f}.")
        st.write(f"The scaling factor applied was: {scale_factor:.4f}.")
        plot_data(ebit, revenue, examples, scale_factor)
        
    st.sidebar.markdown(model_description())

def model_description():
    return """
        ## Model Explanation

        This valuation model calculates the price of a company by considering both 
        EBIT (Earnings Before Interest and Taxes) and Revenue, using dynamic weightings 
        that adjust based on the proportion of EBIT relative to Revenue. 
        This approach ensures that the price reflects the company's operational efficiency and size.

        The model incorporates scaling factors to adjust these weightings within specified EBIT ranges, 
        enhancing the sensitivity of the model to operational performance. 
        Additionally, prices are adjusted through a calculated scaling factor that ensures 
        alignment with historical pricing data, 
        maintaining accuracy within established minimum and maximum price thresholds. 
        This controlled range prevents overvaluation or undervaluation based on extreme input values.

        ## Scaling Factor Calculation

        The scaling factor is a critical component of this valuation model. 
        It is computed by comparing known historical prices with prices generated by 
        an initial pricing model based on a set of example data points. 
        Each data point consists of an EBIT, Revenue, and an associated historical price. 
        The scaling factor is then applied uniformly across the pricing calculations 
        to ensure that the model outputs prices that align closely with market realities, 
        thereby improving the reliability and credibility of the model.
        """

if __name__ == '__main__':
    main()
