from peloton import PelotonProcessor
import pandas as pd
from datetime import timedelta
import random
from matplotlib.pyplot import Axes

pd.set_option('plotting.backend', 'matplotlib')

processor = PelotonProcessor()

workout = processor.workouts[random.randint(0, len(processor.workouts))]

metrics = {'output': 'watts',
           'cadence': 'rpm',
           'resistance': '%',
           'speed': 'mph',
           'heart_rate': 'bpm'}

print(f"Start Time: {workout.summary.start_time.strftime('%a, %b %-d, %Y @ %-I:%M %p')}")
print(f"Title: {workout.summary.ride.title}")

for x in range(len(workout.metrics.metrics)):
    values = workout.metrics.metrics[x].values
    slug = workout.metrics.metrics[x].slug
    df = pd.DataFrame(
        {slug: values},
        index = [(workout.summary.start_time + timedelta(seconds=(x))).strftime('%-I:%M %p') for x in range(0, (5 * len(values)), 5)],
    )
    # df.plot()

    with open('asdf.png', 'wb') as f:
        f.write(df.plot(figsize=(16, 4), ylabel=metrics[slug]))
    

