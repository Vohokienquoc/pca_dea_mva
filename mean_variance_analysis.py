import pandas as pd
import numpy as np
from datetime import datetime
from scipy.optimize import minimize

class PortfolioOptimizer:
    def __init__(self, efficiency_stocks_file, initial_capital=1):
        self.efficiency_stocks_file = efficiency_stocks_file
        self.initial_capital = initial_capital
        self.get_efficiency_stocks()
        self.get_investment_length()
        self.get_stocks_data()
        self.get_others_data()
        self.portfolio_allocation()

    def get_efficiency_stocks(self):
        self.efficiency_stocks = pd.read_csv(f"Results/{self.efficiency_stocks_file}", header=[0, 1], index_col=[0])

    def get_investment_length(self):
        quarter_months = {1: 1, 2: 4, 3: 7, 4: 10}

        f_quarter = self.efficiency_stocks.columns[0]

        month = quarter_months[int(f_quarter[1])]
        year = int(f_quarter[0])
        self.first_day1 = datetime(year, month, 21)

        f_month = month - 3 if int(f_quarter[1]) != 1 else 10
        f_year = year if int(f_quarter[1]) != 1 else year - 1
        self.first_day2 = datetime(f_year, f_month, 21)

        l_quarter = self.efficiency_stocks.columns[-1]

        month = quarter_months[int(l_quarter[1])]
        year = int(l_quarter[0])

        l_month = month + 3 if int(l_quarter[1]) != 4 else 1
        l_year = year if int(l_quarter[1]) != 4 else year + 1
        self.last_day = datetime(l_year, l_month, 20)  
 
    def get_stocks_data(self):
        stocks_data = {}
        all_stocks = set()

        for col in self.efficiency_stocks.columns:
            all_stocks.update(self.efficiency_stocks[col].dropna().unique())

        all_stocks = [*all_stocks]

        for stock in all_stocks:
            file_path = f"Data/Historical Data/Stocks/{stock}.csv"
            df = pd.read_csv(file_path)

            df['time'] = pd.to_datetime(df['time'])

            if 'close' in df.columns:
                df.rename(columns={'time': 'date'}, inplace=True)
                df.set_index('date', inplace=True)
                stocks_data[stock] = df['close']

        stocks_data = pd.DataFrame(stocks_data)
        stocks_data.ffill(inplace=True)
        stocks_data.bfill(inplace=True)

        self.stocks_data = stocks_data[(stocks_data.index >= self.first_day2) & (stocks_data.index <= self.last_day)]
    
    def get_others_data(self):
        dir = 'Data/Historical Data'

        df = pd.read_csv(f'{dir}/1-YearBond.csv')
        df.rename(columns={'Price': 'close', 'Date': 'date'}, inplace=True)
        df['date'] = pd.to_datetime(df['date'], format='%m/%d/%Y')
        df['date'] = df['date'].dt.strftime('%Y-%m-%d')
        df['date'] = pd.to_datetime(df['date'])
        df.set_index('date', inplace=True)
        self.bond = pd.DataFrame(df['close'])

        df = pd.read_csv(f'{dir}/VN30.csv')
        df['time'] = pd.to_datetime(df['time'])
        df.rename(columns={'time': 'date'}, inplace=True)
        df.set_index('date', inplace=True)
        df = pd.DataFrame(df['close'])
        df = df[(df.index >= self.first_day1) & (df.index <= self.last_day)]
        df['VN30'] = df['close'] / df['close'].iloc[0] * self.initial_capital
        self.VN30 = df['VN30']

        bond = self.bond[(self.bond.index >= self.first_day1) & (self.bond.index <= self.last_day)]
        risk_fr = bond['close'].mean() / 100
        
        ret = np.log(df / df.shift(1))

        annual_ret = ret.iloc[:, 0].mean() * 252
        annual_vol = ret.iloc[:, 0].std() * np.sqrt(252)
        sr = (annual_ret - risk_fr) / annual_vol

        self.VN30_performance = pd.DataFrame({
            'Information Level': ['Sharpe Ratio', 'Annualized Return', 'Annualized Volatility', 'Final Portfolio Value'],
            'VN30': ['{:.2f}'.format(sr), '{:.2%}'.format(annual_ret), '{:.2%}'.format(annual_vol), '{:.1f}'.format(df.iloc[-1, 0])]
        })

        self.VN30_performance.set_index('Information Level', inplace=True)

        df = pd.read_csv(f'{dir}/VNINDEX.csv')
        df['time'] = pd.to_datetime(df['time'])
        df.rename(columns={'time': 'date'}, inplace=True)
        df.set_index('date', inplace=True)
        df = pd.DataFrame(df['close'])
        df = df[(df.index >= self.first_day1) & (df.index <= self.last_day)]
        df['VNINDEX'] = df['close'] / df['close'].iloc[0] * self.initial_capital
        self.VNINDEX = df['VNINDEX']

        bond = self.bond[(self.bond.index >= self.first_day1) & (self.bond.index <= self.last_day)]
        risk_fr = bond['close'].mean() / 100
        
        ret = np.log(df / df.shift(1))

        annual_ret = ret.iloc[:, 0].mean() * 252
        annual_vol = ret.iloc[:, 0].std() * np.sqrt(252)
        sr = (annual_ret - risk_fr) / annual_vol

        self.VNINDEX_performance = pd.DataFrame({
            'Information Level': ['Sharpe Ratio', 'Annualized Return', 'Annualized Volatility', 'Final Portfolio Value'],
            'VNINDEX': ['{:.2f}'.format(sr), '{:.2%}'.format(annual_ret), '{:.2%}'.format(annual_vol), '{:.1f}'.format(df.iloc[-1, 0])]
        })

        self.VNINDEX_performance.set_index('Information Level', inplace=True)

    def get_quarter_data(self, quarter, efficiency_stocks):
        quarter_months = {1: 1, 2: 4, 3: 7, 4: 10}

        end_month = quarter_months[int(quarter[1])]
        end_year = int(quarter[0])
        end_day = datetime(end_year, end_month, 20)

        start_month = end_month - 3 if int(quarter[1]) != 1 else 10
        start_year = end_year if int(quarter[1]) != 1 else end_year - 1
        start_day = datetime(start_year, start_month, 21)
       
        quarter_bond_data = self.bond[(self.bond.index >= start_day) & (self.bond.index <= end_day)]
        
        self.risk_free_rate =  quarter_bond_data['close'].mean() / 100

        ret = np.log(self.stocks_data / self.stocks_data.shift(1))
        ret = ret[(ret.index >= start_day) & (ret.index >= end_day)]
        self.quarter_stocks_return = ret[efficiency_stocks.dropna().tolist()]

        s_month = quarter_months[int(quarter[1])]
        s_year = int(quarter[0])
        s_day = datetime(s_year, s_month, 21)

        e_month = s_month + 3 if int(quarter[1]) != 4 else 1
        e_year = s_year if int(quarter[1]) != 4 else s_year + 1
        e_day = datetime(e_year, e_month, 20)  
  
        quarter_stocks_data = self.stocks_data[(self.stocks_data.index >= s_day) & (self.stocks_data.index <= e_day)]
        self.quarter_stocks_data = quarter_stocks_data[efficiency_stocks.dropna().tolist()]
    
    def get_quarter_return(self, weights):
        port_ret = np.sum((self.quarter_stocks_return.mean() * weights) * 252)

        return port_ret

    def get_quarter_volatility(self, weights):
        port_vol = np.sqrt(np.dot(weights.T, np.dot(self.quarter_stocks_return.cov() * 252, weights)))
    
        return port_vol

    def get_negative_SR(self, weights):
        port_ret = self.get_quarter_return(weights)
        port_vol = self.get_quarter_volatility(weights)
        sr = - (port_ret - self.risk_free_rate) / port_vol
        
        return sr

    def get_optimal_weights(self):
        n_stocks = len(self.quarter_stocks_return.columns)
        constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
        bounds = tuple((0, 1) for _ in range(n_stocks))
        initial_guess = n_stocks * [1 / n_stocks,]

        optimal = minimize(self.get_negative_SR, initial_guess, method='SLSQP', bounds=bounds, constraints=constraints)
        
        self.optimal_weights =  optimal.x

        return optimal.x
    
    def portfolio_allocation(self):
        asset_memory = []
        date_memory = []
        begin_portfolio_value = self.initial_capital

        for col in self.efficiency_stocks.columns:
            quarter = col
            efficiency_stocks = self.efficiency_stocks[col]

            self.get_quarter_data(quarter, efficiency_stocks)

            optimal_weights = self.get_optimal_weights()

            prices = self.quarter_stocks_data.iloc[0]

            port_cap = begin_portfolio_value * optimal_weights

            port_shares = port_cap / prices

            for day in range(0, len(self.quarter_stocks_data)):
                total_asset = sum(port_shares * self.quarter_stocks_data.iloc[day])
                asset_memory.append(total_asset)
                date_memory.append(self.quarter_stocks_data.index[day])

            begin_portfolio_value = asset_memory[-1]

        name = self.efficiency_stocks_file.split('.')[0].split('_')[2]
        df = pd.DataFrame({
            f'{name}%': asset_memory,
            'date': date_memory
        })

        df.set_index('date', inplace=True)

        self.portfolio_values = df

        bond = self.bond[(self.bond.index >= self.first_day1) & (self.bond.index <= self.last_day)]
        risk_fr = bond['close'].mean() / 100
        
        ret = np.log(df / df.shift(1))

        annual_ret = ret.iloc[:, 0].mean() * 252
        annual_vol = ret.iloc[:, 0].std() * np.sqrt(252)
        sr = (annual_ret - risk_fr) / annual_vol

        self.portfolio_performance = pd.DataFrame({
            'Information Level': ['Sharpe Ratio', 'Annualized Return', 'Annualized Volatility', 'Final Portfolio Value'],
            f"{name}%": ['{:.2f}'.format(sr), '{:.2%}'.format(annual_ret), '{:.2%}'.format(annual_vol), '{:.1f}'.format(df.iloc[-1, 0])]
        })

        self.portfolio_performance.set_index('Information Level', inplace=True)

    def plot(self):
        self.portfolio_values.plot()