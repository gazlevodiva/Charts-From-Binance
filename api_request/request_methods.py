import peakutils
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

from mplfinance.original_flavor  import candlestick_ohlc
from datetime import datetime


def plot_support_resistance(ohlcv, ax=None):
    # Get the closing prices of the candles
    closes = [x[4] for x in ohlcv]

    # Finding support and resistance levels using the peakutils library
    indices = peakutils.indexes(np.array(closes), thres=0.5, min_dist=30)
    support_levels = [closes[i] for i in indices if closes[i] < closes[-1]]
    resistance_levels = [closes[i] for i in indices if closes[i] > closes[-1]]

    # Draw resistance levels on the chart
    if len(resistance_levels) > 0:
        ax.plot([ohlcv[0][0], ohlcv[-1][0]], [resistance_levels[-1], resistance_levels[-1]], color='white', linestyle='--', linewidth=0.5)

    # Draw support levels on the chart
    if len(support_levels) > 0:
        ax.plot([ohlcv[0][0], ohlcv[-1][0]], [support_levels[-1], support_levels[-1]], color='white', linestyle='--', linewidth=0.5)


def extract_ohlcv(data, interval):
    ohlcv = []
    for candle in data:

        time = int(candle[0]) // 1000
        time = datetime.utcfromtimestamp(time)
        time = mdates.date2num(time)

        open_price  = float(candle[1])
        high_price  = float(candle[2])
        low_price   = float(candle[3])
        close_price = float(candle[4])
        volume      = float(candle[5])

        ohlcv.append([ time, open_price, high_price, low_price, close_price, volume])

    return ohlcv


def plot_candles(ohlcv, title, width, ax):
    fig = plt.gcf()
    fig.subplots_adjust(bottom=0.2)
    plt.xticks(rotation=45, ha='right')

    ax.set_title(title)
    plt.title(title)

    if title == "Daily":
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%d-%m'))

    if title == "Hourly":
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))

    if title == "15-Min":
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))

    if title == "5-Min":
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))

    candlestick_ohlc(ax, ohlcv, width=width, colorup='green', colordown='red', alpha=1.0)

    last_close = ohlcv[-1][4]
    last_candle_color = 'green' if last_close > ohlcv[-2][4] else 'red'

    ax.axhline(last_close, color=last_candle_color, linestyle='-', linewidth=1.0)
    ax.annotate(f'{last_close:.2f}', xy=(0, last_close), xycoords=('axes fraction', 'data'), ha='right', va='center', color=last_candle_color, fontsize=10, fontweight='bold')

    plot_support_resistance(ohlcv, ax=ax)
