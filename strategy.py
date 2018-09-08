# import talib as ta
from util import *
from indicators import *


class Strategy():
    def __init__(self, client, timeframe='5m'):
        self.client = client
        # self.pair = pair
        self.timeframe = timeframe

    def get_ticker_indicator(self):
        return int(self.timeframe[:-1])

    def predict(self):

        # df = pd.DataFrame(self.client.Trade.Trade_getBucketed(
        #     binSize=self.timeframe,
        #     symbol='XBTUSD',
        #     count=100,
        #     reverse=True
        # ).result()[0])

        # df.set_index(['timestamp'], inplace=True)

        res = self.client.Trade.Trade_getBucketed(
            binSize=self.timeframe,
            symbol='XBTUSD',
            count=100,
            reverse=True
        ).result()[0]

        df = parse_dataframe(res)

        bb = bollinger_bands(df, period=40, stdv=2)
        df['lower'] = bb['bb_lower']
        df['mid'] = bb['bb_middle']
        df['upper'] = bb['bb_upper']
        df['mean-volume'] = df['volume'].mean()
        df['delta_low'] = (df['mid'] - df['lower']).abs()
        df['delta_high'] = (df['upper'] - df['mid']).abs()
        # df['price_delta'] = (df['open'] - df['close']).abs()
        df['close_delta'] = (df['close'] - df['close'].shift()).abs()
        df['open_delta'] = (df['open'] - df['open'].shift()).abs()
        df['tail'] = (df['close'] - df['low']).abs()
        df['head'] = (df['high'] - df['open']).abs()

        df.fillna(method='ffill', inplace=True)

        df.loc[
            (
                df['lower'].gt(df['close'] * 0.008) &
                # df['lower'].shift().gt(0) &
                df['delta_low'].gt(df['close'] * 0.008) &
                df['close_delta'].gt(df['close'] * 0.0175) &
                df['tail'].lt(df['delta_low'] * 0.25) &
                df['close'].lt(df['lower'].shift()) &
                df['close'].le(df['close'].shift())
                # df['volume'].gt(df['volume'].mean() * 4) &
                # (df['mean-volume'] > 0.75)
            ),
            'buy'] = 1

        df.loc[
            (
                df['upper'].lt(df['open'] * 0.008) &
                # df['upper'].shift().gt(0) &
                df['delta_high'].lt(df['open'] * 0.008) &
                df['open_delta'].lt(df['open'] * 0.0175) &
                df['head'].gt(df['delta_high'] * 0.25) &
                df['open'].gt(df['upper'].shift()) &
                df['open'].ge(df['open'].shift())
                # df['volume'].gt(df['volume'].mean() * 4)
                # (df['mean-volume'] > 0.75)
            ),
            'sell'] = 1

        df.loc[
            (
                # crossed_above(df['close'], df['mid']) |
                # crossed_below(df['close'], df['mid']) |
                crossed_above(df['close'], df['upper']) |
                crossed_below(df['close'], df['lower']) |
                crossed_above(df['high'], df['upper']) |
                crossed_below(df['low'], df['lower'])
            ),
            'target'] = 1

        latest = df.iloc[-1]

        (buy, sell, target) = latest['buy'] == 1, latest['sell'] == 1, latest['target'] == 1

        if buy and not sell:
            return 1
        elif sell and not buy:
            return 2
        elif target and not buy and not sell:
            return 3
        else:
            return 0
