from urllib.request import urlretrieve

from peloton.constants import IMAGES_DIR
from peloton.schema import PelotonWorkoutData


class PelotonImageDownloader():
    def __init__(self):
        ...

    @staticmethod
    def download_workout_image(workout: PelotonWorkoutData) -> None:
        image_url = workout.summary.ride.image_url
        local_filename = IMAGES_DIR.joinpath(image_url.split(sep='/')[-1])

        urlretrieve(image_url, local_filename)


def main():
    pass

if __name__ == '__main__':
    main()