import winsound
import pandas as pd
from data_handling_realtime import save_order_parameters_to_file, save_list_of_orders_to_file
from datetime import datetime


def last_candle_ohlc(output_df_with_levels):
    try:
        last_candle_high = output_df_with_levels['High'].iloc[-1]
        last_candle_low = output_df_with_levels['Low'].iloc[-1]
        last_candle_close = output_df_with_levels['Close'].iloc[-1]
        ticker = output_df_with_levels['Ticker'].iloc[-1]
        return last_candle_high, last_candle_low, last_candle_close, ticker
    except IndexError:
        print("Must be at least two rows in the source file")
        return


def send_buy_sell_orders(
        t_price,
        last_signal,
        current_signal,
        n_index,
        buy_signal,
        sell_signal,
        last_candle_high,
        last_candle_low,
        last_candle_close,
        ticker,
        stop_loss_offset,
        risk_reward,
        current_order_timestamp,
        last_order_timestamp
):

    current_time = pd.to_datetime(datetime.now())
    current_order_timestamp = pd.to_datetime(current_order_timestamp)
    time_difference_current_time_order = None

    if not pd.isna(current_order_timestamp):
        time_difference_current_time_order = ((current_time - current_order_timestamp).total_seconds() / 60)

    print(f'Last signal: {last_signal}'.upper())
    print(f'Current signal: {current_signal}'.upper())
    print(f'Last order timestamp: {last_order_timestamp}')
    print(f'Current order timestamp: {current_order_timestamp}')
    print(f'Current time: {current_time}')

    # +------------------------------------------------------------------+
    # BUY ORDER
    # +------------------------------------------------------------------+
    if not pd.isna(current_order_timestamp):

        if current_signal != last_signal:
            # If time difference between current and last order is positive then it's accepted:
            if time_difference_current_time_order < 1:
                # If there is unique new signal and flag is True:
                if current_signal == f'100+{n_index}' and buy_signal:  # If there is signal and flag is True:

                    winsound.PlaySound('chord.wav', winsound.SND_FILENAME)
                    print()
                    print('▲ ▲ ▲ Buy order has been sent to MT5! ▲ ▲ ▲'.upper())

                    # ORDER PARAMETERS
                    entry_price = last_candle_high

                    # Stop Loss Price
                    stop_loss_price = round(last_candle_low - stop_loss_offset, 3)
                    risk = entry_price - stop_loss_price  # Distance between entry and stop loss

                    # Take Profit Prices (based on R:R ratios)
                    take_profit_price = round(entry_price + 1 * risk, 3)  # 1:1 R:R

                    line_order_parameters = f'{ticker},Buy,{t_price},{stop_loss_price},{take_profit_price}'  # NO WHITESPACES
                    print('line_order_parameters: ', line_order_parameters)
                    save_order_parameters_to_file(line_order_parameters)  # Located in data_handling_realtime.py

                    # line_order_parameters_to_order_list = f'{n_index},Buy,{t_price},{s_time}'
                    line_order_parameters_to_order_list = f'{current_order_timestamp}'
                    print('line_order_parameters_to_order_list: ', line_order_parameters_to_order_list)
                    save_list_of_orders_to_file(line_order_parameters_to_order_list)

                    # Reset buy_signal flag after processing order to allow the next unique signal
                    buy_signal = False  # Prevent repeated order for the same signal

                if current_signal != last_signal:
                    buy_signal, sell_signal = True, True  # Reset flags to allow the next unique signal
            else:
                winsound.PlaySound('Windows Critical Stop.wav', winsound.SND_FILENAME)
                print('Longs: Old signal. Rejected')
    else:
        print('Longs: No new orders so far')

    # +------------------------------------------------------------------+
    # SELL ORDER
    # +------------------------------------------------------------------+

    if not pd.isna(current_order_timestamp):
        if current_signal != last_signal:
            # If time difference between current and last order is positive then it's accepted:
            if time_difference_current_time_order < 1:
                # Proceed if no last order exists or if the current order timestamp is newer
                if current_signal == f'-100+{n_index}' and sell_signal:
                    # Play sound to indicate order sent
                    winsound.PlaySound('chord.wav', winsound.SND_FILENAME)
                    print()
                    print('▼ ▼ ▼ Sell order has been sent to MT5! ▼ ▼ ▼'.upper())

                    # ORDER PARAMETERS
                    entry_price = last_candle_low

                    # Stop Loss Price
                    stop_loss_price = round(last_candle_high + stop_loss_offset, 3)
                    risk = stop_loss_price - entry_price

                    # Take Profit Prices (based on R:R ratios)
                    take_profit_price = round(entry_price - 1 * risk, 3)

                    line_order_parameters = f'{ticker},Sell,{t_price},{stop_loss_price},{take_profit_price}'
                    print('line_order_parameters: ', line_order_parameters)
                    save_order_parameters_to_file(line_order_parameters)  # Save to file function

                    # line_order_parameters_to_order_list = f'{n_index},Sell,{t_price},{s_time}'
                    line_order_parameters_to_order_list = f'{current_order_timestamp}'
                    print('line_order_parameters_to_order_list: ', line_order_parameters_to_order_list)
                    save_list_of_orders_to_file(line_order_parameters_to_order_list)

                    # Reset sell_signal flag after processing order to allow the next unique signal
                    sell_signal = False  # Prevent repeated order for the same signal

                if current_signal != last_signal:
                    buy_signal, sell_signal = True, True  # Reset flags to allow the next unique signal
            else:
                winsound.PlaySound('Windows Critical Stop.wav', winsound.SND_FILENAME)
                print('Shorts: Old signal. Rejected')
    else:
        print('Shorts: No new orders so far')

    return buy_signal, sell_signal
