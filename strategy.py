import talib as ta
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

        ha = heikinashi(df)

        df['ha_open'] = ha['open']
        df['ha_close'] = ha['close']
        df['mfi'] = ta.MFI(df['high'], df['close'], df['close'], df['volume'], timeperiod=14)

        df.fillna(method='ffill', inplace=True)

        df.loc[
            (
                df['ha_open'].lt(df['ha_close']) &   # green bar
                crossed_above(df['mfi'], 30)
            ),
            'buy'] = 1

        df.loc[
            (
                df['ha_open'].lt(df['ha_close']) &  # red bar
                crossed_below(df['mfi'], 70)
            ),
            'sell'] = 1

        df.loc[
            (
                crossed_above(df['mfi'], 70) |
                crossed_below(df['mfi'], 30)
            ),
            'tp'] = 1

        latest = df.iloc[-1]

        (buy, sell, tp) = latest['buy'] == 1, latest['sell'] == 1, latest['tp'] == 1

        if buy and not sell:
            return 1
        elif sell and not buy:
            return 2
        elif tp and not buy and not sell:
            return 3
        else:
            return 0
