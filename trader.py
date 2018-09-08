class Trader():
    def __init__(self, client, strategy, money_to_trade=100, leverage=5):
        self.client = client
        self.strategy = strategy
        # self.pair = pair
        self.money_to_trade = money_to_trade
        self.leverage = leverage

    def execute_trade(self):
        prediction = self.strategy.predict()

        print(f"Last prediction: {prediction}")

        try:
            if prediction == 1:  # buy

                res = self.client.Position.Position_get(
                    filter="{\"symbol\":\"XBTUSD\"}",
                    # filter="{\"symbol\":\"{}\"}".format(self.pair),
                    columns="[\"currentQty\"]"
                ).result()

                if res[0][0]['execSellQty'] > 0:
                    close = self.client.Order.Order_closePosition(
                        symbol="XBTUSD"
                        # symbol=self.pair
                    ).result()

                buy = self.client.Order.Order_new(
                    symbol="XBTUSD",
                    # symbol=self.pair,
                    side="Buy",
                    orderQty=self.money_to_trade * self.leverage,
                ).result()

            if prediction == 2:  # sell

                res = self.client.Position.Position_get(
                    filter="{\"symbol\":\"XBTUSD\"}",
                    # filter="{\"symbol\":\"{}\"}".format(self.pair),
                    columns="[\"currentQty\"]"
                ).result()

                if res[0][0]['execBuyQty'] > 0:
                    close = self.client.Order.Order_closePosition(
                        symbol="XBTUSD"
                        # symbol=self.pair
                    ).result()

                sell = self.client.Order.Order_new(
                    symbol="XBTUSD",
                    # symbol=self.pair,
                    side="Sell",
                    orderQty=self.money_to_trade * self.leverage,
                ).result()

            if prediction == 3:  # tp hit close any position

                res = self.client.Position.Position_get(
                    filter="{\"symbol\":\"XBTUSD\"}",
                    columns="[\"currentQty\"]"
                ).result()

                if res[0][0]['currentQty'] != 0:
                    close = self.client.Order.Order_closePosition(
                        symbol="XBTUSD"
                    ).result()

            # if prediction == 0:
            #     res = self.client.Position.Position_get(
            #         filter="{\"symbol\":\"XBTUSD\"}",
            #         columns="[\"currentQty\"]"
            #     ).result()
            #     print(res[0][0]['currentQty'])

        except Exception:
            print("Something goes wrong!")

        return
