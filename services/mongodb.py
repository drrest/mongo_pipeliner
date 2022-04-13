from pymongo import MongoClient

from settings.db import mongo_db, mongo_host, mongo_port, mongo_username, mongo_password, mongo_auth, mongo_auth_src

if mongo_auth == "1":
    uri = "mongodb://{}:{}@{}:{}/{}?retryWrites=true&w=majority".format(mongo_username,
                                                                        mongo_password, mongo_host,
                                                                        mongo_port, mongo_db)
    if mongo_auth_src != "":
        uri += "&authSource={}".format(mongo_auth_src)

else:
    uri = "mongodb://{}:{}/{}?retryWrites=true&w=majority".format(mongo_host, mongo_port, mongo_db)

mongo_client = MongoClient(uri)[mongo_db]
