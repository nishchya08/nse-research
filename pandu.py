import pandas as pd
#  Series  = A Pandas 1-Dimensional labeled array capable of holding any data type
#            Think of it like a single column in a spreadhseet(1-Dimensional)

#print(pd.__version__)

# data = [100,101,102]
# #series = pd.Series(data)
# series = pd.Series(data, index=[1, 2, 3])
# #print(series.loc[2])
# #print(series)
# #print(series.iloc[0])
# print(series[series <= 100])

calories = {"Day 1": 100, "Day 2": 200, "Day 3": 150}
series = pd.Series(calories)
# print(calories)
series.loc["Day 3"] += 150
print(series)