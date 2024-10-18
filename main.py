import argparse

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from zoneinfo import ZoneInfo

from peloton.api import router, peloton
from peloton.helpers.constants import STATIC_DIR, WORKOUT_IMAGES_DIR, ACHIEVEMENT_IMAGES_DIR

LOCAL_TZ = ZoneInfo('America/New_York')

origins = ["*"]

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount('/static', StaticFiles(directory=STATIC_DIR, follow_symlink=True), name='static')
app.mount('/workout_images', StaticFiles(directory=WORKOUT_IMAGES_DIR, follow_symlink=True), name='workout_images')
app.mount('/achievement_images', StaticFiles(directory=ACHIEVEMENT_IMAGES_DIR, follow_symlink=True), name='achievement_images')

app.include_router(router)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--check-new-workouts', dest='CHECK_FOR_NEW_WORKOUTS',
                        action='store_const', const=True, default=False,
                        help='check for new workouts on remote Peloton database')
    args = parser.parse_args()
    
    if args.CHECK_FOR_NEW_WORKOUTS:
        peloton.check_for_new_workouts()

    peloton.print_processed_data_to_stdout()
    peloton.print_pivot_tables_to_stdout()

    if peloton.new_workouts:
        peloton.write_csv_files()


if __name__ == '__main__':
    main()