import pandas as pd

df = pd.read_csv("data.csv", index_col="Name")

# SELECTION BY COLUMN
#print(df.to_string())
#print(df["Name"].to_string())
#print(df[["Name", "Height"]].to_string())

# SELECTION BY ROW/S
#df = df.set_index("Name", drop=False)
#print(df.loc["Charizard":"Blastoise", ["Height", "Weight"]])
#print(df.iloc[0:11:2])
pokemon = input("Enter Pokemon name: ")

try:
    print(df.loc[pokemon])
except KeyError:
    print("Pokemon not found")