import pandas as pd
data = {"Name": ["Alice", "Bob", "Charlie", "David"],
        "Age": [32,31,45,35]
}
df = pd.DataFrame(data, index = ["a", "b", "c", "d"])
#print(df.loc["c"])

# Add a new column
df["City"] = ["Chandigarh", "Pune", "Mumbai", "Delhi"]

# Add a new row
new_rows = pd.DataFrame([{"Name": "sandy", "Age": 29, "City": "Bangalore"},
                         {"Name": "sanjay", "Age": 28, "City": "Jaipur"}], index=["e", "f"])
df = pd.concat([df, new_rows])
print(df)