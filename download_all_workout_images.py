from peloton.helpers import create_mariadb_engine
from peloton.peloton_processor import PelotonProcessor

def download_images():
    peloton_processor = PelotonProcessor()
    for workout in peloton_processor.workouts:
        if workout.summary.ride.image_url is not None:
            peloton_processor.image_downloader.download_workout_image(workout)

def main():
    ...    

if __name__ == "__main__":
    main()