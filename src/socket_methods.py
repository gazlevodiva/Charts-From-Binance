import requests
import peakutils
import numpy as np
from typing import List
from datetime import datetime
import matplotlib.axes
import matplotlib.dates as mdates


def get_historical_candles(symbol: str, interval: str, limit: int) -> List:
    base_url = "https://api.binance.com"
    endpoint = "/api/v3/klines"

    url = f"{base_url}{endpoint}?symbol={symbol}&interval={interval}&limit={limit}"
    response = requests.get(url)
    data = response.json()

    ohlcv = []
    for candle in data:
        time = int(candle[0]) // 1000 
        time = datetime.utcfromtimestamp(time)
        time = mdates.date2num(time) 
        
        o = float(candle[1])
        h = float(candle[2])
        l = float(candle[3])
        c = float(candle[4])
        ohlcv.append((time, o, h, l, c))

    return ohlcv


def plot_support_resistance(ohlcv: List, ax: matplotlib.axes.Axes) -> None:
    # Get the closing prices of the candles
    closes = [x[4] for x in ohlcv]

    # Finding support and resistance levels using the peakutils library
    indices = peakutils.indexes(np.array(closes), thres=0.5, min_dist=30)
    support_levels = [closes[i] for i in indices if closes[i] < closes[-1]]
    resistance_levels = [closes[i] for i in indices if closes[i] > closes[-1]]

    # Draw resistance levels on the chart
    if len(resistance_levels) > 0:
        ax.plot([ohlcv[0][0], ohlcv[-1][0]],
                [resistance_levels[-1], resistance_levels[-1]],
                color='blue', linestyle='-', linewidth=0.5)

    # Drawing support levels on the chart
    if len(support_levels) > 0:
        ax.plot([ohlcv[0][0], ohlcv[-1][0]],
                [support_levels[-1], support_levels[-1]],
                color='blue', linestyle='-', linewidth=0.5)
