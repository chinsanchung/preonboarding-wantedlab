import os
from dotenv import load_dotenv

load_dotenv(verbose=True)

BASE_DIR = os.path.dirname(__file__)

SQLALCHEMY_DATABASE_URI = (
    "mysql+pymysql://{username}:{password}@{db_host}:{db_port}/{db_name}".format(
        username=os.getenv("RDS_USERNAME"),
        password=os.getenv("RDS_PASSWORD"),
        db_host=os.getenv("RDS_HOST"),
        db_port=os.getenv("RDS_PORT"),
        db_name=os.getenv("RDS_DB_NAME"),
    )
)
SQLALCHEMY_ECHO = False
SQLALCHEMY_TRACK_MODIFICATIONS = False
