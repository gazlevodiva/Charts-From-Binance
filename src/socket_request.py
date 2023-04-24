import json
import asyncio
import websockets
import matplotlib.axes
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

from datetime import datetime
from collections import deque
from typing import Any, Dict, List
from websockets.exceptions import ConnectionClosed
from mplfinance.original_flavor import candlestick_ohlc
from socket_methods import get_historical_candles
from socket_methods import plot_support_resistance


# Global variables
candles = {
    "5m":  deque(maxlen=100),
    "15m": deque(maxlen=100),
    "1h":  deque(maxlen=100),
    "1d":  deque(maxlen=100)
}

plt.style.use('dark_background')
plt.rcParams['toolbar'] = 'None'

fig, axs = plt.subplots(nrows=2, ncols=2, figsize=(16, 12))
axs = axs.flatten()

symbol = "BTCUSDT"
intervals = ["1d", "1h", "15m", "5m"]
limits = [100, 80, 50, 50]

titles = {
    "1d":  "Daily",
    "1h":  "Hourly",
    "15m": "15-Min",
    "5m":  "5-Min"
}

widths = {
    "1d":  0.6,
    "1h":  0.025,
    "15m": 0.007,
    "5m":  0.002
}


def plot_candles(ohlcv: List, title: str, width: float, ax: matplotlib.axes.Axes) -> None:
    ax.clear()
    fig = plt.gcf()
    fig.subplots_adjust(bottom=0.2)
    plt.xticks(rotation=45, ha='right')

    ax.set_title(title)

    formatter_map = {
        "Daily":  mdates.DateFormatter('%d-%m'),
        "Hourly": mdates.DateFormatter('%H:%M'),
        "15-Min": mdates.DateFormatter('%H:%M'),
        "5-Min":  mdates.DateFormatter('%H:%M'),
        "1-Min":  mdates.DateFormatter('%H:%M:%S')
    }

    ax.xaxis.set_major_formatter(formatter_map[title])

    # Build the Chart
    candlestick_ohlc(ax, ohlcv, width=width, colorup='green', colordown='red', alpha=1.0)

    # Get last candle price for color pick
    last_close = ohlcv[-1][4]
    last_candle_color = 'green' if last_close > ohlcv[-2][4] else 'red'
    ax.axhline(last_close, color=last_candle_color, linestyle='--', linewidth=1.0)

    # Set a candles side
    ha_value = 'left' if ax in axs[1::2] else 'right'
    ax.annotate(
        f'{last_close:.2f}', xy=(1.0 if ha_value == 'left' else 0, last_close),
        xycoords=('axes fraction', 'data'), ha=ha_value, va='center',
        color=last_candle_color, fontsize=10, fontweight='bold'
    )
    if ha_value == 'left':
        ax.yaxis.tick_right()


def update_plot(ohlcv: List, title: str, width: float, ax: matplotlib.axes.Axes) -> None:

    plot_candles(ohlcv=ohlcv, title=title, width=width, ax=ax)
    plot_support_resistance(ohlcv=ohlcv, ax=ax)

    plt.draw()
    plt.subplots_adjust(hspace=0.25)
    plt.tight_layout()
    plt.pause(0.1)


def on_message(message: str) -> None:
    global candles

    data: Dict[str, Any] = json.loads(message)

    if 'e' in data and data['e'] == 'kline':
        kline_data  = data['k']
        interval    = kline_data['i']
        kline_time  = int(kline_data['t']) // 1000
        kline_open  = float(kline_data['o'])
        kline_high  = float(kline_data['h'])
        kline_low   = float(kline_data['l'])
        kline_close = float(kline_data['c'])

        kline_time = datetime.utcfromtimestamp(kline_time)
        kline_time = mdates.date2num(kline_time)

        if not candles[interval] or candles[interval][-1][0] != kline_time:
            candles[interval].append((kline_time, kline_open, kline_high, kline_low, kline_close))
        else:
            candles[interval][-1] = (kline_time, kline_open, kline_high, kline_low, kline_close)

        idx = intervals.index(interval)
        ax = axs[idx]
        width = widths[interval]

        update_plot(candles[interval], titles[interval], width, ax)


def on_open(websocket: Any, time_interval: str) -> None:
    websocket.send(json.dumps({
        "method": "SUBSCRIBE",
        "params": [
            f"{symbol.lower()}@kline_{time_interval}"
        ],
        "id": 1
    }))


async def run_websocket(time_interval: str) -> None:
    websocket_url = f"wss://fstream.binance.com/ws/{symbol.lower()}@kline_{time_interval}"
    
    async with websockets.connect(websocket_url) as websocket:
        await websocket.send(json.dumps({
            "method": "SUBSCRIBE",
            "params": [
                f"{symbol.lower()}@kline_{time_interval}"
            ],
            "id": 1
        }))

        while True:
            # Stop script when canvas close
            try:
                if plt.fignum_exists(fig.number):  
                    message = await websocket.recv()
                    on_message(message)
                else:
                    break
            except ConnectionClosed:
                print(f"Connection closed for {time_interval}")
                break


if __name__ == "__main__":

    # Interactive mode
    plt.ion()  

    for idx, interval in enumerate(intervals):
        historical_candles = get_historical_candles(symbol, interval, limits[idx])
        candles[interval].extend(historical_candles)
        plot_candles(candles[interval], titles[interval], widths[interval], axs[idx])

    loop = asyncio.get_event_loop()
    tasks = [loop.create_task(run_websocket(interval)) for interval in intervals]
    loop.run_until_complete(asyncio.gather(*tasks))
    loop.close()

    plt.show()
