import pandas as pd
import numpy as np
import yfinance as yf
import pymongo
import json
from datetime import datetime



#ambil daftar dari csv
data = pd.read_csv('Daftar_Saham.csv')
print(data)

#koneksi ke mongodb
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["yfinance"]

#ambil satu dua data dulu
for index, row in data.iterrows():
   
  
    print(row['Kode'] + '.JK', row['Nama Perusahaan'])

    ticker = yf.Ticker(row['Kode'] + '.JK')
    hist = ticker.history(start="2014-01-01", end="2025-03-07")

   
    hist.reset_index(inplace=True)
    hist['Date'] = hist['Date'].apply(lambda x: x.isoformat())
    data_json = json.loads(hist.to_json(orient="records", date_format="iso"))
   
    if data_json:
        collection = db[row['Nama Perusahaan']]
        collection.insert_many(data_json)
        print(f"Data saham {row['Kode']} berhasil disimpan ke MongoDB!")
    else:
        print(f"Tidak ada data yang tersedia untuk {row['Kode']}.")

