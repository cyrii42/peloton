import json
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
from typing import Annotated, Union
from collections import OrderedDict

from fastapi import FastAPI, Request, Header, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd

from peloton import PelotonProcessor, PelotonWorkoutData, PelotonDataFrameRow, PelotonPivotTableRow

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

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")
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
    rows = [PelotonPivotTableRow.model_validate(row) for row in df.to_dict('records')]
    return templates.TemplateResponse(request=request, 
                                        name='table.html', 
                                        context={'col_header_names': df.columns,
                                                'columns': [x[0] for x 
                                                            in rows[0].__repr_args__() 
                                                            if x[1] is not None],
                                                'rows': rows})
    
def construct_template_response_dataframe(request: Request, list_of_dicts: list[dict]) -> HTMLResponse:
    desired_columns = ['date', 'time', 'title', 'instructor_name', 'total_output', 'output_per_min', 
                        'distance', 'calories', 'effort_score']
    rows = [PelotonDataFrameRow.model_validate(row).model_dump(include=desired_columns)
            for row in list_of_dicts]
    
    def reorder_columns(row: dict) -> dict:
        ordered_dict = OrderedDict(row)

        for col in desired_columns:
            ordered_dict.move_to_end(col)
            
        return dict(ordered_dict)
    
    reordered_rows = [reorder_columns(row) for row in rows]
    return templates.TemplateResponse(request=request, 
                                        name='table.html', 
                                        context={'col_header_names': reordered_rows[0].keys(),
                                                'columns': reordered_rows[0].keys(),
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
        df = peloton.processed_df.sort_index(ascending=False)
        df_json = json.loads(df.to_json(orient='records'))
        return JSONResponse(df_json)

@app.get('/month_table', response_class=HTMLResponse)
async def month_table(request: Request, 
                      hx_request: Annotated[Union[str | None], Header()] = None):
    df = peloton.pivots.month_table.copy()
    df = rename_columns(df)
        
    if hx_request:
        return construct_template_response_pivot(request, df)

    else:
        df_json = json.loads(df.to_json(orient='records'))
        return JSONResponse(df_json)
    
    
@app.get('/year_table', response_class=HTMLResponse)
async def year_table(request: Request, 
                     hx_request: Annotated[Union[str | None], Header()] = None):
    df = peloton.pivots.year_table.copy()
    df = rename_columns(df).drop(columns='Rides')
        
    if hx_request:
        return construct_template_response_pivot(request, df)

    else:
        df_json = json.loads(df.to_json(orient='records'))
        return JSONResponse(df_json)


@app.get('/totals_table')
async def totals_table(request: Request, 
                       hx_request: Annotated[Union[str | None], Header()] = None):
    df = peloton.pivots.totals_table.copy()
    df = rename_columns(df)
        
    if hx_request:
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