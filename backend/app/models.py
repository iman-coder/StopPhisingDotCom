from sqlalchemy import Column, Integer, String, DateTime
from app.utils.database import Base
from datetime import datetime

class URL(Base):
    __tablename__ = "urls"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, unique=True, index=True, nullable=False)
    domain = Column(String, index=True)
    threat = Column(String)
    date_added = Column(DateTime, default=datetime.utcnow)
    status = Column(String)
    source = Column(String)
