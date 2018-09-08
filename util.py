"""
    defines utility functions to be used
"""
from pandas import DatetimeIndex, merge, DataFrame, to_datetime
from configuration import TICKER_INTERVAL_MINUTES


def parse_dataframe(ticker: list) -> DataFrame:
    """
    builds dataframe based on the given trades

    :param ticker: see /trade/bucketed API
    :return: DataFrame
    """

    cols = ['timestamp', 'symbol', 'open', 'high', 'low', 'close', 'trades', 'volume', 'vwap', 'lastSize', 'turnover', 'homeNotional', 'foreignNotional']
    frame = DataFrame(ticker, columns=cols)

    # drop unnecessary columns
    frame.drop(['symbol', 'trades', 'vwap', 'lastSize', 'turnover', 'homeNotional', 'foreignNotional'], axis=1)

    # rename timestamp column
    frame = frame.rename(columns={'timestamp': 'date'})

    # reformat date column
    frame['date'] = to_datetime(frame['date'],
                                unit='ms',
                                utc=True,
                                infer_datetime_format=True)

    # group by index and aggregate results to eliminate duplicate ticks
    frame = frame.groupby(by='date', as_index=False, sort=True).agg({
        'open': 'first',
        'high': 'max',
        'low': 'min',
        'close': 'last',
        'volume': 'max',
    })

    frame.drop(frame.tail(1).index, inplace=True)  # eliminate partial candle

    return frame


def resample_to_interval(dataframe, interval):
    if isinstance(interval, str):
        interval = TICKER_INTERVAL_MINUTES[interval]

    """
        resamples the given dataframe to the desired interval. Please be aware you need to upscale this to join the results
        with the other dataframe

    :param dataframe: dataframe containing close/high/low/open/volume
    :param interval: to which ticker value in minutes would you like to resample it
    :return:
    """

    df = dataframe.copy()
    df = df.set_index(DatetimeIndex(df['date']))
    ohlc_dict = {
        'open': 'first',
        'high': 'max',
        'low': 'min',
        'close': 'last',
        'volume': 'sum'
    }
    df = df.resample(str(interval) + 'min').agg(ohlc_dict).dropna()
    df['date'] = df.index

    return df


def resampled_merge(original, resampled):
    """
    this method merges a resampled dataset back into the orignal data set

    :param original: the original non resampled dataset
    :param resampled:  the resampled dataset
    :return: the merged dataset
    """

    interval = int((original['date'] - original['date'].shift()).min().seconds / 60)
    resampled_interval = compute_interval(resampled)

    # no point in interpolating these colums
    # resampled = resampled.drop(columns=['date', 'volume'])
    resampled = resampled.drop(['date', 'volume'], axis=1)

    # rename all the colums to the correct interval
    for header in list(resampled):
        # store the resampled columns in it
        resampled['resample_{}_{}'.format(resampled_interval, header)] = resampled[header]

    # drop columns which should not be joined
    # resampled = resampled.drop(columns=['open', 'high', 'low', 'close'])
    resampled = resampled.drop(['open', 'high', 'low', 'close'], axis=1)

    resampled = resampled.resample(str(interval) + 'min').interpolate(method='nearest')
    resampled['date'] = resampled.index
    resampled.index = range(len(resampled))
    dataframe = merge(original, resampled, on='date', how='left')
    return dataframe


def compute_interval(dataframe: DataFrame, exchange_interval=False):
    """
        calculates the interval of the given dataframe for us
    :param dataframe:
    :param exchange_interval: should we convert the result to an exchange interval or just a number
    :return:
    """
    resampled_interval = int((dataframe['date'] - dataframe['date'].shift()).min().seconds / 60)

    if exchange_interval:
        # convert to our allowed ticker values
        from configuration import TICKER_INTERVAL_MINUTES
        converted = list(TICKER_INTERVAL_MINUTES.keys())[
            list(TICKER_INTERVAL_MINUTES.values()).index(exchange_interval)]
        if len(converted) > 0:
            return converted
        else:
            raise Exception(
                "sorry, your interval of {} is not supported in {}".format(resampled_interval, TICKER_INTERVAL_MINUTES))

    return resampled_interval

