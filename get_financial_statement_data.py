from vnstock3 import Vnstock
import pandas as pd

# Lấy danh sách cổ phiếu niêm yết
VN_stocks_list = Vnstock().stock().listing.symbols_by_industries()

# Lập danh sách cổ phiếu không trong lĩnh vực tài chính
stocks_list = [stock for stock, code in zip(VN_stocks_list['symbol'], VN_stocks_list['icb_code2']) if not code.startswith('8')]

# Tải dữ liệu các công ty có trong danh sách
docs = {'Balance Sheet': 'balance_sheet', 'Income Statement': 'income_statement', 'Cash Flow': 'cash_flow', 'Ratio': 'ratio'}

for stock, i in zip(stocks_list, range(len(stocks_list))):
    try:
        stock_info = Vnstock().stock(symbol=stock, source='VCI')
        for key, value in docs.items():
            data = eval(f"stock_info.finance.{value}(period='quarter', lang='en')")
            path = f"Data/{key}/{stock}.csv"
            data.to_csv(path)
        print(i)
    except:
        pass