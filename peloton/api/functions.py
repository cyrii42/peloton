import pandas as pd
from fastapi import Request
from fastapi.responses import HTMLResponse
from zoneinfo import ZoneInfo

from peloton.api.templates import templates
from peloton.models import PelotonDataFrameRow, PelotonPivotTableRow

LOCAL_TZ = ZoneInfo('America/New_York')
    
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
    rows = [PelotonPivotTableRow
            .model_validate(row)
            .model_dump(exclude_none=True, exclude='workout_id') 
            for row in df.to_dict('records')]
    return templates.TemplateResponse(request=request, 
                                      name='table.html', 
                                      context={'col_header_names': df.columns,
                                               'columns': rows[0].keys(),
                                               'rows': rows})
    
def construct_template_response_dataframe(request: Request, 
                                          list_of_dicts: list[dict], 
                                          reverse: bool = True) -> HTMLResponse:
    desired_columns = ['date', 'time', 'title', 'image_url_html_local_thumb', 'instructor_name', 
                       'total_output', 'output_per_min', 'distance', 'calories', 'effort_score']
    column_headers = ['Date', 'Time', 'Title', 'Image', 'Instructor', 'Output', 'Output/min', 
                      'Distance', 'Calories', 'Effort Score']
    
    rows: list[dict] = [PelotonDataFrameRow
                        .model_validate(row)
                        .model_dump(include=(desired_columns + ['start_time'])) 
                        for row in list_of_dicts]
    sorted_rows: list[dict] = sorted(rows, key=lambda row: row.get('start_time'), reverse=reverse)
    reordered_rows: list[dict] = [{key: row.get(key) for key in desired_columns} for row in sorted_rows]
    
    return templates.TemplateResponse(request=request, 
                                      name='table.html', 
                                      context={'col_header_names': column_headers,
                                               'columns': desired_columns,
                                               'rows': reordered_rows})


def main():
    ...


if __name__ == '__main__':
    main()