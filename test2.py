from datetime import datetime
import pandas as pd

current = datetime.now()
current2 = pd.to_datetime(datetime.now())
print(type(current))
print(type(current2))
print(current)
print(current2)