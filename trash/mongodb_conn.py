from pymongo import MongoClient

from peloton.constants import MONGODB_HOSTNAME

class MongoDBConnection():
    """ MongoDB Connection """    
    def __init__(self, host: str = MONGODB_HOSTNAME, port: int = 27017):
        self.host = host
        self.port = port
        self.connection = None    

    def __enter__(self) -> 'MongoDBConnection':
        self.connection = MongoClient(self.host, self.port)
        return self    

    def __exit__(self, exc_type, exc_value, exc_traceback) -> None:
        self.connection.close()