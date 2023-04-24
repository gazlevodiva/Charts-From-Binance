## Hello!

This program shows the cryptocurrency markets that you specify. In the examples there is a simple request to Binance API, also there is an example how to draw a chart which will be updated in real time using Binance WebSocket. 


The code shows 4 charts at once in the case of Binance API and Binance WebSocket. Daily, hourly, 15-minute and 5-minute charts. Also, each chart has its own size in the number of candles. You can specify your own values for the time periods and the number of candles on the chart in these places:

```Python
# request_api.py
params['limit']    = '100'
params['interval'] = '1d'
params['symbol']   = 'BTCUSDT'  
```

```Python
# socket_request.py
symbol    = 'BTCUSDT'
intervals = ['1d', '1h', '15m', '5m']
limits    = [100, 80, 50, 50]
```

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install foobar.

```bash
pip install -r requirements.txt
```

## Usage
```bash
# For WebSocket realtime charts
python src/socket_request.py

# For API request charts
python api_request/request_api.py
```

You can use this code as a basis for your experiments with Binance.