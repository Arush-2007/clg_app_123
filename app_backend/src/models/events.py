from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class CreateEvent(BaseModel):
    event_name     :  str
    event_host  :   str
    event_description  :  str
    event_init_date     :   datetime
    event_end_date     :  datetime
    event_location :   str


class UpdateEvent(BaseModel):
    event_name     :  Optional[str]
    event_host     :  Optional[str]
    event_description  :  Optional[str]
    event_init_date     :  Optional[datetime]
    event_end_date     :  Optional[datetime]
    event_location :   Optional[str]
