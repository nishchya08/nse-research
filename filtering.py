import pandas as pd
df = pd.read_csv("data.csv")

# Filtering: Keeping the rows that matching a condition

#tall_pokemon = df[df["Height"] >= 2.0]
#heavy_pokemon = df[df["Weight"] > 100]

#legendary = df[df["Legendary"] == True]

#water_pokemon = df[(df["Type1"] == "Water") | (df["Type2"] == "Water")]

ff_pokemon = df[(df["Type1"] == "Fire") & (df["Type2"] == "Flying")]

print(ff_pokemon)

#print(water_pokemon)

#print(legendary)
#print(heavy_pokemon)
#print(tall_pokemon)