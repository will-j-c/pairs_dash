from requests import get
import pandas as pd
import numpy as np
from helper import authentication_function, get_headers, create_post_data
from dotenv import load_dotenv
import os

load_dotenv(override=True)

api_key = os.getenv('PUBLIC_KEY')
secret = os.getenv('SECRET')

class Data:
    
    def create_pair_data(self, pair_1, pair_2, resolution, beta, ticker_type='mark', lag=72):
        pair_1_df = self._create_df_candles(pair_1, resolution, ticker_type)
        pair_2_df = self._create_df_candles(pair_2, resolution, ticker_type)
        pairs_df = pd.merge(pair_1_df, pair_2_df, on='time', suffixes=[pair_1, pair_2])
        pairs_df['spread'] = pairs_df[f'close{pair_1}'] - beta * pairs_df[f'close{pair_2}']
        pairs_df['z'] = (pairs_df['spread'] - pairs_df['spread'].rolling(lag).mean()) / pairs_df['spread'].rolling(lag).std()
        pairs_df.dropna(inplace=True)
        pairs_df['time'] = pairs_df.index
        return pairs_df
    
        
    def create_axis_from_df(self, df):
        index = df['time']
        start = index.iloc[0]
        end = pd.Timestamp(index.iloc[-1]) + pd.Timedelta(hours=12)
        return pd.date_range(start, end, freq='h')

    def _create_df_candles(self, symbol, resolution, ticker_type):
        candles = self._get_candles(symbol, resolution, ticker_type)
        df = pd.DataFrame(candles)
        df['time'] = pd.to_datetime(df['time'], unit='ms')
        df.set_index('time', drop=True, inplace=True)
        df = df['close'].astype(float)
        return df

    def _call_api(self, url):
        r = get(url)
        data = r.json()
        r.close()
        return data
    
    def _get_candles(self, symbol, resolution, ticker_type):
        # Error for non input of strings
        self._check_input_type(symbol)
        self._check_input_type(resolution)
        self._check_input_type(ticker_type)

        # Error test the ticker type
        if ticker_type not in ['mark', 'spot', 'trade']:
            raise ValueError('The ticker type should be either mark, spot or trade')
        # Error test the resolution
        if ticker_type not in ['mark', 'spot', 'trade']:
            raise ValueError('The resolution type should be either mark, spot or trade')
        
        url = f'https://futures.kraken.com/api/charts/v1/{ticker_type}/{symbol}/{resolution}'
        data = self._call_api(url)

        if data['candles']:
            return data['candles']
        else:
            raise ValueError('The API returned an empty set of data')
    
    def _get_open_positions(self):
        base_url = 'https://futures.kraken.com/derivatives'
        endpoint = '/api/v3/openpositions'
        data = self._authenticated_call_api(endpoint, base_url, api_key, secret)
        if data['result'] == 'success':
            return data
        raise ValueError(f'Error: {data["error"]}')

    def _get_wallets(self):
        base_url = 'https://futures.kraken.com/derivatives'
        endpoint = '/api/v3/accounts'
        data = self._authenticated_call_api(endpoint, base_url, api_key, secret)
        if data['result'] == 'success':
            return data
        raise ValueError(f'Error: {data["error"]}')

    def _check_input_type(self, obj):
        if not isinstance(obj, str):
            raise TypeError(f'{obj} is not of the correct type. Should be a string.')
    
    def _authenticated_call_api(self, endpoint, base_url, api_key, api_secret, data=''):
        url = base_url + endpoint
        post_data = create_post_data(data)
        authent = authentication_function(post_data, endpoint, api_secret)
        headers = get_headers(api_key, authent)
        r = get(url, headers=headers, data=data)
        data_to_return = r.json()
        r.close()
        return data_to_return
    
    def _get_tickers(self):
        data = self._call_api('https://futures.kraken.com/derivatives/api/v3/tickers')
        if data['result'] == 'success':
            return data['tickers']
        raise ValueError(f'Error: {data["error"]}')
    
    def get_position_info(self, config):
        position_df = self._create_position_df(config)
        if position_df.empty:
            return position_df
        config_df = self._create_config_df(config)
        ticker_df = self._create_ticker_df()
        df = pd.merge(position_df, config_df, left_on='symbol', right_on='value')
        df = pd.merge(df, ticker_df, left_on='symbol', right_on='symbol')
        df['entry'] = df.apply(self._calc_entry, axis=1)
        df['entry_side'] = df.apply(self._calc_side, axis=1)
        df['pnl'] = df.apply(self._calc_pnl, axis=1)
        df['closing_fee'] = df['size'] * df['markPrice'] * 0.05/100
        df['estimated_net_pnl'] = df['pnl'] - df['closing_fee']
        df = df[['position','entry', 'entry_side', 'pnl', 'closing_fee', 'estimated_net_pnl']]
        df = df.groupby('position', as_index=False).sum()
        df['entry_side'] = np.where(df['entry_side'] == 0, 'Short Spread', 'Long spread')
        df.columns = ['Position', 'Entry', 'Entry Side', 'P&L', 'Est. Fee', 'Net P&L']
        df = df.round(7)
        return df
    
    def get_collateral_value(self):
        return float(self._get_wallets()['accounts']['flex']['collateralValue'])

    def _create_position_df(self, config):
        position_data = self._get_open_positions()['openPositions']
        strategy_symbols = [value['pair_1'] for value in config.values()] + [value['pair_2'] for value in config.values()]
        df = pd.DataFrame(position_data)
        if not df.empty:
            mask = df['symbol'].isin(strategy_symbols)
            df = df[mask]
        return df

    def _create_config_df(self, config):
        df = pd.DataFrame.from_dict(config).T
        df['position'] = df.index
        df.reset_index(inplace=True, drop=True)
        df = pd.melt(df, id_vars=['position', 'beta'], value_vars=['pair_1', 'pair_2'])
        return df
    
    def _create_ticker_df(self):
        tickers = self._get_tickers()
        df = pd.DataFrame.from_dict(tickers)
        return df
    
    def _calc_pnl(self, row):
        cost = row['price'] * row['size']
        current_value = row['markPrice'] * row['size']
        pnl = 0
        if row['side'] == 'long':
            pnl = current_value - cost
        else:
            pnl = cost - current_value
        return pnl
    
    def _calc_entry(self, row):
        if row['variable'] == 'pair_1':
            if row['side'] == 'long':
                return row['price']
            else:
                return -row['price']
            
        if row['variable'] == 'pair_2':
            if row['side'] == 'long':
                return row['beta'] * row['price']
            else:
                return -row['beta'] * row['price']
            
    def _calc_side(self, row):
        if row['variable'] == 'pair_1':
            if row['side'] == 'long':
                return 1
            else:
                return 0
            
        if row['variable'] == 'pair_2':
            if row['side'] == 'long':
                return 0
            else:
                return 1

    
if __name__ == '__main__':
    from helper import create_config_dict
    data = Data()
    config = create_config_dict()
    data.get_position_info(config)
