import MetaTrader5 as mt
import pandas as pd
import time

def check_closing(symbol_name, ma, timeframe, direction, candle_count):
    market_bars = mt.copy_rates_from_pos(symbol_name, timeframe, 1, ma)
    bars_df = pd.DataFrame(market_bars)

    last_low = round(bars_df.iloc[-2].low, 5)
    last_high = round(bars_df.iloc[-2].high, 5)

    if direction == "buyt" or direction == "sellt":
        time.sleep(60*candle_count)
        market_bars = mt.copy_rates_from_pos(symbol_name, timeframe, 1, ma)
        bars_df = pd.DataFrame(market_bars)

    last_close = round(bars_df.iloc[-1].close, 5)
    ma_value = round(bars_df.close.mean(), 5)

    if direction == " ":
        if last_close > ma_value:
            direction = "buyc"
        elif last_close < ma_value:
            direction = "sellc"
    elif direction == "buyt":
        if last_close > ma_value:
            direction = "buy"
            #return direction, ma_value, last_close, last_low, last_high
        elif last_close < ma_value:
            direction = " "
    elif direction == "sellt":
        if last_close < ma_value:
            direction = "sell"
            #return direction, ma_value, last_close, last_low, last_high
        elif last_close > ma_value:
            direction = " "

    return direction, ma_value, last_close, last_low, last_high

def check_signal(symbol_name, ma, timeframe, direction):
    market_bars = mt.copy_rates_from_pos(symbol_name, timeframe, 1, ma)
    bars_df = pd.DataFrame(market_bars)

    current_price = mt.symbol_info_tick(symbol_name)._asdict()
    current_price = round(current_price["ask"], 5)
    ma_value = round(bars_df.close.mean(), 5)

    if current_price == ma_value or current_price < ma_value:
        if direction == "buyc":
            direction = "buyt"
    elif current_price == ma_value or current_price > ma_value:
        if direction == "sellc":
            direction = "sellt"
    return direction

def open_order(symbol, direction, volume, deviation, sl, tp_per):
    
    price_tick = mt.symbol_info_tick(symbol)

    if direction == "buy":
        price_tick = price_tick.ask
        type_order = 0
        tp = ((price_tick - sl) * tp_per) + price_tick
    elif direction == "sell":
        price_tick = price_tick.bid
        type_order = 1
        tp = ((sl - price_tick) * tp_per) + price_tick
    
    request = {
        "action": mt.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": volume,
        "type": type_order,
        "price": price_tick,
        "deviation": deviation,
        "magic": 100,
        "tp"   : round(tp, 5),
        "sl"   : round(sl, 5),
        "comment": "Placing Order",
        "type_time": mt.ORDER_TIME_GTC,
        "type_filling": mt.ORDER_FILLING_IOC,
    }
    order_result = mt.order_send(request)
    print(order_result)

    return order_result

SYMBOL_NAME = "EURUSD"
MA = 10
VOLUME = 1.0
TIMEFRAME = mt.TIMEFRAME_M1
DEVIATION = 29
TP_PER = 1.3
direction = " "
CANDLE_COUNT = 1

Login = 0
Password = ""
Server = ""

mt.initialize(login = Login, password = Password, server = Server)

while True:
    num_positions = int(mt.positions_total())
    if num_positions <= 0:
        open_orders = True
    elif num_positions > 0:
        open_orders = False

    if open_orders:
        if direction == " ":
            direction, ma_value, last_close, last_low, last_high = check_closing(SYMBOL_NAME, MA, TIMEFRAME, " ", CANDLE_COUNT)
        elif direction == "buyc" or direction == "sellc":
            direction = check_signal(SYMBOL_NAME, MA, TIMEFRAME, direction)
        elif direction == "buyt" or direction == "sellt":
            direction, ma_value, last_close, last_low, last_high = check_closing(SYMBOL_NAME, MA, TIMEFRAME, direction, CANDLE_COUNT)
        elif direction == "buy":
            open_order(SYMBOL_NAME, direction, VOLUME, DEVIATION, last_low, TP_PER)
            print("Buy Order Opened")
            direction = " "
        elif direction == "sell":
            open_order(SYMBOL_NAME, direction, VOLUME, DEVIATION, last_high, TP_PER)
            print("Sell Order Opened")
            direction = " "

    print(f"No. of Positions (OPENED): {num_positions}")
    print(f"Symbol: {SYMBOL_NAME}")
    print(f"Direction: {direction}")
    print(f"SMA: {ma_value}")
    print(f"Last_close: {last_close}")
    print("------------------------------")

    time.sleep(1)
