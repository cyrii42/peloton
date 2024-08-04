import json
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd

from peloton import PelotonProcessor, PelotonWorkoutData

LOCAL_TZ = ZoneInfo('America/New_York')

origins = ["*"]

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# app.mount("/static", StaticFiles(directory="static"), name="static")

peloton = PelotonProcessor()

peloton_data = peloton.workouts[8]

# @app.get('/favicon.ico', include_in_schema=False)
# async def favicon():
#     favicon_path = Path.cwd().joinpath('static', 'images', 'favicon.ico')
#     return FileResponse(favicon_path)

@app.post('/refresh_data')
async def refresh_data() -> None:
    peloton.check_for_new_workouts()
    return None

@app.get('/stats_summary')
async def get_stats_summary(end_date: int) -> dict:
    end_date_dt = datetime.fromtimestamp(end_date, tz=LOCAL_TZ)
    return peloton.chart_maker.make_stats_summary(end_date_dt)

@app.get('/data')
async def get_data(workout_id: str) -> PelotonWorkoutData:
    return peloton.get_workout_object_from_id(workout_id)

@app.get('/dataframe')
async def get_dataframe() -> list[dict]:
    df = peloton.processed_df
    df_json = df.to_json(orient='records')
    
    return json.loads(df_json)

@app.get('/year_table')
async def get_year_table() -> list[dict]:
    df = peloton.pivots.year_table.copy()
    df = df.sort_index(ascending=False)
    df_json = df.to_json(orient='records')

    return json.loads(df_json)

@app.get('/month_table')
async def get_month_table() -> list[dict]:
    df = peloton.pivots.month_table.copy()
    df = (df
          .rename(columns={'avg_output/min': 'avg_output_min'})
          .sort_index(ascending=False))
    df_json = df.to_json(orient='records')

    return json.loads(df_json)

@app.get('/totals_table')
async def get_totals_table() -> list[dict]:
    df = peloton.pivots.totals_table.copy()
    df = (df
          .rename(columns={
                'month': 'Month',
                'rides': 'Rides',
                'total_hours': 'Hours',
                'total_miles': 'Miles',
                'avg_calories': 'Avg. Cals',
                'avg_output/min': 'OT/min'})
          .sort_index(ascending=False))
    df_json = df.to_json(orient='records')

    return json.loads(df_json)

@app.get('/hr_zones/')
async def get_hr_zones_chart_df(workout_id: str) -> list[dict]:
    df = peloton.chart_maker.make_hr_zones_chart_df(workout_id)
    if isinstance(df, pd.DataFrame):
        return json.loads(df.to_json(orient='records'))
    else:
        raise HTTPException(status_code=404, detail=f"No HR zone data for workout ID: {workout_id}")

@app.get('/line_chart/')
async def get_line_chart_df(workout_id: str):
    df = (peloton.chart_maker
          .make_line_chart_df_new(workout_id)
          .reset_index(names='datetime'))
    df_json = df.to_json(orient='records')

    return json.loads(df_json)