import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

# Create SQLite database
# sql_conn = sqlite3.connect(str(datetime.now().strftime("%Y-%m-%d_%H-%M")) + "peleton_data_test.db")
sql_conn = sqlite3.connect("/home/zvaughan/docker/peleton_workouts.db")

db_dataframe = pd.read_sql("SELECT * from peleton", sql_conn, index_col='start_time_iso', parse_dates=['start_time_iso', 'start_time_local'])

s = db_dataframe['instructor'].value_counts()

plt.pie(s, labels=s.index)

plt.savefig('./test.png')