from sqlalchemy import Column, Integer, String, DateTime, Boolean
from app.utils.database import Base
from datetime import datetime

class URL(Base):
    __tablename__ = "urls"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, unique=True, index=True, nullable=False)
    domain = Column(String, index=True)
    threat = Column(String)
    # optional numeric representation of risk (0-100). Populated from imports or computed.
    risk_score = Column(Integer, nullable=True)
    date_added = Column(DateTime, default=datetime.utcnow)
    status = Column(String)
    source = Column(String)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    email = Column(String, unique=True, index=True, nullable=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
