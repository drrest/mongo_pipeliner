import os

mongo_username = os.getenv("MONGO_USERNAME", "username")
mongo_password = os.getenv("MONGO_PASSWORD", "password")
mongo_host = os.getenv("MONGO_HOST", "0.0.0.0")
mongo_port = os.getenv("MONGO_PORT", "27017")
mongo_auth = os.getenv("MONGO_AUTH", "0")
mongo_auth_src = os.getenv("MONGO_AUTH_SRC", "admin")

mongo_db = os.getenv("MONGO_DB", "dev_database")
