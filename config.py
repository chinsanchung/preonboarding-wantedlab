import os
from dotenv import load_dotenv

load_dotenv(verbose=True)

BASE_DIR = os.path.dirname(__file__)

SQLALCHEMY_DATABASE_URI = "sqlite:///{}".format(os.path.join(BASE_DIR, "wantedlab.db"))

SQLALCHEMY_ECHO = False
SQLALCHEMY_TRACK_MODIFICATIONS = False
