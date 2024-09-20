from venv import create
from zoneinfo import ZoneInfo
from sqlmodel import SQLModel, Session, create_engine, select

from peloton import PelotonProcessor
from peloton.models import Dataframe, DataframeBase, DataframeCreate
from peloton.schema import PelotonDataFrameRow

LOCAL_TZ = ZoneInfo('America/New_York')
SQLITE_FILENAME = "peloton_test.db"
SQLITE_URL = f"sqlite:///{SQLITE_FILENAME}"
engine = create_engine(SQLITE_URL, echo=True, connect_args={"check_same_thread": False})



def create_db_and_tables():
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)

def create_test_records(records: list[dict]):
    test_records = records
    for record in test_records:
        with Session(engine) as session:
            transaction = Dataframe.model_validate(record)
            session.add(transaction)
            session.commit()

def main():
    peloton = PelotonProcessor()
    test_records = [workout.create_dictionary() for workout in peloton.workouts]
    
    create_db_and_tables()
    create_test_records(test_records)


if __name__ == '__main__':
    main()