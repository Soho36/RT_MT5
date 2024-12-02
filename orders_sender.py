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

    # time_difference_current_last_order = None
    current_time = pd.to_datetime(datetime.now())
    current_order_timestamp = pd.to_datetime(current_order_timestamp)
    time_difference_current_last_order = None

    if not pd.isna(current_order_timestamp):
        time_difference_current_last_order = ((current_time - current_order_timestamp).total_seconds() / 60)

    # +------------------------------------------------------------------+
    # BUY ORDER
    # +------------------------------------------------------------------+
    print(f'Last signal: {last_signal}'.upper())
    print(f'Current signal: {current_signal}'.upper())
    print(f'Last order timestamp: {last_order_timestamp}')
    print(f'Current order timestamp: {current_order_timestamp}')
    print(f'Current time: {current_time}')

    if not pd.isna(current_order_timestamp):
        if time_difference_current_last_order < 1:
            # If time difference between current and last order is positive then it's accepted:
            if current_signal != last_signal:
                # If there is unique new signal and flag is True:
                if current_signal == f'100+{n_index}' and buy_signal:  # If there is signal and flag is True:

                    winsound.PlaySound('chord.wav', winsound.SND_FILENAME)
                    print()
                    print('▲ ▲ ▲ Buy order has been sent to MT5! ▲ ▲ ▲'.upper())

                    # ORDER PARAMETERS
                    stop_loss_price = round(last_candle_low - stop_loss_offset, 3)
                    take_profit_price = round((((last_candle_high - stop_loss_price) * risk_reward)  # R/R hardcoded
                                               + last_candle_high) + stop_loss_offset, 3)

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
        if time_difference_current_last_order < 1:
            # If time difference between current and last order is positive then it's accepted:
            if current_signal != last_signal:
                # Proceed if no last order exists or if the current order timestamp is newer
                if current_signal == f'-100+{n_index}' and sell_signal:
                    # Play sound to indicate order sent
                    winsound.PlaySound('chord.wav', winsound.SND_FILENAME)
                    print()
                    print('▼ ▼ ▼ Sell order has been sent to MT5! ▼ ▼ ▼'.upper())

                    # Order parameters
                    stop_loss_price = round(last_candle_high + stop_loss_offset, 3)
                    take_profit_price = round((last_candle_low - ((stop_loss_price - last_candle_low) * risk_reward))
                                              + stop_loss_offset, 3)

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
