
import streamlit as st
import pandas as pd
import plotly.express as px
from sql_queries import get_monthly_growth, get_customer_segments
import matplotlib.pyplot as plt

st.set_page_config(
    page_title="E-commerce Sales Dashboard",
    page_icon="📊",
    layout="wide"
)

# Load cleaned data
@st.cache_data
def load_data():
    df = pd.read_csv("cleaned_sales.csv")
    df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"])
    df["Month"] = df["InvoiceDate"].dt.to_period("M").astype(str)
    return df

df = load_data()

# Dashboard title
st.title("📊 E-commerce Sales Analysis Dashboard")
st.caption("Explore sales performance, product trends and customer behaviour.")

# Sidebar filters
st.sidebar.header("Filters")

countries = ["All"] + sorted(df["Country"].dropna().unique().tolist())
selected_country = st.sidebar.selectbox("Select Country", countries)

min_date = df["InvoiceDate"].min().date()
max_date = df["InvoiceDate"].max().date()

date_range = st.sidebar.date_input(
    "Select Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)
start_date, end_date = min_date, max_date

if isinstance(date_range, (tuple, list)) and len(date_range) == 2:
    start_date, end_date = date_range

# Apply filters
filtered = df.copy()

if selected_country != "All":
    filtered = filtered[filtered["Country"] == selected_country]

if isinstance(date_range, (tuple, list)) and len(date_range) == 2:
    start_date, end_date = date_range
    filtered = filtered[
        (filtered["InvoiceDate"].dt.date >= start_date) &
        (filtered["InvoiceDate"].dt.date <= end_date)
    ]

if filtered.empty:
    st.warning("No sales data available for these filters.")
    st.stop()


# KPI calculations
total_revenue = filtered["Revenue"].sum()
total_orders = filtered["InvoiceNo"].nunique()
total_customers = filtered["CustomerID"].nunique()
total_products = filtered["Description"].nunique()

# Average Order Value
aov = total_revenue / total_orders if total_orders else 0

# Repeat customer analysis
customer_orders = (
    filtered.dropna(subset=["CustomerID"])
    .groupby("CustomerID")["InvoiceNo"]
    .nunique()
)

repeat_customers = (customer_orders > 1).sum()
identified_customers = customer_orders.shape[0]

repeat_rate = (
    repeat_customers / identified_customers * 100
    if identified_customers else 0
)

# Display KPI cards
c1, c2, c3 = st.columns(3)
c4, c5, c6 = st.columns(3)

c1.metric("Total Revenue", f"£{total_revenue:,.2f}")
c2.metric("Total Orders", f"{total_orders:,}")
c3.metric("Average Order Value", f"£{aov:,.2f}")

c4.metric("Unique Customers", f"{total_customers:,}")
c5.metric("Unique Products", f"{total_products:,}")
c6.metric("Repeat Customer Rate", f"{repeat_rate:.1f}%")




st.divider()



# Month-over-month revenue growth
st.subheader("Month-over-Month Revenue Growth")

monthly_growth = (
    filtered.groupby("Month", as_index=False)["Revenue"]
    .sum()
    .sort_values("Month")
)

monthly_growth["MoM Growth (%)"] = (
    monthly_growth["Revenue"].pct_change() * 100
)

fig_growth = px.bar(
    monthly_growth,
    x="Month",
    y="MoM Growth (%)",
    title="Monthly Revenue Growth (%)",
    labels={
        "MoM Growth (%)": "Growth (%)",
        "Month": "Month"
    }
)

fig_growth.add_hline(y=0, line_dash="dash")

st.plotly_chart(
    fig_growth,
    use_container_width=True,
    key="monthly_growth_chart"
)


# Show the detailed figures
with st.expander("View monthly growth calculations"):
    st.dataframe(
        monthly_growth.round(2),
        use_container_width=True
    )


# Product and country charts
left, right = st.columns(2)

with left:
    st.subheader("Top 10 Products by Revenue")
    products = (
        filtered.groupby("Description", as_index=False)["Revenue"]
        .sum()
        .nlargest(10, "Revenue")
        .sort_values("Revenue")
    )

    fig_products = px.bar(
        products,
        x="Revenue",
        y="Description",
        orientation="h",
        title="Highest Revenue Products"
    )
    st.plotly_chart(fig_products, use_container_width=True)

with right:
    st.subheader("Top 10 Countries by Revenue")
    country_sales = (
        filtered.groupby("Country", as_index=False)["Revenue"]
        .sum()
        .nlargest(10, "Revenue")
        .sort_values("Revenue")
    )

    fig_countries = px.bar(
        country_sales,
        x="Revenue",
        y="Country",
        orientation="h",
        title="Highest Revenue Countries"
    )
    st.plotly_chart(fig_countries, use_container_width=True)

# Customer insights
st.subheader("Top 10 Customers by Revenue")

customer_sales = (
    filtered.dropna(subset=["CustomerID"])
    .groupby("CustomerID", as_index=False)["Revenue"]
    .sum()
    .nlargest(10, "Revenue")
    .sort_values("Revenue")
)

fig_customers = px.bar(
    customer_sales,
    x="Revenue",
    y="CustomerID",
    orientation="h",
    title="Highest Spending Customers"
)
st.plotly_chart(fig_customers, use_container_width=True)

# Data preview
with st.expander("View filtered sales data"):
    st.dataframe(filtered.head(500), use_container_width=True)

st.caption("Revenue is calculated from positive, non-cancelled invoice lines.")


# Actionable Business Insights
st.subheader("💡 Key Business Insights")

# 1. Best sales month
monthly_insights = (
    filtered.groupby("Month", as_index=False)["Revenue"]
    .sum()
    .sort_values("Month")
)

if not monthly_insights.empty:
    best_month = monthly_insights.loc[
        monthly_insights["Revenue"].idxmax()
    ]

    st.markdown(
        f"**📈 Highest-revenue month:** {best_month['Month']} "
        f"generated £{best_month['Revenue']:,.2f}."
    )

    st.info(
        "Business action: Review stock availability, promotions and "
        "marketing activity around this period. Prepare inventory "
        "early if the pattern repeats in future periods."
    )

# 2. Top product and revenue share
product_insights = (
    filtered.groupby("Description", as_index=False)["Revenue"]
    .sum()
    .sort_values("Revenue", ascending=False)
)

if not product_insights.empty:
    best_product = product_insights.iloc[0]
    total_revenue = filtered["Revenue"].sum()

    product_share = (
        best_product["Revenue"] / total_revenue * 100
        if total_revenue > 0 else 0
    )

    st.markdown(
        f"**🛍️ Highest-revenue product:** "
        f"{best_product['Description']} generated "
        f"£{best_product['Revenue']:,.2f}, or "
        f"{product_share:.1f}% of filtered revenue."
    )

    st.info(
        "Business action: Monitor stock availability for this product. "
        "Compare its sales volume and margin with other products "
        "before deciding whether to promote it further."
    )

# 3. Highest-revenue country
country_insights = (
    filtered.groupby("Country", as_index=False)["Revenue"]
    .sum()
    .sort_values("Revenue", ascending=False)
)

if not country_insights.empty:
    best_country = country_insights.iloc[0]
    total_revenue = filtered["Revenue"].sum()

    country_share = (
        best_country["Revenue"] / total_revenue * 100
        if total_revenue > 0 else 0
    )

    st.markdown(
        f"**🌍 Leading country:** {best_country['Country']} "
        f"generated £{best_country['Revenue']:,.2f}, contributing "
        f"{country_share:.1f}% of filtered revenue."
    )

    if country_share >= 70:
        st.warning(
            "Business action: Revenue is highly concentrated in this "
            "country. Investigate opportunities in other markets while "
            "protecting performance in the leading market."
        )
    else:
        st.info(
            "Business action: Compare country-level growth and "
            "customer demand to identify markets with expansion potential."
        )

# 4. Monthly growth: strongest increase
if len(monthly_insights) >= 2:
    monthly_insights["Revenue Change"] = (
        monthly_insights["Revenue"].diff()
    )

    monthly_insights["Growth (%)"] = (
        monthly_insights["Revenue"].pct_change() * 100
    )

    valid_growth = monthly_insights.dropna(subset=["Growth (%)"])

    if not valid_growth.empty:
        strongest_growth = valid_growth.loc[
            valid_growth["Growth (%)"].idxmax()
        ]

        st.markdown(
            f"**📊 Strongest month-over-month growth:** "
            f"{strongest_growth['Month']} recorded "
            f"{strongest_growth['Growth (%)']:.1f}% growth."
        )

        st.info(
            "Business action: Investigate whether this increase was "
            "driven by promotions, seasonal demand, order volume or "
            "a small number of large orders before allocating more budget."
        )


# Calculate insights directly from filtered data
monthly_insights = (
    filtered.groupby("Month", as_index=False)["Revenue"]
    .sum()
)

product_insights = (
    filtered.groupby("Description", as_index=False)["Revenue"]
    .sum()
)

country_insights = (
    filtered.groupby("Country", as_index=False)["Revenue"]
    .sum()
)

# Best sales month
if not monthly_insights.empty:
    best_month = monthly_insights.loc[
        monthly_insights["Revenue"].idxmax()
    ]
    st.write(
        f"📈 **Best Sales Month:** {best_month['Month']} "
        f"— £{best_month['Revenue']:,.2f}"
    )

# Top product
if not product_insights.empty:
    best_product = product_insights.loc[
        product_insights["Revenue"].idxmax()
    ]
    st.write(
        f"🛍️ **Top Product:** {best_product['Description']} "
        f"— £{best_product['Revenue']:,.2f}"
    )

# Top country
if not country_insights.empty:
    best_country = country_insights.loc[
        country_insights["Revenue"].idxmax()
    ]
    st.write(
        f"🌍 **Top Country:** {best_country['Country']} "
        f"— £{best_country['Revenue']:,.2f}"
    )

# Highest-revenue country's contribution
total_filtered_revenue = filtered["Revenue"].sum()

if total_filtered_revenue > 0 and not country_insights.empty:
    share = (
        country_insights["Revenue"].max()
        / total_filtered_revenue
    ) * 100

    st.write(
        f"💡 The highest-revenue country contributes "
        f"{share:.1f}% of filtered revenue."
    )


# SQL-powered analysis
st.divider()
st.header("🧮 SQL-Powered Analysis")

st.subheader("Monthly Revenue Growth — SQL Window Functions")

sql_monthly = get_monthly_growth(
    selected_country, start_date, end_date
)

st.dataframe(sql_monthly, use_container_width=True)

st.caption(
    "Calculated in DuckDB SQL using a CTE, LAG(), "
    "and a window function."
)

st.subheader("Customer Segmentation — SQL CASE WHEN")

sql_customers = get_customer_segments(
    selected_country, start_date, end_date
)

st.dataframe(sql_customers, use_container_width=True)

st.caption(
    "Customers are classified by their number of distinct orders. "
    "Customer-level analysis excludes missing CustomerIDs."
)

# Matplotlib visualization
st.divider()
st.subheader("📉 Monthly Revenue Trend — Matplotlib")

monthly_matplotlib = (
    filtered.groupby("Month", as_index=False)["Revenue"]
    .sum()
    .sort_values("Month")
)

fig, ax = plt.subplots(figsize=(10, 4))

ax.plot(
    monthly_matplotlib["Month"],
    monthly_matplotlib["Revenue"],
    marker="o"
)

ax.set_title("Monthly Revenue Trend")
ax.set_xlabel("Month")
ax.set_ylabel("Revenue (£)")
ax.tick_params(axis="x", rotation=45)
ax.grid(True, linestyle="--", alpha=0.4)

fig.tight_layout()
st.pyplot(fig)
plt.close(fig)
