import pandas as pd
import os
from vnstock3 import Vnstock

in_dir = 'Results'

out_dir = 'Data/Historical Data/Stocks'

eff_files = [file for file in os.listdir(in_dir) if file.startswith('efficiency_stocks')]

exst_tickers = [file.split('.')[0] for file in os.listdir(out_dir)]

for file in eff_files:
    df = pd.read_csv(f'{in_dir}/{file}', header=[0, 1], index_col=[0])

    for col in df.columns:
        for ticker in df[col].dropna().tolist():
            if ticker not in exst_tickers:
                info = Vnstock().stock(symbol=ticker, source='VCI')
                dt = info.quote.history(start='2010-01-01', end='2024-10-10', interval='1D')
                dt.to_csv(f"{out_dir}/{ticker}.csv")

for ind in ['VN30', 'VNINDEX']:
    info = Vnstock().stock(symbol=ind, source='VCI')
    dt = info.quote.history(start='2010-01-01', end='2024-10-10', interval='1D')
    dt.to_csv(f"Data/Historical Data/{ind}.csv")

