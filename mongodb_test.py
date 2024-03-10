from pymongo import MongoClient
from peloton import PelotonMongoDB#, PelotonProcessor, PelotonWorkoutData, 

def main():
    db = PelotonMongoDB()

    # pp = PelotonProcessor()
    # workouts = pp.workouts

    # with db.mongodb_client as client:
    #     collection = client.connection['peloton']['peloton']
    #     collection.insert_many([workout.model_dump() for workout in workouts])


    # db.export_workout_to_mongodb(workouts[0])
    
    asdf = db.get_instructor_info_from_instructor_id('f4f9ca8074ef44cd8bc4df88ad366de8')
    print(asdf)

def asdf():
    CONNECTION_STRING = "mongodb://portainarr.box:27017"
    client = MongoClient(host='portainarr.box', port=27017)
    db = client.test_database
    collection = db.peloton_test_collection_2

    # pp = PelotonProcessor()
    # workouts = pp.workouts

    # collection.insert_many([workout.model_dump() for workout in workouts])

    print(db.list_collection_names())
    workouts = collection.find()
    workout1 = workouts.next()

    # print(PelotonWorkoutData(**workout1))
    
    # print(collection.find({'workout_id': 'f4f9ca8074ef44cd8bc4df88ad366de8'}).next())
    
    # Close the client
    client.close()


if __name__ == "__main__":
    main()
    
