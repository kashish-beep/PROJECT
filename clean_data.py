
import pandas as pd

# Load the dataset
df = pd.read_excel("Online Retail.xlsx")

print("Original shape:", df.shape)

# Remove duplicate rows
df = df.drop_duplicates()

# Remove rows without product descriptions
df = df.dropna(subset=["Description"])

# Remove rows with invalid prices or quantities
df = df[(df["Quantity"] > 0) & (df["UnitPrice"] > 0)]

# Identify cancelled invoices
df["InvoiceNo"] = df["InvoiceNo"].astype(str)
cancelled = df["InvoiceNo"].str.startswith("C")

print("Cancelled invoice rows:", cancelled.sum())

# Exclude cancelled invoices from sales analysis
df = df[~cancelled].copy()

# Create revenue column
df["Revenue"] = df["Quantity"] * df["UnitPrice"]

# Create month column for monthly analysis
df["Month"] = df["InvoiceDate"].dt.to_period("M").astype(str)

# Save the cleaned dataset
df.to_csv("cleaned_sales.csv", index=False)

print("Cleaned shape:", df.shape)
print("Total revenue:", round(df["Revenue"].sum(), 2))
print("Unique invoices:", df["InvoiceNo"].nunique())
print("Unique customers:", df["CustomerID"].nunique())
print("\nMissing values after cleaning:")
print(df.isnull().sum())
