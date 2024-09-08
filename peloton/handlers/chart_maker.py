import random
from datetime import timedelta, datetime

import pandas as pd
import plotly.express as px
import plotly.graph_objs as go

from peloton.models import PelotonWorkoutData
from peloton.handlers import PelotonPivots
from peloton.helpers.constants import EASTERN_TIME

STRIVE_SCORE_COLOR_MAP = {
    'Zone 1': '#88cfa5',
    'Zone 2': '#b7c95d',
    'Zone 3': '#fbca3f',
    'Zone 4': '#fc7f10',
    'Zone 5': '#ff465a'
}

def main():
    pass

class PelotonChartMaker():
    def __init__(self, workouts: list[PelotonWorkoutData], pivots: PelotonPivots):
        self.workouts = workouts
        self.pivots = pivots
        self.workouts_by_id = {workout.summary.workout_id: workout for workout in workouts}
        self.stats_summary = self.make_stats_summary()

    def get_achievements(self) -> pd.DataFrame:
        achievements = [workout.summary_raw['achievement_templates'] for workout in self.workouts 
                        if len(workout.summary_raw['achievement_templates']) > 0]
        return pd.DataFrame([item for row in achievements for item in row])

    def make_stats_summary(self, end_date: datetime = datetime.now(tz=EASTERN_TIME)) -> dict:
        '''
        Total workouts, total workout time, total calories, total strive score

        Total active days, difference in total active dates as compared to previous 30-day period

        Week streak
        ''' 
        DAYS = 30
        output_dict = {}

        end_date = end_date.date()
        start_date = end_date - timedelta(days=(DAYS))  # was (DAYS - 1) (changed on 8/14/2024)
        workouts = [workout for workout in self.workouts 
                             if workout.summary.start_time.date() >= start_date
                             and workout.summary.start_time.date() <= end_date]

        output_dict['total_workouts'] = len(workouts)
        output_dict['total_workout_days'] = len(set([workout.summary.start_time.date() for workout in workouts]))

        total_duration = sum([workout.summary.ride.ride_duration for workout in workouts])
        output_dict['total_duration'] = total_duration
        output_dict['total_duration_str'] = f"{total_duration // 3600} hr {total_duration % 3600 // 60} min"
        output_dict['total_hours'] = total_duration / 3600

        workout_metrics_summaries = [workout.metrics.summaries for workout in workouts]
        output_dict['total_calories'] = sum([x[2].value for x in workout_metrics_summaries])

        strive_score_total = sum([workout.metrics.effort_zones.effort_score for workout in workouts 
                                       if workout.metrics.effort_zones is not None])
        output_dict['total_strive_score'] = strive_score_total

        active_weekly_streak = 0
        last_monday = (end_date - timedelta(days=end_date.weekday()))
        test_date = last_monday
        while True:
            if len([workout for workout in self.workouts
                    if workout.summary.start_time.date() >= test_date
                    and workout.summary.start_time.date() <= (test_date + timedelta(weeks=1))]) > 0:
                active_weekly_streak += 1
                test_date = test_date - timedelta(weeks=1)
            elif test_date == last_monday:
                test_date = test_date - timedelta(weeks=1)
            else:
                break
        output_dict['active_weekly_streak'] = active_weekly_streak

        return output_dict

    def make_workouts_chart(self) -> go.Figure:
        df = self.pivots.month_table
        fig = px.bar(df, 
                     x=df['month'], 
                     y=df['total_miles'])
        return fig

    def make_hr_zones_pie_chart(self, workout_id: str) -> go.Figure | None:
        df = self.make_hr_zones_chart_df(workout_id)
        if df is None:
            return None

        fig = px.pie(df, 
                     values='pct', 
                     labels=None,
                     names='display_name', 
                     hole=0.5, 
                     color='display_name', 
                     color_discrete_map=STRIVE_SCORE_COLOR_MAP)
        fig.update_layout(showlegend=True)
        fig.update_traces(textinfo='none')

        return fig

    def make_hr_zones_bar_chart(self, workout_id: str) -> go.Figure | None:
        df = self.make_hr_zones_chart_df(workout_id)
        if df is None:
            return None

        fig = px.bar(df.sort_index(ascending=False), 
                      x='duration', 
                      y='display_name', 
                      color='display_name', 
                      color_discrete_map=STRIVE_SCORE_COLOR_MAP, 
                      template='simple_white')
        fig.update_layout(showlegend=False)

        return fig

    def make_hr_zones_chart_df(self, workout_id: str) -> pd.DataFrame | None:
        workout = self.workouts_by_id[workout_id]
        if len(workout.metrics.metrics) < 5:
            return None

        hr_zones = [hr_zone.model_dump() for hr_zone in workout.metrics.metrics[4].zones]
        df = pd.DataFrame(hr_zones)

        def get_ss_multiplier(slug: str) -> int:
            ss_multipliers = {'zone1': 1, 'zone2': 2, 'zone3': 4, 'zone4': 8, 'zone5': 8}
            return ss_multipliers[slug]

        df['ss_multiplier'] = df['slug'].apply(get_ss_multiplier)
        df['strive_score'] = (df['duration'] * (df['ss_multiplier'] * 0.3))/60
        df['pct'] = (df['duration'] / df['duration'].sum()) * 100

        return df

    def make_line_charts(self, workout_id: str) -> list[go.Figure]:
        metric_types = ['Output', 'Cadence', 'Resistance', 'Speed', 'Heart Rate']

        df_list = self.make_line_chart_dfs(workout_id)
        fig_list = []
        for idx, df in enumerate(df_list):
            fig = px.line(df, 
                            x=df.index, 
                            y=df.columns, 
                            labels={'index': 'Time', 'value': metric_types[idx]},
                            color_discrete_map={'output': 'darkblue',
                                                'cadence': 'green',
                                                'resistance': 'orange',
                                                'speed': 'purple',
                                                'heart_rate': 'red'})
            fig.update_layout(showlegend=False)
            fig.update_xaxes(tickformat='%-I:%M %p')
            fig_list.append(fig)
        return fig_list

    def make_line_chart_dfs(self, workout_id: str) -> list[pd.DataFrame]:
        workout = self.workouts_by_id[workout_id]
        metrics = {'output': 'watts',
                   'cadence': 'rpm',
                   'resistance': '%',
                   'speed': 'mph',
                   'heart_rate': 'bpm'}

        print(f"Start Time: {workout.summary.start_time.strftime('%a, %b %-d, %Y @ %-I:%M %p')}")
        print(f"Title: {workout.summary.ride.title}")

        output_list = []
        for x in range(len(workout.metrics.metrics)):
            if x == 4:
                values = list(map(lambda x: max(100, x), workout.metrics.metrics[x].values))
            else:
                values = workout.metrics.metrics[x].values
            slug = workout.metrics.metrics[x].slug
            df = pd.DataFrame(
                {slug: values},
                index = [(workout.summary.start_time + timedelta(seconds=(x))) 
                         for x in range(0, (5 * len(workout.metrics.metrics[x].values)), 5)]
            )
            output_list.append(df)

        return output_list

    def make_random_chart_dfs(self) -> list[pd.DataFrame]:
        workout = self.workouts[random.randint(0, len(self.workouts))]
        return self.make_chart_dfs(workout.workout_id)

    def make_line_chart_df_new(self, workout_id: str) -> pd.DataFrame:
        workout = self.workouts_by_id[workout_id]
        metrics = {'output': 'watts',
                   'cadence': 'rpm',
                   'resistance': '%',
                   'speed': 'mph',
                   'heart_rate': 'bpm'}

        print(f"Start Time: {workout.summary.start_time.strftime('%a, %b %-d, %Y @ %-I:%M %p')}")
        print(f"Title: {workout.summary.ride.title}")

        output_list: list[pd.DataFrame] = []
        for x in range(len(workout.metrics.metrics)):
            if x == 4:
                values = list(map(lambda x: max(100, x), workout.metrics.metrics[x].values))
            else:
                values = workout.metrics.metrics[x].values
            slug = workout.metrics.metrics[x].slug
            df = pd.DataFrame(
                {slug: values},
                index = [(workout.summary.start_time + timedelta(seconds=(x))) 
                         for x in range(0, (5 * len(workout.metrics.metrics[x].values)), 5)]
            )
            output_list.append(df)

        return output_list[0].join(output_list[1:])

    def make_random_chart_dfs(self) -> list[pd.DataFrame]:
        workout = self.workouts[random.randint(0, len(self.workouts))]
        return self.make_line_chart_dfs(workout.workout_id)

if __name__ == '__main__':
    main()