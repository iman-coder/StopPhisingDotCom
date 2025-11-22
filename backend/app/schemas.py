from pydantic import BaseModel
from datetime import datetime

class URLBase(BaseModel):
    url: str
    domain: str
    threat: str
    date_added: datetime
    status: str
    source: str

class URLCreate(URLBase):
    pass

class URLUpdate(URLBase):
    pass

class URLResponse(URLBase):
    id: int

    class Config:
        orm_mode = True
