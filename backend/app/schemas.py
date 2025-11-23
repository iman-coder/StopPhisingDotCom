from typing import Optional
from pydantic import BaseModel
from datetime import datetime


class URLBase(BaseModel):
    url: str
    domain: Optional[str] = None
    threat: Optional[str] = None
    status: Optional[str] = None
    source: Optional[str] = None


class URLCreate(URLBase):
    # `date_added` is optional on create; if omitted the service/model
    # can set the current time automatically.
    date_added: Optional[datetime] = None


class URLUpdate(BaseModel):
    # All fields optional for partial updates (PATCH-like behavior).
    url: Optional[str] = None
    domain: Optional[str] = None
    threat: Optional[str] = None
    date_added: Optional[datetime] = None
    status: Optional[str] = None
    source: Optional[str] = None


class URLResponse(URLBase):
    id: int
    date_added: Optional[datetime] = None

    class Config:
        orm_mode = True
