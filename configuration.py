TEST_EXCHANGE=True
API_KEY=''
API_SECRET=''

AMOUNT_MONEY_TO_TRADE = 100  #$
LEVERAGE = 10

TIMEFRAME = '1m'

PAIR = 'XBTUSD'

TICKER_INTERVAL_MINUTES = {
    '1m': 1,
    '5m': 5,
    '1h': 60,
    '1d': 1440,
}

time_to_wait_new_trade = {'1m': 60,
                          '5m': 60*5,
                          '1h': 60*60,
                          '1d': 60*60*24}
