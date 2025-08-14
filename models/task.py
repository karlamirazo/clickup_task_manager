from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.dialects.sqlite import JSON as SQLiteJSON
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    clickup_id = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    description = Column(String, default="")
    status = Column(String, default="pending")
    priority = Column(Integer, default=3)
    due_date = Column(DateTime, nullable=True)
    start_date = Column(DateTime, nullable=True)
    workspace_id = Column(String, index=True)
    list_id = Column(String, index=True)
    assignee_id = Column(String, nullable=True)
    creator_id = Column(String, nullable=True)
    tags = Column(SQLiteJSON, default=list)
    custom_fields = Column(SQLiteJSON, default=dict)
    is_synced = Column(Integer, default=1)
    last_sync = Column(DateTime, nullable=True)


