import json
from datetime import datetime
from pathlib import Path
from typing import Annotated, Union

import pandas as pd
from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from zoneinfo import ZoneInfo

from peloton import PelotonDataFrameRow, PelotonPivotTableRow, PelotonProcessor, PelotonWorkoutData

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

app.mount('/static', StaticFiles(directory='static', follow_symlink=True), name='static')
app.mount('/workout_images', StaticFiles(directory='data/workout_images', follow_symlink=True), name='workout_images')
templates = Jinja2Templates(directory='templates')
TemplateResponse = templates.TemplateResponse

peloton = PelotonProcessor()

peloton_data = peloton.workouts[8]
    
def rename_columns(df: pd.DataFrame) -> pd.DataFrame:
    return (df.rename(columns={
                'year': 'Year',
                'month': 'Month',
                'rides': 'Rides',
                'days': 'Days',
                'total_hours': 'Hours',
                'total_miles': 'Miles',
                'avg_calories': 'Avg. Cals',
                'avg_output/min': 'OT/min'})
            .sort_index(ascending=False))
    
def construct_template_response_pivot(request: Request, df: pd.DataFrame) -> HTMLResponse:
    rows = [PelotonPivotTableRow.model_validate(row).model_dump(exclude_none=True, exclude='workout_id') for row in df.to_dict('records')]
    return templates.TemplateResponse(request=request, 
                                      name='table.html', 
                                      context={'col_header_names': df.columns,
                                               'columns': rows[0].keys(),
                                               'rows': rows})
    
def construct_template_response_dataframe(request: Request, list_of_dicts: list[dict], reverse: bool = True) -> HTMLResponse:
    desired_columns = ['date', 'time', 'title', 'image_url_html_local_thumb', 'instructor_name', 'total_output', 'output_per_min', 'distance', 'calories', 'effort_score']
    column_headers = ['Date', 'Time', 'Title', 'Image', 'Instructor', 'Output', 'Output/min', 'Distance', 'Calories', 'Effort Score']
    
    rows: list[dict] = [PelotonDataFrameRow.model_validate(row).model_dump(include=(desired_columns + ['start_time'])) for row in list_of_dicts]
    sorted_rows: list[dict] = sorted(rows, key=lambda row: row.get('start_time'), reverse=reverse)
    reordered_rows: list[dict] = [{key: row.get(key) for key in desired_columns} for row in sorted_rows]
    
    return templates.TemplateResponse(request=request, 
                                      name='table.html', 
                                      context={'col_header_names': column_headers,
                                               'columns': desired_columns,
                                               'rows': reordered_rows})

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
  return templates.TemplateResponse(request=request, name='index.html')

@app.get('/dataframe')
async def get_dataframe(request: Request, 
                        hx_request: Annotated[Union[str | None], Header()] = None):
    
    if hx_request:
        list_of_dicts = peloton.make_list_of_dicts()
        return construct_template_response_dataframe(request, list_of_dicts)

    else:
        df = peloton.processed_df
        df_json = json.loads(df.to_json(orient='records'))
        return JSONResponse(df_json)

@app.get('/month_table', response_class=HTMLResponse)
async def month_table(request: Request, 
                      hx_request: Annotated[Union[str | None], Header()] = None):
    df = peloton.pivots.month_table.copy()
            
    if hx_request:
        df = rename_columns(df)
        return construct_template_response_pivot(request, df)

    else:
        df_json = json.loads(df.to_json(orient='records'))
        return JSONResponse(df_json)
    
    
@app.get('/year_table', response_class=HTMLResponse)
async def year_table(request: Request, 
                     hx_request: Annotated[Union[str | None], Header()] = None):
    df = peloton.pivots.year_table.copy()
        
    if hx_request:
        df = rename_columns(df).drop(columns='Rides')
        return construct_template_response_pivot(request, df)

    else:
        df_json = json.loads(df.to_json(orient='records'))
        return JSONResponse(df_json)


@app.get('/totals_table')
async def totals_table(request: Request, 
                       hx_request: Annotated[Union[str | None], Header()] = None):
    df = peloton.pivots.totals_table.copy()
        
    if hx_request:
        df = rename_columns(df)
        return construct_template_response_pivot(request, df)

    else:
        df_json = json.loads(df.to_json(orient='records'))
        return JSONResponse(df_json)


@app.get('/favicon.ico', include_in_schema=False)
async def favicon():
    favicon_path = Path.cwd().joinpath('static', 'images', 'favicon.ico')
    return FileResponse(favicon_path)

@app.post('/refresh_data')
async def refresh_data() -> None:
    peloton.check_for_new_workouts()
    return None

@app.get('/stats_summary')
async def get_stats_summary(end_date_ts: int = None) -> dict:
    end_date_dt = (datetime.fromtimestamp(end_date_ts, tz=LOCAL_TZ) 
                   if end_date_ts else datetime.now(tz=LOCAL_TZ))
    return peloton.chart_maker.make_stats_summary(end_date_dt)

@app.get('/data')
async def get_data(workout_id: str) -> PelotonWorkoutData:
    return peloton.get_workout_object_from_id(workout_id)

@app.get('/hr_zones/')
async def get_hr_zones_chart_df(workout_id: str) -> list[dict]:
    df = peloton.chart_maker.make_hr_zones_chart_df(workout_id)
    if isinstance(df, pd.DataFrame):
        return json.loads(df.to_json(orient='records'))
    else:
        raise HTTPException(status_code=404, 
                            detail=f"No HR-zone data for workout ID: {workout_id}")

@app.get('/line_chart/')
async def get_line_chart_df(workout_id: str):
    df = (peloton.chart_maker
          .make_line_chart_df_new(workout_id)
          .reset_index(names='datetime'))
    df_json = df.to_json(orient='records')

    return json.loads(df_json)