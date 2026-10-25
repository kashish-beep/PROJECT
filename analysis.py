
import duckdb

con = duckdb.connect()

# Load cleaned sales data into DuckDB
con.execute("""
    CREATE TABLE sales AS
    SELECT *
    FROM read_csv(
        'cleaned_sales.csv',
        types = {'InvoiceNo': 'VARCHAR'},
        sample_size = -1
    )
""")

# 1. Total revenue
print("\n1. TOTAL REVENUE")
print(con.execute("""
    SELECT ROUND(SUM(Revenue), 2) AS total_revenue
    FROM sales
""").df())

# 2. Monthly revenue with month-over-month growth
print("\n2. MONTHLY REVENUE AND GROWTH")
print(con.execute("""
    WITH monthly_sales AS (
        SELECT
            Month,
            SUM(Revenue) AS revenue
        FROM sales
        GROUP BY Month
    ),
    monthly_comparison AS (
        SELECT
            Month,
            revenue,
            LAG(revenue) OVER (ORDER BY Month) AS previous_month_revenue
        FROM monthly_sales
    )
    SELECT
        Month,
        ROUND(revenue, 2) AS revenue,
        ROUND(previous_month_revenue, 2) AS previous_month_revenue,
        ROUND(revenue - previous_month_revenue, 2) AS revenue_change,
        ROUND(
            100.0 * (revenue - previous_month_revenue)
            / NULLIF(previous_month_revenue, 0),
            2
        ) AS growth_percentage
    FROM monthly_comparison
    ORDER BY Month
""").df())

# 3. Top 10 products by revenue
print("\n3. TOP 10 PRODUCTS")
print(con.execute("""
    SELECT
        Description,
        SUM(Quantity) AS units_sold,
        ROUND(SUM(Revenue), 2) AS total_revenue
    FROM sales
    GROUP BY Description
    ORDER BY total_revenue DESC
    LIMIT 10
""").df())

# 4. Top 10 countries by revenue
print("\n4. TOP 10 COUNTRIES")
print(con.execute("""
    WITH country_sales AS (
        SELECT
            Country,
            SUM(Revenue) AS revenue
        FROM sales
        GROUP BY Country
    )
    SELECT
        Country,
        ROUND(revenue, 2) AS total_revenue,
        ROUND(
            100.0 * revenue / SUM(revenue) OVER (),
            2
        ) AS revenue_contribution_pct
    FROM country_sales
    ORDER BY revenue DESC
    LIMIT 10
""").df())

# 5. Monthly number of orders
print("\n5. MONTHLY ORDERS")
print(con.execute("""
    SELECT
        Month,
        COUNT(DISTINCT InvoiceNo) AS total_orders
    FROM sales
    GROUP BY Month
    ORDER BY Month
""").df())

# 6. Customer purchase behaviour
print("\n6. CUSTOMER PURCHASE BEHAVIOUR")
print(con.execute("""
    WITH customer_summary AS (
        SELECT
            CustomerID,
            COUNT(DISTINCT InvoiceNo) AS total_orders,
            SUM(Quantity) AS units_purchased,
            SUM(Revenue) AS total_revenue
        FROM sales
        WHERE CustomerID IS NOT NULL
        GROUP BY CustomerID
    )
    SELECT
        CASE
            WHEN total_orders > 1 THEN 'Repeat Customer'
            ELSE 'One-Time Customer'
        END AS customer_type,
        COUNT(*) AS number_of_customers,
        ROUND(SUM(total_revenue), 2) AS total_revenue,
        ROUND(AVG(total_revenue), 2) AS average_customer_revenue
    FROM customer_summary
    GROUP BY customer_type
    ORDER BY total_revenue DESC
""").df())


# 7. Top 10 customers and their revenue contribution
print("\n7. TOP 10 CUSTOMERS AND REVENUE CONTRIBUTION")
print(con.execute("""
    WITH customer_sales AS (
        SELECT
            CustomerID,
            COUNT(DISTINCT InvoiceNo) AS total_orders,
            SUM(Revenue) AS revenue
        FROM sales
        WHERE CustomerID IS NOT NULL
        GROUP BY CustomerID
    ),
    ranked_customers AS (
        SELECT
            CustomerID,
            total_orders,
            revenue,
            RANK() OVER (ORDER BY revenue DESC) AS revenue_rank,
            SUM(revenue) OVER () AS all_customer_revenue
        FROM customer_sales
    )
    SELECT
        CustomerID,
        total_orders,
        ROUND(revenue, 2) AS total_revenue,
        revenue_rank,
        ROUND(
            100.0 * revenue / NULLIF(all_customer_revenue, 0),
            2
        ) AS customer_revenue_pct
    FROM ranked_customers
    ORDER BY revenue DESC
    LIMIT 10
""").df())


# 8. Product performance and revenue contribution
print("\n8. PRODUCT PERFORMANCE AND REVENUE CONTRIBUTION")

print(con.execute("""
    WITH product_sales AS (
        SELECT
            Description,
            SUM(Quantity) AS units_sold,
            SUM(Revenue) AS revenue
        FROM sales
        WHERE Description IS NOT NULL
        GROUP BY Description
    ),
    ranked_products AS (
        SELECT
            Description,
            units_sold,
            revenue,
            RANK() OVER (ORDER BY revenue DESC) AS revenue_rank,
            SUM(revenue) OVER () AS total_product_revenue
        FROM product_sales
    )
    SELECT
        Description,
        units_sold,
        ROUND(revenue, 2) AS total_revenue,
        revenue_rank,
        ROUND(
            100.0 * revenue / NULLIF(total_product_revenue, 0),
            2
        ) AS revenue_contribution_pct
    FROM ranked_products
    ORDER BY revenue DESC
    LIMIT 10
""").df())


# 9. Top 10 products' combined revenue contribution
print("\n9. TOP 10 PRODUCTS REVENUE SHARE")

print(con.execute("""
    WITH product_sales AS (
        SELECT
            Description,
            SUM(Revenue) AS revenue
        FROM sales
        WHERE Description IS NOT NULL
        GROUP BY Description
    ),
    ranked_products AS (
        SELECT
            Description,
            revenue,
            ROW_NUMBER() OVER (ORDER BY revenue DESC) AS row_num,
            SUM(revenue) OVER () AS total_product_revenue
        FROM product_sales
    )
    SELECT
        COUNT(*) AS products_in_top_10,
        ROUND(SUM(revenue), 2) AS top_10_revenue,
        ROUND(MAX(total_product_revenue), 2) AS total_product_revenue,
        ROUND(
            100.0 * SUM(revenue) / NULLIF(MAX(total_product_revenue), 0),
            2
        ) AS top_10_revenue_share_pct
    FROM ranked_products
    WHERE row_num <= 10
""").df())


con.close()
