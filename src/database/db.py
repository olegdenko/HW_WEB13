import configparser
import pathlib
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


file_config = pathlib.Path(__file__).parent.parent.joinpath("conf/config.ini")
config = configparser.ConfigParser()
config.read(file_config)

db = config.get("DEV_DB", "DB")
username = config.get("DEV_DB", "USER")
password = config.get("DEV_DB", "PASSWORD")
domain = config.get("DEV_DB", "DOMAIN")
port = config.get("DEV_DB", "PORT")
database = config.get("DEV_DB", "DB_NAME")

URI = f"{db}://{username}:{password}@{domain}:{port}/{database}"

engine = create_engine(URI)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
