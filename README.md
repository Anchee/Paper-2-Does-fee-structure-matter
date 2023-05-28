# Paper-2-Does-fee-structure-matter
Second project in PhD

This repository contains a Python script that performs various metrics on financial data stored in a CSV file. The script utilizes the pandas, numpy, and matplotlib libraries for data manipulation, calculations, and visualization. The main purpose of the script is to analyze trading data and calculate different metrics related to trading fees, spreads, and trade direction.

## Prerequisites
Python 3.x
pandas
numpy
matplotlib
Usage
Make sure you have Python 3.x installed on your system.

## Install the required libraries by running the following command:
pip install pandas numpy matplotlib
Save your financial data in a CSV file.
Modify the filename variable in the code to specify the path to your CSV file.

## Run the script with the following command:
python script.py

## Metrics Calculated
The script performs the following metrics on the financial data:

# Data preprocessing:

Parsing the CSV file and extracting relevant columns.
Parsing and converting the timestamp column to the appropriate datetime format.
Filtering out irrelevant rows.
Fee-related metrics:

Calculating fee differences based on the value of trades.
Analyzing fee changes, increases, decreases, and unchanged fees.
Calculating fee averages per stock.
Spread-related metrics:

Calculating quoted spreads based on bid and ask prices.
Analyzing quoted spreads in basis points.
Calculating effective spreads based on trade prices and midquotes.
Analyzing effective spreads in basis points.
Calculating value-weighted effective spreads and spreads in basis points.
Other metrics:

Analyzing trade direction (buy/sell).
Analyzing trading issues based on trade prices and bid/ask prices.
Analyzing quote lifetimes.
Analyzing trade sizes.
Realized spread:

Calculating realized spreads based on trade prices and midquotes.
Analyzing realized spreads in basis points.

## Customization
The script currently assumes that the financial data is stored in a CSV file. If your data is in a different format, you will need to modify the code accordingly.
You can customize the file path and name in the filename variable to match your data file location.
Additional metrics or modifications to existing metrics can be added to the script as per your requirements.
