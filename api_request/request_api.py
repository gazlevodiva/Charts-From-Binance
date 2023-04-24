import requests
import json
import matplotlib.pyplot as plt
from request_methods import *


if __name__ == "__main__":

    params = {}

    params['symbol'] = 'BTCUSDT'
    url = 'https://testnet.binancefuture.com/fapi/v1/klines'

    params['limit'] = '100'
    params['interval'] = '1d'    
    response = requests.get(url, params=params)
    daily_data = json.loads(response.text)

    params['limit'] = '80'
    params['interval'] = '1h'
    response = requests.get(url, params=params)
    hourly_data = json.loads(response.text)

    params['limit'] = '50'
    params['interval'] = '15m'
    response = requests.get(url, params=params)
    fifteen_min_data = json.loads(response.text)

    params['limit'] = '50'
    params['interval'] = '5m'
    response = requests.get(url, params=params)
    five_min_data = json.loads(response.text)

    daily_ohlcv       = extract_ohlcv( daily_data, '1d' )
    hourly_ohlcv      = extract_ohlcv( hourly_data, '1h' )
    fifteen_min_ohlcv = extract_ohlcv( fifteen_min_data, '15m' )
    five_min_ohlcv    = extract_ohlcv( five_min_data, '5m' )


    plt.style.use('dark_background')
    plt.rcParams['toolbar'] = 'None'

    fig, axes = plt.subplots(
        nrows   = 2, 
        ncols   = 2, 
        figsize = (16, 9)
    )

    plot_candles(
        ohlcv = daily_ohlcv, 
        title = 'Daily',
        width = 0.6, 
        ax    = axes[0, 0]
    )

    plot_candles(
        ohlcv = hourly_ohlcv, 
        title = 'Hourly', 
        width = 0.02, 
        ax    = axes[0, 1]
    )

    plot_candles(
        ohlcv = fifteen_min_ohlcv, 
        title = '15-Min', 
        width = 0.006, 
        ax    = axes[1, 0]
    )

    plot_candles(
        ohlcv = five_min_ohlcv, 
        title = '5-Min', 
        width = 0.002, 
        ax    = axes[1, 1]
    )

    fig.subplots_adjust(hspace=0.4, wspace=0.3)

    plt.tight_layout()
    plt.show()

