import pandas as pd

# Load the data
df = pd.read_excel("Online Retail.xlsx")

# Basic information
print("Shape of data:", df.shape)
print("\nColumn names:")
print(df.columns.tolist())

print("\nFirst 5 rows:")
print(df.head())

print("\nData types:")
print(df.dtypes)

print("\nMissing values:")
print(df.isnull().sum())

print("\nBasic statistics:")
print(df.describe())