# Company Valuation App

This Streamlit application calculates the valuation of a company based on EBIT (Earnings Before Interest and Taxes) and Revenue. The app uses dynamic weighting to adjust the influence of EBIT and Revenue based on specific thresholds and applies a scaling factor derived from predefined data to align the computed values with historical prices.

## Features

- Input EBIT and Revenue to compute the company's valuation.
- Dynamic adjustment of weighting based on the percentage of EBIT relative to Revenue.
- Display of calculated valuation and visualization of data points and their interconnections on a chart.
- Explanation of the model and scaling factor calculation included.

## Installation

To run this application, you will need Python and Streamlit. Follow these steps:

1. Clone this repository or download the files.
2. Install the required Python packages:

```bash
pip install -r requirements.txt
```

3. Run the application:

```bash
streamlit run valuation_app.py
```