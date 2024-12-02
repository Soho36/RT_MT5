import pandas as pd

list_of_orders_path = 'C:\\Users\\Liikurserv\\PycharmProjects\\RT_MT5\\list_of_orders.csv'

timestamp_to_compare = '2024-12-01 14:30:00'
current = pd.to_datetime(timestamp_to_compare)


def get_last_order_time_from_file():
    with open(list_of_orders_path, 'r', encoding='utf-8') as file:
        last_order_timestamp = pd.to_datetime(file.read())
        if pd.isna(last_order_timestamp):
            last_order_timestamp = pd.to_datetime('2024-01-01 00:00:00')
        return last_order_timestamp


last = get_last_order_time_from_file()
print(last)

diff = (current - last).total_seconds()/60
print(diff)


# if diff >= 4:
#     print('more than 4')
# else:
#     print('less than 4')
