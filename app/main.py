from fastapi import FastAPI, Body, Path, Depends
from typing import Union
from datetime import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from app.tasks import scheduler, schedule_tasks
from app.models import Announcement, Base

SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def check_db():
    db = SessionLocal()
    return db


app = FastAPI()


@app.on_event("startup")
def startup_event():
    schedule_tasks()
    scheduler.start()
    with check_db() as db:
        print("Db connected successfully")

    print(f"Scheduler started: {scheduler}")


@app.get("/")
async def root():
    return {"message": "Health check OK", "status": 200}


@app.post("/api/v1/announcements")
async def schedule_announcement(message: str = Body(...), send_at: datetime = Body(...), db: Session = Depends(get_db)):
    print(f"Announcement scheduled: {message} - Scheduled for: {send_at}")

    announcement = Announcement(message=message, send_at=send_at)
    db.add(announcement)
    db.commit()
    db.refresh(announcement)

    return {"message": f"Announcement scheduled successfully. ID: {announcement.id}"}


@app.get("/api/v1/announcements/{announcement_id}")
async def get_announcement_by_id(announcement_id: int = Path(..., description="ID of the announcement to retrieve"), db: Session = Depends(get_db)):

    announcement = db.query(Announcement).filter(Announcement.id == announcement_id).first()

    if not announcement:
        return {"message": f"Announcement with ID {announcement_id} not found"}

    return {
        "id": announcement.id,
        "message": announcement.message,
        "status": announcement.status.value,
        "send_at": announcement.send_at.isoformat() if announcement.send_at else None
    }


@app.get("/items/{item_id}")
async def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}
