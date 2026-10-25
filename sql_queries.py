
import duckdb


def run_query(query, params=None):
    con = duckdb.connect()

    try:
        con.execute("""
            CREATE VIEW sales AS
            SELECT *
            FROM read_csv(
                'cleaned_sales.csv',
                types = {'InvoiceNo': 'VARCHAR'},
                sample_size = -1
            )
        """)

        return con.execute(query, params or []).df()

    finally:
        con.close()


def get_monthly_growth(country="All", start_date=None, end_date=None):
    query = """
        WITH filtered_sales AS (
            SELECT *
            FROM sales
            WHERE CAST(InvoiceDate AS DATE) BETWEEN ? AND ?
              AND (? = 'All' OR Country = ?)
        ),
        monthly_sales AS (
            SELECT Month, SUM(Revenue) AS revenue
            FROM filtered_sales
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
    """

    return run_query(
        query,
        [start_date, end_date, country, country]
    )


def get_customer_segments(country="All", start_date=None, end_date=None):
    query = """
        WITH filtered_sales AS (
            SELECT *
            FROM sales
            WHERE CAST(InvoiceDate AS DATE) BETWEEN ? AND ?
              AND (? = 'All' OR Country = ?)
        ),
        customer_summary AS (
            SELECT
                CustomerID,
                COUNT(DISTINCT InvoiceNo) AS total_orders,
                SUM(Revenue) AS total_revenue
            FROM filtered_sales
            WHERE CustomerID IS NOT NULL
            GROUP BY CustomerID
        )
        SELECT
            CASE
                WHEN total_orders > 1 THEN 'Repeat Customer'
                ELSE 'One-Time Customer'
            END AS customer_type,
            COUNT(*) AS number_of_customers,
            ROUND(SUM(total_revenue), 2) AS total_revenue
        FROM customer_summary
        GROUP BY customer_type
        ORDER BY total_revenue DESC
    """

    return run_query(
        query,
        [start_date, end_date, country, country]
    )
