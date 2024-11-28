from datetime import datetime, timedelta

levels_path = 'E:\\YandexDisk\\Desktop_Zal\\44.txt'


def get_levels_from_file():
    updated_lines = []
    levels = []

    with open(levels_path, 'r', encoding='utf-8') as file:
        for line in file:
            parts = line.strip().split(',')

            if len(parts) == 2:
                # Properly formatted line
                timestamp = parts[0].strip()
                level = float(parts[1].strip())
            else:
                # Line with only a level; add current timestamp
                current_time = datetime.now()
                # Add 1 minute if there are any seconds
                # if current_time.second > 0:
                #     current_time += timedelta(minutes=1)
                # Set seconds to 00
                current_time = current_time.replace(second=0, microsecond=0)

                timestamp = current_time.strftime('%Y-%m-%d %H:%M:%S')
                level = float(parts[0].strip())

            # Add the formatted line to the update list
            updated_lines.append(f"{timestamp}, {level}\n")
            levels.append((timestamp, level))

    # Rewrite the file with only properly formatted lines
    with open(levels_path, 'w', encoding='utf-8') as file:
        file.writelines(updated_lines)

    return levels


get = get_levels_from_file()
print(get)