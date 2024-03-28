from flask import current_app
from pymongo import MongoClient


class MongoDB:
    def __init__(self):
        self.client = None
        self.db = None

    def get_db(self):
        if not self.client:
            self.client = MongoClient(current_app.config['MONGO_URI'])
            self.db = self.client[current_app.config['DATABASE_NAME']]
        return self.db
