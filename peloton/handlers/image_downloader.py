import urllib3

from peloton.constants import IMAGES_DIR
from peloton.schema import PelotonWorkoutData


class PelotonImageDownloader():
    def __init__(self):
        ...

    @staticmethod
    def download_workout_image(workout: PelotonWorkoutData) -> None:
        if workout.summary.ride.image_url is not None:
            print(f"Downloading image for workout {workout.workout_id}...")

            image_url = workout.summary.ride.image_url
            local_filename = IMAGES_DIR.joinpath(image_url.split(sep='/')[-1])

            http = urllib3.PoolManager()
            try:
                response: urllib3.response.BaseHTTPResponse = http.request('GET', image_url)           
            except urllib3.exceptions.LocationValueError as e:
                print(e)
            else:
                if response.status == 200:
                    with open(local_filename, 'wb') as file:
                        file.write(response.data)
                else:
                    print(f"ERROR - HTTP Status Code: {response.status}")


def main():
    pass

if __name__ == '__main__':
    main()