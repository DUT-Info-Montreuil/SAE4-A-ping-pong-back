from pymongo import MongoClient
from pymongo.errors import ConnectionFailure


class SingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


class Mongo2Client(metaclass=SingletonMeta):
    def __init__(self, host='localhost', port=27017, db_name='Tournoi_Ping-pong', username='luc', password=None):
        try:
            if username and password:
                uri = f"mongodb://{username}:{password}@{host}:{port}/{db_name}"
                self.client = MongoClient(uri)
            else:
                self.client = MongoClient(host, port)
            self.db = self.client[db_name]
        except ConnectionFailure as e:
            print("Erreur de connexion à la base de données MongoDB:", e)


if __name__ == "__main__":
    # Test du singleton MongoDB client.
    client1 = Mongo2Client()
    client2 = Mongo2Client()

    if id(client1) == id(client2):
        print("Singleton works, both variables contain the same instance.")
    else:
        print("Singleton failed, variables contain different instances.")
