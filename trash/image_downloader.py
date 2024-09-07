import urllib3
from PIL import Image
from io import BytesIO

from peloton.constants import IMAGES_DIR
from peloton.models import PelotonWorkoutData


class PelotonImageDownloader():
    def __init__(self):
        ...

    @staticmethod
    def download_workout_image(workout: PelotonWorkoutData) -> None:
        if workout.summary.ride.image_url is None:
            return None
        
        print(f"Downloading image for workout {workout.workout_id}...")

        image_url = workout.summary.ride.image_url
        local_filename = IMAGES_DIR.joinpath(image_url.split(sep='/')[-1])
        thumb_filename = local_filename.with_stem(f"{local_filename.stem}_thumb")

        http = urllib3.PoolManager()
        try:
            response: urllib3.response.BaseHTTPResponse = http.request('GET', image_url)           
        except urllib3.exceptions.LocationValueError as e:
            print(e)
        else:
            if response.status == 200:
                img_data = BytesIO(response.data)
                img = Image.open(img_data)
                
                thumb = img.copy()
                thumb.thumbnail(size=(250, 250))

                img.save(local_filename)
                thumb.save(thumb_filename)
            else:
                print(f"ERROR - HTTP Status Code: {response.status}")

def main():
    pass

if __name__ == '__main__':
    main()