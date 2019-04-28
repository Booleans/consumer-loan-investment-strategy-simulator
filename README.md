# Consumer Loan Investment Strategy Simulator

Building a model to predict return on investment (ROI) of consumer loans issued through the company Lending Club. Predictions are used to simulate a historical investment portfolio and analyze performance of the model.

## Table of Contents
1. [Motivation](#motivation)
2. [Product](#product)
3. [Data Sources](#data-sources)
4. [Data Preparation](#data-preparation)
5. [Modeling](#modeling)
6. [Usage](#usage)
7. [Future Work](#future-work)
8. [References](#references)

## Motivation
Consumer loans are a relatively new asset class available for private citizens to invest in. They potentially offer returns similar to traditional investments while offering lower portfolio volatility. However, a significant number of consumer loans are defaulted on by the borrowers. A significant amount of capital can be lost to defaults if a portfolio invests in loans based off of poor criteria. The goal of this project is to construct a model to predict the ROI of a loan in order to determine if it would be a good investment. Once a model is built it can be run through a portfolio simulation of historical loan payment data to analyze how the model's strategy would have performed.


## Data Sources
Please see Lending Club's [statistics page](https://www.lendingclub.com/info/download-data.action) for data on loans that have been issued.Files containing all payments that borrowers have made on their loans can be found at Lending Club's [additional statistics page](https://www.lendingclub.com/company/additional-statistics).

Supplemental data comes from the Federal Reserve Economic Database, [FRED](https://fred.stlouisfed.org/). The supplemental data currently used are the monthly values for the bank prime loan rate ([MPRIME](https://fred.stlouisfed.org/series/MPRIME)), the 30-year fixed rate mortgage average ([MORTGAGE30US](https://fred.stlouisfed.org/series/MORTGAGE30US)), as well as the University of Michigan inflation expectation rate ([MICH](https://fred.stlouisfed.org/series/MICH)).
