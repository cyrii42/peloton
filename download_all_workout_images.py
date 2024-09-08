from peloton.helpers import create_mariadb_engine
from peloton import PelotonProcessor
from urllib.request import urlretrieve


def download_images():
    peloton_processor = PelotonProcessor()
    for workout in peloton_processor.workouts:
        if workout.summary.ride.image_url is not None:
            peloton_processor.image_downloader.download_workout_image(workout)

def test():
    test_url = 'https://s3.amazonaws.com/peloton-ride-images/e9e4253f78e4877d267b8dbacc47e3da620e70b2/img_1666115383_13232dbbc48d43739b3a0108e71266e5.jpg'
    local_filename, img = urlretrieve(test_url)
    print


def main():
    download_images()

if __name__ == "__main__":
    main()