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
                print(workout.metrics.metrics[x].values)
                values = list(map(lambda x: max(100, x), workout.metrics.metrics[x].values))
                print(values)
            else:
                values = workout.metrics.metrics[x].values
            slug = workout.metrics.metrics[x].slug
            df = pd.DataFrame(
                {slug: values},
                index = [(workout.summary.start_time + timedelta(seconds=(x))) 
                         for x in range(0, (5 * len(workout.metrics.metrics[x].values)), 5)]
            )

            # df.plot(figsize=(16, 4), ylabel=metrics[slug])
            output_list.append(df)

        return output_list

    def make_random_chart_dfs(self) -> list[pd.DataFrame]:
        workout = self.workouts[random.randint(0, len(self.workouts))]
        return self.make_chart_dfs(workout.workout_id)

if __name__ == '__main__':
    main()