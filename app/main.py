import os
from datetime import datetime

from fastapi import FastAPI, Body, Path, Depends, HTTPException

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from rq import Queue, Worker, Connection, get_current_job

from app.tasks import scheduler, schedule_tasks
from app.models import Base, Announcement, AnnouncementStatus
from app.redis_queue import queue as q


SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", 'sqlite:///./sql_app.db')

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
    with check_db():
        print("Db connected successfully")


def send_announcement(announcement: dict):
    current_job = get_current_job()
    if current_job:
        print(f"SENT - {announcement}")
        #  current_job.delete()


@app.get("/")
async def root():
    return {"message": "Health check OK", "status": 200}


@app.post("/api/v1/announcements")
async def schedule_announcement(message: str = Body(...), send_at: datetime = Body(...), db: Session = Depends(get_db)):
    try:
        print(f"Announcement scheduled: {message} - Scheduled for: {send_at}")

        announcement = Announcement(message=message, send_at=send_at)
        db.add(announcement)
        db.commit()
        db.refresh(announcement)

        queue_item = {"announcement_id": announcement.id, "send_at": send_at.isoformat()}
        q.enqueue(send_announcement, queue_item, result_ttl=-1)

        return {"message": f"Announcement scheduled successfully. ID: {announcement.id}"}
    except Exception as e:
        db.rollback()  # rollback any changes made in case of error
        raise HTTPException(status_code=500, detail=f"An error occurred while scheduling the announcement - {str(e)}")


@app.get("/api/v1/announcements/{announcement_id}")
async def get_announcement_by_id(announcement_id: int = Path(..., description="ID of the announcement to retrieve"),
                                 db: Session = Depends(get_db)):
    try:
        announcement = db.query(Announcement).filter(Announcement.id == announcement_id).first()
        if not announcement:
            raise HTTPException(status_code=404, detail=f"Announcement with ID {announcement_id} not found")

        return {
            "id": announcement.id,
            "message": announcement.message,
            "status": announcement.status.value,
            "send_at": announcement.send_at.isoformat() if announcement.send_at else None
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred while retrieving the announcement - {str(e)}")


@app.put("/api/v1/announcements/{announcement_id}/update-status")
async def update_announcement_status(announcement_id: int, new_status: AnnouncementStatus, db: Session = Depends(get_db)):
    try:
        announcement = db.query(Announcement).filter(Announcement.id == announcement_id).first()
        if not announcement:
            raise HTTPException(status_code=404, detail=f"Announcement with ID: {announcement_id} not found")

        announcement.status = new_status
        db.commit()

        return {"message": f"Announcement with ID: {announcement_id} updated to SENT successfully"}
    except Exception as e:
        db.rollback()  # rollback any changes made in case of error
        raise HTTPException(status_code=500, detail=f"An error occurred while updating the announcement - {str(e)}")
