import requests
import pandas as pd
import json

# Fetch the dataset
url = "https://hebbkx1anhila5yf.public.blob.vercel-storage.com/crop_yield-vVSgMXEYDuWI9cFGqrAOXthiUiRFNl.csv"

print("[v0] Fetching crop yield dataset...")
response = requests.get(url)

# Save the CSV content
with open('crop_yield.csv', 'wb') as f:
    f.write(response.content)

print("[v0] Dataset downloaded successfully")

# Load and analyze the dataset
df = pd.read_csv('crop_yield.csv')

print(f"[v0] Dataset shape: {df.shape}")
print(f"[v0] Columns: {df.columns.tolist()}")
print(f"\n[v0] First few rows:")
print(df.head())

print(f"\n[v0] Data types:")
print(df.dtypes)

print(f"\n[v0] Missing values:")
print(df.isnull().sum())

print(f"\n[v0] Unique crops: {df['Crop'].nunique()}")
print(f"[v0] Crop list: {df['Crop'].unique().tolist()}")

print(f"\n[v0] Unique states: {df['State'].nunique()}")
print(f"\n[v0] Unique seasons: {df['Season'].unique().tolist()}")

# Statistical summary
print(f"\n[v0] Statistical Summary:")
print(df.describe())

# Save analysis results
analysis = {
    "total_records": len(df),
    "crops": df['Crop'].unique().tolist(),
    "states": df['State'].unique().tolist(),
    "seasons": df['Season'].unique().tolist(),
    "year_range": f"{df['Crop_Year'].min()} - {df['Crop_Year'].max()}"
}

with open('dataset_analysis.json', 'w') as f:
    json.dump(analysis, f, indent=2)

print("\n[v0] Analysis complete! Results saved to dataset_analysis.json")
