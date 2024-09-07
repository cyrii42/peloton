import json

from peloton.constants import (MONGODB_COLLECTION, MONGODB_DATABASE,
                               WORKOUTS_DIR, MONGODB_INSTRUCTORS_COLLECTION)

from peloton.models import PelotonWorkoutData
from .mongodb_conn import MongoDBConnection

class PelotonMongoDB():
    def __init__(self):
        self.mongodb_client = MongoDBConnection()

    def get_workout_id_list(self) -> list[str]:
        with self.mongodb_client as client:
            db = client.connection[MONGODB_DATABASE]
            collection = db[MONGODB_COLLECTION]
            workouts = collection.find()
            workout_id_list = [workout['workout_id'] for workout in workouts]

        return workout_id_list

    def ingest_workouts(self) -> list[PelotonWorkoutData]:
        print("Getting workouts from MongoDB...")
        with self.mongodb_client as client:
            db = client.connection[MONGODB_DATABASE]
            collection = db[MONGODB_COLLECTION]
            workouts = collection.find()
            workout_list = [PelotonWorkoutData(**workout) for workout in workouts]
        
        return workout_list

    def export_workout(self, workout: PelotonWorkoutData) -> None:
        print(f"Exporting workout {workout.workout_id} to MongoDB...")
        with self.mongodb_client as client:
            db = client.connection[MONGODB_DATABASE]
            collection = db[MONGODB_COLLECTION]
            collection.insert_one(workout.model_dump())
        
    def update_workout(self, workout: PelotonWorkoutData) -> None:
        print(f"Updating workout {workout.workout_id} on MongoDB with new data...")
        with self.mongodb_client as client:
            db = client.connection[MONGODB_DATABASE]
            collection = db[MONGODB_COLLECTION]
            collection.find_one_and_replace(
                filter={'workout_id': workout.workout_id},
                replacement=workout.model_dump())

    def get_workout(self, workout_id: str) -> PelotonWorkoutData:
        with self.mongodb_client as client:
            db = client.connection[MONGODB_DATABASE]
            collection = db[MONGODB_COLLECTION]
            workout = collection.find_one({'workout_id': workout_id})
        return PelotonWorkoutData(**workout)

    def get_instructor(self, instructor_id: str) -> dict:
        with self.mongodb_client as client: 
            db = client.connection[MONGODB_DATABASE]
            collection = db[MONGODB_INSTRUCTORS_COLLECTION]
            instructor = collection.find_one({'instructor_id': instructor_id})
        return instructor

    def add_instructor(self, instructor: dict) -> None:
        with self.mongodb_client as client:
            db = client.connection[MONGODB_DATABASE]
            collection = db[MONGODB_INSTRUCTORS_COLLECTION]
            collection.insert_one(instructor)

    

def main():
    ...

if __name__ == "__main__":
    main()
