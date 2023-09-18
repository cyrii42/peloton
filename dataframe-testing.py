from datetime import datetime
from config import py_conn, eastern_time
import pandas as pd
import csv

workouts = pd.DataFrame(py_conn.GetRecentWorkouts(2))

print(workouts.columns)
      
csv_filename = '/mnt/home-ds920/workouts.csv'

workouts.to_csv(csv_filename)