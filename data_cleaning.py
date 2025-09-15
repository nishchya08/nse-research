import pandas as pd

# Data Cleaning = the process of fixing/removing:
#             incorrect, corrupted, incorrectly formatted,
#             ~75% of work done with pandas is data cleaning

df = pd.read_csv("data.csv")

# Drop irrelevant columns
#df = df.drop(columns=["Legendary", "No"])

# Handle missing data
#df = df.dropna(subset=["Type2"])
#df = df.fillna({"Type2": "None"})

# Fix inconsistent values
#df["Type1"] = df["Type1"].replace({"Grass": "GRASS",
#                                   "Fire": "FIRE"})


# Standardize text
#df["Name"] = df["Name"].str.lower()

# Fix data types
#df["Legendary"] = df["Legendary"].astype(bool)


# Remove duplicate values
df  = df.drop_duplicates()

print(df.to_string())