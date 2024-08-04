import requests
import pandas as pd
from datetime import datetime
from zoneinfo import ZoneInfo

ts_now = int(round(datetime.now(tz=ZoneInfo('America/New_York')).timestamp()))

# test_ts = ts_now
# test_dt = datetime.fromtimestamp(test_ts)
# print(test_dt)

url = f"https://pelotondata.cyrii42.net/stats_summary/?end_date={ts_now}"

print(url)

response = requests.get(url)

resp = response.json()

print(resp)

# df = pd.DataFrame(resp)#.astype({'datetime': 'datetime64[ms]'}).set_index('datetime')

# print(df)

# dt = datetime.now(tz=ZoneInfo('America/New_York')).isoformat()
# print(dt)