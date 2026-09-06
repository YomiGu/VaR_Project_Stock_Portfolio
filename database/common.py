import pandas as pd

dell = pd.read_csv("data/dell.csv", sep=";")
avgo = pd.read_csv("data/avgo.csv", sep=";")
nvda = pd.read_csv("data/nvda.csv", sep=";")

print(dell.head())
print(dell.columns)
print(avgo.head())
print(avgo.columns)
print(nvda.head())
print(nvda.columns)
