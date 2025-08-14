from sqlalchemy import Column, Integer, String
from core.database import Base


class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, nullable=False)
    report_type = Column(String, nullable=False)
    workspace_id = Column(String, nullable=True)


