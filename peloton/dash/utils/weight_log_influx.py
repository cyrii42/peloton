from datetime import date, datetime, timedelta

import pandas as pd
import sqlalchemy as db
from influxdb_client import InfluxDBClient

from peloton.constants import (EASTERN_TIME, INFLUX_ORG, INFLUX_TOKEN_HASS,
                               INFLUX_URL)


def get_range_start_str(days:int=3) -> str:
    today = date.today()
    today_at_midnight = datetime(today.year, today.month, today.day, hour=0, minute=0, second=0, tzinfo=EASTERN_TIME) 
    days_to_subtract = days
    range_start_time = today_at_midnight - timedelta(days=days_to_subtract)
    range_start_time_str = range_start_time.isoformat(sep='T', timespec='seconds')
    return range_start_time_str

def influx_query_weight(range_start_time_str: str) -> pd.DataFrame:
    influx_query = (
        f"import \"timezone\""
        f"import \"interpolate\""
        f"option location = timezone.location(name: \"America/New_York\")"
        f"from(bucket: \"homeassistant\")"
        f"  |> range(start: {range_start_time_str})"
        f"  |> filter(fn: (r) => r[\"entity_id\"] == \"zmv_weight\")"
        f"  |> filter(fn: (r) => r[\"_field\"] == \"value\")"
        f"  |> interpolate.linear(every: 1d)"
        f"  |> aggregateWindow(every: 1d, fn: last, timeSrc: \"_start\", createEmpty: true)"
        f"  |> pivot(rowKey:[\"_time\"], columnKey: [\"_field\"], valueColumn: \"_value\")"
    )

    with InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN_HASS, org=INFLUX_ORG) as client:
        df_influx = client.query_api().query_data_frame(influx_query)
        
    return df_influx