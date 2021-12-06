from .singleton import Singleton
from . import logger
# from ..api.endpoints.pipelines import convert_pipeline_to_dict
import pymongo
import os
# from quart import jsonify
# import json
from bson import ObjectId, json_util

# class JSONEncoder(json.JSONEncoder):
#     def default(self, o):
#         if isinstance(o, ObjectId):
#             return str(o)
#         return json.JSONEncoder.default(self, o)

class MongoConnector(metaclass=Singleton):
    def __init__(self, db_name: str="theiaserver", collection: str="gstpipelines"):
        super().__init__()
        mongo_service_host = os.getenv('DATABASE_MONGO_SERVICE_HOST')
        if not mongo_service_host:
            mongo_service_host = "mongodb"
        mongo_service_port = os.getenv('DATABASE_MONGO_SERVICE_PORT')
        if not mongo_service_port:
            mongo_service_port = "27017"
        
        mongo_ip_port = f"mongodb://{mongo_service_host}:{mongo_service_port}/"
        self.collection = self.__db_connect(mongo_ip_port, db_name, collection)
        logger.debug("Mongo DB connector initiated.")
        
    def __db_connect(self, mongo_ip_port: str, db_name: str, collection: str):
        client = pymongo.MongoClient(mongo_ip_port)
        db = client[db_name]
        return db[collection]

    def read_all(self):
        logger.debug(f'Reading all records from Mongo DB.')
        # return JSONEncoder().encode([i for i in self.collection.find()])
        return json_util.dumps([i for i in self.collection.find()])

    def read_one(self, pipeline_uuid: str):
        
        query = {"uuid": pipeline_uuid}
        logger.debug(f'Reading record with uuid {pipeline_uuid} from Mongo DB.')
        return [x for x in self.collection.find(query)][0]
        