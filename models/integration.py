from sqlalchemy import Column, Integer, String
from core.database import Base


class Integration(Base):
    __tablename__ = "integrations"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, nullable=False)
    integration_type = Column(String, nullable=True)
    provider = Column(String, nullable=True)


