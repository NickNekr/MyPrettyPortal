import pandas as pd

# Создаем два DataFrame для примера
data1 = {"id": [1], "region": ["Orel"]}

data2 = {"id": [1], "region": ["Meow"]}

df1 = pd.DataFrame(data1)
df2 = pd.DataFrame(data2)

# Слияние по колонке 'id'
merged_df = df1.merge(df2, on=["id"], how="outer", indicator=True)

print(merged_df)
