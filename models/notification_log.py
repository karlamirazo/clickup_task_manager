from sqlalchemy import Column, Integer, String, DateTime
from core.database import Base


class NotificationLog(Base):
    __tablename__ = "notification_logs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    task_id = Column(String, nullable=True)
    channel = Column(String, nullable=True)
    recipient = Column(String, nullable=True)
    sent_at = Column(DateTime, nullable=True)


