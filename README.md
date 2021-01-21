# Goal:AutoTrading
## Historical Bar update

- Realtime3k.py:Get historical data and keep update realtime bar.
- MarketData.py:Get the tick snapshot.
- consolidation3K: Resample realtime bar to 3k.
- TradingviewWebhookListener.py:Use ngrok to setup a webhook for tradingview alerts sent to.
- SendMarketOrder.py:The TradingviewWebhookListener.py call the function in it to send market orders through IB API.
- SendBracketOrder.py:Send the BracketOrder through IB API.
- PlaceOrder.py & Balance.py:Manully place an order through IB API and check the balance of account for testing purpose.
- GetHistorical3K_28FX.py:get 28 pairs of FX 1week 3K data.
- GetHistorical3K_Long.py:get 28 pairs of FX 12 years 3K data till no data.
- GetHistorical3K_XAUUSD.py:get gold 1 week 3k data.
- TradingBot.py:My first Python trading Robot auto trading through IB API.
- AllStrategies1.py:Put all indicators and strategies in it for TradingBot to call it or backtest to call it.

## Tradingview Alert Telegram
- *todo*
