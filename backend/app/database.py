import os
from sqlmodel import SQLModel, create_engine, Session
import redis


DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://postgres:postgres@db:5432/registrydb")

engine = create_engine(DATABASE_URL, echo=False)

def init_db():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

def get_redis():
    url = os.environ.get('REDIS_URL','redis://redis:6379/0')
    return redis.from_url(url)
