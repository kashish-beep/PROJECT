# E-commerce Sales Analysis Dashboard

An interactive sales analytics dashboard built using **Python, SQL, Pandas, DuckDB, Streamlit, Plotly, and Matplotlib** to explore transaction data, identify revenue trends, and generate actionable business insights.

## Project Overview

This project analyzes e-commerce transactions to understand sales performance across time periods, products, countries, and customers. It combines data cleaning, SQL-based analysis, and interactive visualizations to support data-driven decision-making.

## Business Questions

- How does revenue change month over month?
- Which products generate the most revenue?
- Which countries contribute the most to sales?
- How do repeat customers compare with one-time customers?
- Which periods show the strongest revenue growth?

## Tools and Technologies

- **Python:** Data processing and analysis
- **Pandas:** Data cleaning and aggregation
- **DuckDB SQL:** Analytical queries and data exploration
- **Streamlit:** Interactive dashboard
- **Plotly and Matplotlib:** Data visualization

## SQL Skills Demonstrated

- Common Table Expressions (CTEs)
- Window functions
- `LAG()` for month-over-month comparisons
- `RANK()` and `ROW_NUMBER()` for ranking
- `CASE WHEN` for customer segmentation
- Aggregations, filtering, and revenue contribution calculations

## Dashboard Features

- Key performance indicators (KPIs)
- Country and date filters
- Monthly revenue and growth analysis
- Top-performing products and countries
- Customer purchase behaviour and segmentation
- SQL-powered analysis tables
- Actionable business insights

## Data Preparation

The raw transaction data was cleaned before analysis. The process includes removing duplicate records, handling missing product descriptions, excluding cancellations and non-positive quantities or prices, and calculating revenue as quantity multiplied by unit price.

Customer-level analysis excludes records with missing customer IDs where customer identification is required.

## Run Locally

1. Clone this repository.
2. Create and activate a Python virtual environment.
3. Install the required dependencies.
4. Ensure `cleaned_sales.csv` is available in the project directory.
5. Run the dashboard.

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Business Value

The dashboard helps identify revenue patterns, high-performing products, important markets, and customer purchasing behaviour. These findings can guide further investigation into inventory planning, marketing strategy, and customer retention.

## Limitations

The analysis reflects only the transactions available in the selected dataset and the cleaning rules applied. Revenue figures represent retained transaction line-item sales, not net revenue after returns or other accounting adjustments.
