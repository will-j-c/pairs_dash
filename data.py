from requests import get
import pandas as pd

class Data:
    
    def create_pair_data(self, pair_1, pair_2, resolution, beta, interval, ticker_type='mark', lag=72):
        pair_1_df = self._create_df_candles(pair_1, resolution, ticker_type)
        pair_2_df = self._create_df_candles(pair_2, resolution, ticker_type)
        pairs_df = pd.merge(pair_1_df, pair_2_df, on='time', suffixes=[pair_1, pair_2])
        pairs_df['spread'] = pairs_df[f'close{pair_1}'] - beta * pairs_df[f'close{pair_2}']
        pairs_df['median'] = pairs_df['spread'].rolling(lag).median()
        pairs_df['uq'] = pairs_df['spread'].rolling(lag).quantile(0.75)
        pairs_df['lq'] = pairs_df['spread'].rolling(lag).quantile(0.25)
        pairs_df['robust'] = (pairs_df['spread'] - pairs_df['median']) / (pairs_df['uq'] - pairs_df['lq'])
        pairs_df.dropna(inplace=True)
        pairs_df = pairs_df.tail(interval)
        return pairs_df
        

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


    def _check_input_type(self, obj):
        if not isinstance(obj, str):
            raise TypeError(f'{obj} is not of the correct type. Should be a string.')


if __name__ == '__main__':
    data = Data()
    data.create_pair_data('PF_SEIUSD', 'PF_POLUSD', '1h', 1)
