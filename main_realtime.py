from data_handling_realtime import (get_dataframe_from_file, get_levels_from_file, leave_only_last_line,
                                    remove_expired_levels, get_last_order_time_from_file)
from price_levels_manual_realtime import process_levels
from signals_with_ob_short_long_realtime import level_rejection_signals
from orders_sender import last_candle_ohlc, send_buy_sell_orders
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

import time
import os

# ************************************** ORDER PARAMETERS *******************************************************

volume_value = 1                    # 1000 MAX for stocks. Used only in AU3 (MT5 assigns volume itself)
risk_reward = 1                     # Risk/Reward ratio (Not used with multiple TP-s)
stop_loss_offset = 1                # Is added to SL for Shorts and subtracted for Longs (can be equal to spread)

# hardcoded_sr_levels = [('2024-11-02 16:19:00', 69245.00), ('2024-11-02 16:19:00', 69167.00)]  # Example support levels

level_interactions_threshold = 3     # Times
max_time_waiting_for_entry = 20      # Minutes
# reverse_trades = False
level_lifetime_minutes = 420         # Minutes

clear_csv_before_start = True
# **************************************************************************************************************

# LIIKURI PATHS
path_ohlc = \
    'C:\\Users\\Liikurserv\\AppData\\Roaming\\MetaQuotes\\Terminal\\1D0E83E0BCAA42603583233CF21A762C\\MQL5\\Files'
file = 'OHLCVData_475.csv'

# SILLAMAE PATHS
# path = 'C:\\Users\\Vova deduskin lap\\AppData\\Roaming\\MetaQuotes\\Terminal\\D0E8209F77C8CF37AD8BF550E51FF075\\MQL5\\Files'
# file = 'OHLCVData_475.csv'
# SILLAMAE PATHS

buy_signal_flag = True                    # MUST BE TRUE BEFORE ENTERING MAIN LOOP
sell_signal_flag = True                   # MUST BE TRUE BEFORE ENTERING MAIN LOOP
last_signal = None                              # Initiate last signal

# LEAVE ONLY FIRST OHLC IN CSV BEFORE CREATING DATAFRAME
if clear_csv_before_start:
    leave_only_last_line()
    print('Csv first lines cleared before starting script'.upper())

"""
Watchdog module monitors csv changes for adding new OHLC row and trigger main.py function calls 
only when new data is added to the CSV
"""


class CsvChangeHandler(FileSystemEventHandler):
    print("\nScript successfully started. Waiting for first candle to close...".upper())

    def on_modified(self, event):
        global buy_signal_flag, sell_signal_flag, last_signal
        # print(f"File modified: {event.src_path}")  # This should print on any modification
        if not event.src_path == os.path.join(path_ohlc, file):  # CSV file path
            return
        print("CSV file updated; triggering function calls...")
        # Call a function that contains all main calls
        buy_signal_flag, sell_signal_flag, last_signal = run_main_functions(
            buy_signal_flag, sell_signal_flag, last_signal
        )


def run_main_functions(b_s_flag, s_s_flag, l_signal):
    print('\n********************************************************************************************************')
    print('\n********************************************************************************************************')

    # GET DATAFRAME FROM LOG
    dataframe_from_log, first_date2 = get_dataframe_from_file(max_time_waiting_for_entry)
    # print('\nget_dataframe_from_file: \n', dataframe_from_log[-10:])

    # GET LEVELS FROM FILE
    hardcoded_sr_levels = get_levels_from_file()
    print('hardcoded_sr_levels from file: \n', hardcoded_sr_levels)

    # PRICE LEVELS
    (
        levels_startpoints_to_chart,
        levels_endpoints_to_chart,
        level_discovery_signals_series_out,
        sr_levels,
        output_df_with_levels
    ) = process_levels(
        dataframe_from_log,
        hardcoded_sr_levels
    )
    print('\noutput_df_with_levels2: \n', output_df_with_levels)  # [-10:]
    # SIGNALS
    (
        over_under_counter,
        s_signal,
        n_index,
        t_price,
        levels_to_remove,
        candle_counter,
        s_time
    ) = level_rejection_signals(
        output_df_with_levels,
        sr_levels,
        level_interactions_threshold,
        max_time_waiting_for_entry
    )

    print(f'Candles processed since start: {candle_counter}')

    # Remove the level which has been hit threshold

    remove_expired_levels(level_lifetime_minutes, dataframe_from_log)

    # LAST CANDLE OHLC (current OHLC)
    (
        last_candle_high,
        last_candle_low,
        last_candle_close,
        ticker
     ) = last_candle_ohlc(
        output_df_with_levels
    )

    # GET LAST ORDER TIMESTAMP FUNCTION
    last_order_timestamp = get_last_order_time_from_file()

    # SEND ORDERS
    (
        b_s_flag,
        s_s_flag,
    ) = send_buy_sell_orders(
        t_price,
        l_signal,
        s_signal,
        n_index,
        b_s_flag,
        s_s_flag,
        last_candle_high,
        last_candle_low,
        last_candle_close,
        ticker,
        stop_loss_offset,
        risk_reward,
        s_time,
        last_order_timestamp
    )

    l_signal = s_signal
    return b_s_flag, s_s_flag, l_signal


if __name__ == "__main__":
    try:
        event_handler = CsvChangeHandler()
        observer = Observer()
        observer.schedule(event_handler, path_ohlc, recursive=False)  # CSV folder path
        observer.start()
    except FileNotFoundError as e:
        print(f'Error: {e}. \nPlease check that the path: {path_ohlc} exists and is accessible.')

    else:
        # Run the observer only if no exceptions were raised
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print()
            print('Program stopped manually'.upper())
            observer.stop()
        observer.join()
