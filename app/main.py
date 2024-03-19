from fastapi import FastAPI
from typing import Union

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.tasks import scheduler, schedule_tasks
from app.models import Announcement, Base

SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()


def get_db():
    db = SessionLocal()
    return db  # Return the session object directly


app = FastAPI()


@app.on_event("startup")
def startup_event():
    schedule_tasks()
    scheduler.start()
    with get_db() as db:
        print('Db connected successfully')

    print(f"Scheduler started: {scheduler}")


@app.get("/")
async def root():
    return {"message": "FastAPI app with background task!"}


@app.get("/items/{item_id}")
async def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}
