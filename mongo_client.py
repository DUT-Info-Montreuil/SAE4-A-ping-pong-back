from pymongo import MongoClient
from pymongo.errors import ConnectionFailure


class Mongo2Client:

    def __init__(self, host='localhost', port=27017, db_name='Tournoi_Ping-pong', username='juba', password=None):
        try:
            if username and password:
                uri = f"mongodb://{username}:{password}@{host}:{port}/{db_name}"
                self.client = MongoClient(uri)
            else:
                self.client = MongoClient(host, port)
            self.db = self.client[db_name]
        except ConnectionFailure as e:
            print("Erreur de connexion à la base de données MongoDB:", e)

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.client.close()


if __name__ == '__main__':
    mongo_client = Mongo2Client(db_name='Tournoi_Ping-pong')
    joueurs = mongo_client.db['joueur'].count_documents({}) + 1
    print(joueurs)

    from datetime import date

    today = date.today()
    print("Today's date:", today)