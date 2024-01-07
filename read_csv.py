# coding: utf-8
import pandas as pd

df = pd.read_csv('turkish_inflectional_suffixes.csv')


for _, row in df.iterrows():
    print(row['suffix'])
    
