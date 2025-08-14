from sqlalchemy import Column, Integer, String
from core.database import Base


class Workspace(Base):
    __tablename__ = "workspaces"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    clickup_id = Column(String, unique=True, index=True, nullable=True)
    name = Column(String, nullable=True)


