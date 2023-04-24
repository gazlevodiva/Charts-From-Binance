import websocket
import requests
import json
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from collections import deque
from datetime import datetime
from mplfinance.original_flavor  import candlestick_ohlc


candles = deque(maxlen=50)

plt.style.use('dark_background')
fig, ax = plt.subplots(figsize=(10, 5))

symbol = "BTCUSDT"
interval = "1d"
limit = 50

if interval == "5m":
    title = "5-Min"
    width = 0.005

if interval == "15m":
    title = "15-Min"
    width = 0.01

if interval == "1h":
    title = "Hourly"
    width = 0.02

if interval == "1d":
    title = "Daily"
    width = 0.6
        


def get_historical_candles(symbol, interval, limit):
    base_url = "https://api.binance.com"
    endpoint = "/api/v3/klines"

    url = f"{base_url}{endpoint}?symbol={symbol}&interval={interval}&limit={limit}"
    response = requests.get(url)
    data = response.json()

    ohlcv = []
    for candle in data:

        time = int(candle[0]) // 1000  # получаем время в секундах
        time = datetime.utcfromtimestamp(time)  # преобразуем время в формат datetime
        time = mdates.date2num(time) 
        
        o = float(candle[1])
        h = float(candle[2])
        l = float(candle[3])
        c = float(candle[4])
        ohlcv.append((time, o, h, l, c))

    return ohlcv


def plot_candles(ohlcv, title, width, ax):
    ax.clear()
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

    if title == "1-Min":
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))

    candlestick_ohlc(ax, ohlcv, width=width, colorup='green', colordown='red', alpha=1.0)

    # Находим цену закрытия последней свечи
    last_close = ohlcv[-1][4]

    # Получаем цвет последней свечи
    last_candle_color = 'green' if last_close > ohlcv[-2][4] else 'red'

    # Рисуем пунктирную линию на уровне цены закрытия соответсвующего цвета
    ax.axhline(last_close, color=last_candle_color, linestyle='--', linewidth=1.0)

    # Добавляем текст с текущей ценой на ось Y
    ax.annotate(f'{last_close:.2f}', xy=(0, last_close), xycoords=('axes fraction', 'data'), ha='right', va='center', color=last_candle_color, fontsize=10, fontweight='bold')


def update_plot(ohlcv):
    plot_candles(ohlcv, title=title, width=width, ax=ax)
    plt.draw()
    plt.pause(0.1)

def on_message(ws, message):
    global candles

    data = json.loads(message)

    if 'e' in data and data['e'] == 'kline':
        kline_data = data['k']
        kline_time = int(kline_data['t']) // 1000
        kline_open = float(kline_data['o'])
        kline_high = float(kline_data['h'])
        kline_low = float(kline_data['l'])
        kline_close = float(kline_data['c'])

        kline_time = datetime.utcfromtimestamp(kline_time)
        kline_time = mdates.date2num(kline_time)

        if not candles or candles[-1][0] != kline_time:
            candles.append((kline_time, kline_open, kline_high, kline_low, kline_close))
        else:
            candles[-1] = (kline_time, kline_open, kline_high, kline_low, kline_close)

        update_plot(candles)

def on_open(ws):
    ws.send(json.dumps({
        "method": "SUBSCRIBE",
        "params": [
            f"{symbol.lower()}@kline_{interval}"
        ],
        "id": 1
    }))


if __name__ == "__main__":
    
    historical_candles = get_historical_candles(symbol, interval, limit)
    candles.extend(historical_candles)

    plot_candles(candles, title=title, width=width, ax=ax)

    websocket.enableTrace(True)
    ws = websocket.WebSocketApp(f"wss://fstream.binance.com/ws/{symbol.lower()}@kline_{interval}", on_message=on_message, on_open=on_open)
    ws.run_forever()
    plt.show()