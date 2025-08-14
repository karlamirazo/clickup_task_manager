from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Automation(Base):
    __tablename__ = "automations"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, nullable=False)
    trigger_type = Column(String, nullable=True)
    workspace_id = Column(String, nullable=True)


