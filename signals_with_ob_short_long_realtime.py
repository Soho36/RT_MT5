import pandas as pd


"""
Main function analyzing price interaction with levels and long/short signals generation logics
"""


def level_rejection_signals(
        output_df_with_levels,
        sr_levels,
        level_interactions_threshold,
        max_time_waiting_for_entry
):

    n_index = None
    s_signal = None
    t_price = None
    candle_counter = 0
    levels_to_remove = []  # List to queue levels for deletion

    # Create a dictionary to track signal count per level
    level_signal_count = {i: 0 for i in range(1, len(sr_levels) + 1)}

    output_df_with_levels.reset_index(inplace=True)

    """
    Function to check if the time difference has exceeded the time limit and print the necessary information.
    Returns True if the time limit is exceeded, otherwise False.
    """
    def check_time_limit(
            m_time_waiting_for_entry,
            subs_index,
            candle_time,
            lev_inter_signal_time,
            t_diff,
            trce
    ):

        if t_diff > m_time_waiting_for_entry:
            print(
                "xxxxxxxxxxxxxxxxx\n"
                f"x {trce}: Exceeded {m_time_waiting_for_entry}-minute window "
                f"at index {subs_index}, for level {current_sr_level}\n"
                f"x Level interaction time: {lev_inter_signal_time}, \n"
                f"x Candle time: {candle_time}, \n"
                f"x Time diff: {t_diff} minutes\n"
                "xxxxxxxxxxxxxxxxx"
            )
            return True
        return False

    """
    Print triggered signals
    """
    def signal_triggered_output(
            nn_index,
            sig_time,
            tt_price,
            t_type,
            t_side,
            ss_signal
    ):

        print(
            "++++++++++++++++++++++++++\n"
            f"+ {t_type.upper()} {t_side.capitalize()} triggered at index {nn_index}, "
            f"Time: {sig_time}, "
            f"Stop-market price: {tt_price}\n"
            f"+ s_signal: {ss_signal}\n"
            "++++++++++++++++++++++++++"
        )
        print('-----------------------------------------------------------------------------------------------------')
        return ss_signal, nn_index, tt_price     # RETURNS SIGNAL FOR send_buy_sell_orders()

    sr_level_columns = output_df_with_levels.columns[8:]  # Assuming SR level columns start from the 8th column onwards
    for index, row in output_df_with_levels.iterrows():
        candle_counter += 1
        previous_close = output_df_with_levels.iloc[index - 1]['Close'] if index > 0 else None
        current_candle_close = row['Close']
        current_candle_high = row['High']
        current_candle_low = row['Low']
        current_candle_date = row['Date']
        current_candle_time = row['Time']

        subsequent_index = None  # Initialize subsequent_index

        # Loop through each level column
        for level_column in sr_level_columns:
            current_sr_level = row[level_column]
            if current_sr_level is not None:
                # Check if signal count for this level has reached the threshold
                if level_signal_count[level_column] < level_interactions_threshold:

                    # **************************************************************************************************
                    # SHORTS LOGICS BEGIN HERE
                    # **************************************************************************************************
                    # REJECTION SHORTS LOGIC:
                    # Level interaction logic
                    # print(f'{index} Analyzing candle at {current_candle_time}')
                    if previous_close is not None and previous_close < current_sr_level:
                        if current_candle_high > current_sr_level:
                            if current_candle_close < current_sr_level:
                                # Over-Under condition met for short
                                level_signal_count[level_column] += 1
                                level_interaction_signal_time = current_candle_time
                                print('-------------------------------------------------------------------------------')
                                print(f"{index} ▲▼ Short: 'Over-under' condition met, "
                                      f"Time: {current_candle_time}, "
                                      f"SR level: {current_sr_level}")

                                # Step 1: Find the first green candle (where close > open)
                                green_candle_found = False
                                green_candle_low = None
                                potential_ob_time = None
                                trade_type = 'rejection'
                                side = 'short'

                                # OB candle
                                for subsequent_index in range(index + 1, len(output_df_with_levels)):

                                    potential_ob_candle = output_df_with_levels.iloc[subsequent_index]
                                    # Convert to datetime for time calculations
                                    potential_ob_time = pd.to_datetime(potential_ob_candle['Time'])

                                    # Calculate time difference between the current potential candle
                                    # and the initial SR level interaction
                                    time_diff = (potential_ob_time - pd.to_datetime(
                                        level_interaction_signal_time)).total_seconds() / 60

                                    # Check if we've exceeded the maximum waiting time
                                    trace = 'Rejection_shorts_1'
                                    if check_time_limit(
                                            max_time_waiting_for_entry,
                                            subsequent_index,
                                            potential_ob_time,
                                            level_interaction_signal_time,
                                            time_diff,
                                            trace
                                    ):
                                        break   # Exit the loop if time limit is exceeded

                                    print(
                                        f"Looking for GREEN candle at index {subsequent_index}, "
                                        f"Time: {potential_ob_time}"
                                    )
                                    # Check if it's a green candle (close > open)
                                    if potential_ob_candle['Close'] > potential_ob_candle['Open']:
                                        print(
                                            f"○ Last GREEN candle found at index {subsequent_index}, "
                                            f"Time: {potential_ob_time}"
                                        )
                                        # Check if the green candle is below the SR level
                                        if potential_ob_candle['Close'] < current_sr_level:
                                            green_candle_low = potential_ob_candle['Low']
                                            green_candle_found = True
                                            print(
                                                f"Green candle is below the SR level at index {subsequent_index}, "
                                                f"Time: {potential_ob_time}"
                                            )
                                            print('PLACE STOPMARKET.1A')
                                            signal = f'-100+{subsequent_index}'
                                            # trigger_price = potential_ob_candle['Low']

                                            s_signal, n_index, t_price = signal_triggered_output(
                                                subsequent_index,
                                                potential_ob_time,
                                                green_candle_low,
                                                trade_type,
                                                side,
                                                signal
                                            )
                                            # break
                                        else:
                                            print(
                                                f"Green candle found, but it's not below the level. "
                                                f"Checking next candle..."
                                            )


#                   BR-D LOGIC BEGIN HERE ******************************************************************************
                    # Previous close was above level
                    if previous_close is not None and previous_close > current_sr_level:
                        if current_candle_close < current_sr_level:
                            # Over condition met for short
                            level_signal_count[level_column] += 1
                            level_interaction_signal_time = current_candle_time
                            print('-------------------------------------------------------------------------------')
                            print(f"{index} ▼ Short: 'Under' condition met, "
                                  f"Time: {current_candle_time}, "
                                  f"SR level: {current_sr_level}")

                            # Step 1: Find the first green candle (where close > open)
                            green_candle_found = False
                            green_candle_low = None
                            potential_ob_time = None
                            trade_type = 'BR-D'
                            side = 'short'

                            for subsequent_index in range(index + 1, len(output_df_with_levels)):

                                potential_ob_candle = output_df_with_levels.iloc[subsequent_index]
                                # Convert to datetime for time calculations

                                potential_ob_time = pd.to_datetime(potential_ob_candle['Time'])

                                # Calculate time difference between the current potential candle
                                # and the initial SR level interaction
                                time_diff = (potential_ob_time - pd.to_datetime(
                                    level_interaction_signal_time)).total_seconds() / 60

                                # Check if we've exceeded the maximum waiting time
                                trace = 'BR-D_shorts_1'
                                if check_time_limit(
                                        max_time_waiting_for_entry,
                                        subsequent_index,
                                        potential_ob_time,
                                        level_interaction_signal_time,
                                        time_diff,
                                        trace
                                ):
                                    break  # Exit the loop if time limit is exceeded

                                print(
                                    f"Looking for GREEN candle at index {subsequent_index}, "
                                    f"Time: {potential_ob_time}"
                                )

                                # Check if it's a green candle (close > open)
                                if potential_ob_candle['Close'] > potential_ob_candle['Open']:
                                    print(
                                        f"○ Last GREEN candle found at index {subsequent_index}, "
                                        f"Time: {potential_ob_time}"
                                    )

                                    # Check if the green candle is below the SR level
                                    if potential_ob_candle['Close'] < current_sr_level:
                                        green_candle_low = potential_ob_candle['Low']
                                        green_candle_found = True
                                        print(
                                            f"⦿ It's below the level at index {subsequent_index}, "
                                            f"Time: {potential_ob_time}"
                                        )
                                        print('PLACE STOPMARKET.1B')
                                        signal = f'-100+{subsequent_index}'
                                        # trigger_price = potential_ob_candle['Low']

                                        s_signal, n_index, t_price = signal_triggered_output(
                                            subsequent_index,
                                            potential_ob_time,
                                            green_candle_low,
                                            trade_type,
                                            side,
                                            signal
                                        )
                                        # break # Exit the loop, as we have found the valid green candle below the level

                                    else:
                                        print(
                                            f"Green candle found, but it's not below the level. "
                                            f"Checking next candle...")

                    #  ********************************************************************************************
                    #  LONGS LOGICS BEGIN HERE
                    #  ********************************************************************************************
                    # REJECTION LONGS LOGIC:
                    if previous_close is not None and previous_close > current_sr_level:
                        if current_candle_low < current_sr_level:
                            if current_candle_close > current_sr_level:
                                # Over-Under condition met for long
                                level_signal_count[level_column] += 1
                                level_interaction_signal_time = current_candle_time
                                print('-------------------------------------------------------------------------------')
                                print(f"{index} ▼▲ Long: 'Under-over' condition met, "
                                      f"Time: {current_candle_time}, "
                                      f"SR level: {current_sr_level}")

                                # Step 1: Find the first red candle (where close < open)
                                red_candle_found = False
                                red_candle_high = None
                                potential_ob_time = None
                                trade_type = 'rejection'
                                side = 'long'

                                for subsequent_index in range(index + 1, len(output_df_with_levels)):

                                    potential_ob_candle = output_df_with_levels.iloc[subsequent_index]

                                    # Convert to datetime for time calculations
                                    potential_ob_time = pd.to_datetime(potential_ob_candle['Time'])

                                    # Calculate time difference between the current potential candle
                                    # and the initial SR level interaction
                                    time_diff = (potential_ob_time - pd.to_datetime(
                                        level_interaction_signal_time)).total_seconds() / 60

                                    # Check if we've exceeded the maximum waiting time
                                    trace = 'Rejection_longs_1'
                                    if check_time_limit(
                                            max_time_waiting_for_entry,
                                            subsequent_index,
                                            potential_ob_time,
                                            level_interaction_signal_time,
                                            time_diff,
                                            trace
                                    ):
                                        break  # Exit the loop if time limit is exceeded

                                    print(
                                        f"Looking for RED candle at index {subsequent_index}, "
                                        f"Time: {potential_ob_time}"
                                    )
                                    # Check if it's a red candle (close < open)
                                    if potential_ob_candle['Close'] < potential_ob_candle['Open']:
                                        print(
                                            f"○ Last RED candle found at index {subsequent_index}, "
                                            f"Time: {potential_ob_time}"
                                        )
                                        # Check if the red candle is below the SR level
                                        if potential_ob_candle['Close'] > current_sr_level:
                                            red_candle_high = potential_ob_candle['High']
                                            red_candle_found = True
                                            print(
                                                f"Red candle is above the SR level at index {subsequent_index}, "
                                                f"Time: {potential_ob_time}"
                                            )
                                            print('PLACE STOPMARKET.2A')
                                            signal = f'100+{subsequent_index}'
                                            # trigger_price = potential_ob_candle['High']

                                            s_signal, n_index, t_price = signal_triggered_output(
                                                subsequent_index,
                                                potential_ob_time,
                                                red_candle_high,
                                                trade_type,
                                                side,
                                                signal
                                            )
                                            # break
                                        else:
                                            print(f"Red candle found, but it's not above the level. "
                                                  f"Checking next candle...")

                    # BR-O LOGIC BEGIN HERE ****************************************************************************
                    # Previous close was below level
                    if previous_close is not None and previous_close < current_sr_level:
                        if current_candle_close > current_sr_level:
                            if current_candle_close > current_sr_level:
                                # Under condition met for long
                                level_signal_count[level_column] += 1
                                level_interaction_signal_time = current_candle_time
                                print('-------------------------------------------------------------------------------')
                                print(f"{index} ▲ Long: 'Over' condition met, "
                                      f"Time: {current_candle_time}, "
                                      f"SR level: {current_sr_level}")

                                # Step 1: Find the first red candle (where close < open)
                                red_candle_found = False
                                red_candle_high = None
                                potential_ob_time = None
                                trade_type = 'BR-O'
                                side = 'Long'

                                for subsequent_index in range(index + 1, len(output_df_with_levels)):

                                    potential_ob_candle = output_df_with_levels.iloc[subsequent_index]

                                    # Convert to datetime for time calculations
                                    potential_ob_time = pd.to_datetime(potential_ob_candle['Time'])

                                    # Calculate time difference between the current potential candle
                                    # and the initial SR level interaction
                                    time_diff = (potential_ob_time - pd.to_datetime(
                                        level_interaction_signal_time)).total_seconds() / 60

                                    # Check if we've exceeded the maximum waiting time
                                    trace = 'BR-O_longs_1'
                                    if check_time_limit(
                                            max_time_waiting_for_entry,
                                            subsequent_index,
                                            potential_ob_time,
                                            level_interaction_signal_time,
                                            time_diff,
                                            trace
                                    ):
                                        break  # Exit the loop if time limit is exceeded

                                    print(
                                        f"Looking for RED candle at index {subsequent_index}, "
                                        f"Time: {potential_ob_time}"
                                    )

                                    # Check if it's a red candle (close < open)
                                    if potential_ob_candle['Close'] < potential_ob_candle['Open']:
                                        print(
                                            f"○ Last RED candle found at index {subsequent_index}, "
                                            f"Time: {potential_ob_time}"
                                        )
                                        # Check if the red candle is above the SR level
                                        if potential_ob_candle['Close'] > current_sr_level:
                                            # Candle must be above the level
                                            red_candle_high = potential_ob_candle['High']
                                            red_candle_found = True
                                            print(
                                                f"⦿ It's above the level at index {subsequent_index}, "
                                                f"Time: {potential_ob_time}"
                                            )
                                            print('PLACE STOPMARKET.2B')
                                            signal = f'100+{subsequent_index}'
                                            # trigger_price = potential_ob_candle['High']

                                            s_signal, n_index, t_price = signal_triggered_output(
                                                subsequent_index,
                                                potential_ob_time,
                                                red_candle_high,
                                                trade_type,
                                                side,
                                                signal
                                            )
                                            # break
                                        else:
                                            print(
                                                f"Red candle found, but it's not below the level. "
                                                f"Checking next candle...")

                else:
                    print('-------------------------------------------------------------------------------')
                    print(f'Level interactions number ({level_interactions_threshold}) reached '
                          f'for level {current_sr_level}')

    return (
            level_signal_count,
            s_signal,
            n_index,
            t_price,
            levels_to_remove,
            candle_counter
    )
