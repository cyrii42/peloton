import json

from peloton.constants import (MONGODB_COLLECTION, MONGODB_DATABASE,
                               WORKOUTS_DIR, MONGODB_INSTRUCTORS_COLLECTION)

from peloton.schema import PelotonWorkoutData
from .mongodb_conn import MongoDBConnection

class PelotonMongoDB():
    def __init__(self):
        self.mongodb_client = MongoDBConnection()

    def get_workout_id_list_from_mongodb(self) -> list[str]:
        with self.mongodb_client as client:
            db = client.connection[MONGODB_DATABASE]
            collection = db[MONGODB_COLLECTION]
            workouts = collection.find()
            workout_id_list = [workout['workout_id'] for workout in workouts]

        return workout_id_list

    def ingest_workouts_from_mongodb(self) -> list[PelotonWorkoutData]:
        print("Getting workouts from MongoDB...")
        with self.mongodb_client as client:
            db = client.connection[MONGODB_DATABASE]
            collection = db[MONGODB_COLLECTION]
            workouts = collection.find()
            workout_list = [PelotonWorkoutData(**workout) for workout in workouts]
        
        return workout_list

    def export_workout_to_mongodb(self, workout: PelotonWorkoutData) -> None:
        print(f"Exporting workout {workout.workout_id} to MongoDB...")
        with self.mongodb_client as client:
            db = client.connection[MONGODB_DATABASE]
            collection = db[MONGODB_COLLECTION]
            collection.insert_one(workout.model_dump())

    def get_workout_from_mongodb(self, workout_id: str) -> PelotonWorkoutData:
        with self.mongodb_client as client:
            db = client.connection[MONGODB_DATABASE]
            collection = db[MONGODB_COLLECTION]
            workout = collection.find_one({'workout_id': workout_id})
        return PelotonWorkoutData(**workout)

    def write_workout_to_json(self, workout: PelotonWorkoutData) -> None:
        with open(WORKOUTS_DIR.joinpath(f"{workout.workout_id}.json"), 'w') as f:
            json.dump(workout.model_dump(), f, indent=4)

    def backup_all_workouts_to_json(self) -> None:
        workouts = self.ingest_workouts_from_mongodb()
        for workout in workouts:
            print(f"Writing workout {workout.workout_id} to JSON...")
            self.write_workout_to_json(workout)

    def get_instructor_info_from_instructor_id(self, instructor_id: str) -> dict:
        with self.mongodb_client as client: 
            db = client.connection[MONGODB_DATABASE]
            collection = db[MONGODB_INSTRUCTORS_COLLECTION]
            instructor = collection.find_one({'instructor_id': instructor_id})
        return instructor

    def add_instructor_to_mongodb(self, instructor: dict) -> None:
        with self.mongodb_client as client:
            db = client.connection[MONGODB_DATABASE]
            collection = db[MONGODB_INSTRUCTORS_COLLECTION]
            collection.insert_one(instructor)

    

def main():
    ...

if __name__ == "__main__":
    main()
