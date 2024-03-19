from sqlalchemy import Column, Integer, String, DateTime, Enum
from sqlalchemy.ext.declarative import declarative_base
import enum

Base = declarative_base()


class AnnouncementStatus(enum.Enum):
    pending = "PENDING"
    sent = "SENT"


class Announcement(Base):
    __tablename__ = "announcements"

    id = Column(Integer, primary_key=True, index=True)
    message = Column(String, index=True)
    status = Column(Enum(AnnouncementStatus), default=AnnouncementStatus.pending)
    send_at = Column(DateTime)