from peloton.schema import PelotonWorkoutData
import pandas as pd
from datetime import timedelta
import random

def main():
    pass

class PelotonChartMaker():
    def __init__(self, workouts: list[PelotonWorkoutData], backend: str = 'matplotlib'):
        self.workouts = workouts
        self.workouts_by_id = {workout.summary.workout_id: workout for workout in workouts}
        pd.set_option('plotting.backend', backend)

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
        df['pct'] = df['duration'] / df['duration'].sum()

        return df

    def make_chart_dfs(self, workout_id: str) -> list[pd.DataFrame]:
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

if __name__ == '__main__':
    main()