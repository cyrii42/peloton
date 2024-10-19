import json
from datetime import datetime
from pathlib import Path
from typing import Annotated, Union

import pandas as pd
from fastapi import APIRouter, Header, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from zoneinfo import ZoneInfo

from peloton.api.templates import templates
from peloton.api.functions import (rename_columns, 
                                   construct_template_response_dataframe, 
                                   construct_template_response_pivot)
from peloton.models import PelotonWorkoutData
from peloton import PelotonProcessor

LOCAL_TZ = ZoneInfo('America/New_York')

router = APIRouter()

peloton = PelotonProcessor()

@router.get("/", response_class=HTMLResponse)
async def index(request: Request):
  return templates.TemplateResponse(request=request, name='index.html')

@router.get('/dataframe')
async def get_dataframe(request: Request, 
                        hx_request: Annotated[Union[str | None], Header()] = None):
    if hx_request:
        list_of_dicts = peloton.make_list_of_dicts()
        return construct_template_response_dataframe(request, list_of_dicts)
    else:
        df = peloton.processed_df
        df_json = json.loads(df.to_json(orient='records'))
        return JSONResponse(df_json)

@router.get('/month_table', response_class=HTMLResponse)
async def month_table(request: Request, 
                      hx_request: Annotated[Union[str | None], Header()] = None):
    df = peloton.pivots.month_table.copy()
    if hx_request:
        df = rename_columns(df)
        return construct_template_response_pivot(request, df)
    else:
        df_json = json.loads(df.to_json(orient='records'))
        return JSONResponse(df_json)
    
@router.get('/year_table', response_class=HTMLResponse)
async def year_table(request: Request, 
                     hx_request: Annotated[Union[str | None], Header()] = None):
    df = peloton.pivots.year_table.copy()
    if hx_request:
        df = rename_columns(df).drop(columns='Rides')
        return construct_template_response_pivot(request, df)
    else:
        df_json = json.loads(df.to_json(orient='records'))
        return JSONResponse(df_json)

@router.get('/totals_table')
async def totals_table(request: Request, 
                       hx_request: Annotated[Union[str | None], Header()] = None):
    df = peloton.pivots.totals_table.copy()
    if hx_request:
        df = rename_columns(df)
        return construct_template_response_pivot(request, df)
    else:
        df_json = json.loads(df.to_json(orient='records'))
        return JSONResponse(df_json)

@router.get('/favicon.ico', include_in_schema=False)
async def favicon():
    favicon_path = Path.cwd().joinpath('static', 'images', 'favicon.ico')
    return FileResponse(favicon_path)

@router.post('/refresh_data')
async def refresh_data() -> None:
    peloton.check_for_new_workouts()
    return None

@router.get('/stats_summary')
async def get_stats_summary(end_date_ts: int = None) -> dict:
    end_date_dt = (datetime.fromtimestamp(end_date_ts, tz=LOCAL_TZ) 
                   if end_date_ts else datetime.now(tz=LOCAL_TZ))
    return peloton.chart_maker.make_stats_summary(end_date_dt)

@router.get('/data')
async def get_data(workout_id: str) -> PelotonWorkoutData:
    return peloton.get_workout_object_from_id(workout_id)

@router.get('/hr_zones/')
async def get_hr_zones_chart_df(workout_id: str) -> list[dict]:
    df = peloton.chart_maker.make_hr_zones_chart_df(workout_id)
    if isinstance(df, pd.DataFrame):
        return json.loads(df.to_json(orient='records'))
    else:
        raise HTTPException(status_code=404, 
                            detail=f"No HR-zone data for workout ID: {workout_id}")

@router.get('/line_chart/')
async def get_line_chart_df(workout_id: str):
    df = (peloton.chart_maker
          .make_line_chart_df_new(workout_id)
          .reset_index(names='datetime'))
    df_json = df.to_json(orient='records')
    return json.loads(df_json)


def main():
    ...

if __name__ == '__main__':
    main()