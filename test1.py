import sqlite3
import pandas as pd

# Create SQLite database
sql_conn = sqlite3.connect("/home/zvaughan/docker/peleton_workouts.db")

# Create Pandas DataFrame from existing table
db_dataframe = pd.read_sql("SELECT * from peleton", sql_conn)

print(db_dataframe.tail)