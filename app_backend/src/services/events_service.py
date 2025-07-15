from src.models import Event
from models.events import CreateEvent, UpdateEvent
from utils.prisma import db

class Event_UserService:
    def __init__(self):
        pass

    async def create_event_profile(self, event_id: str, Event_Profile: CreateEvent):
        return await db.event.update(data={
            "event_name"     :  Event_Profile.event_name,
            "event_host"  :    Event_Profile.event_host,
            "event_description"  :  Event_Profile.event_host,
            "event_init_date"     :   Event_Profile.event_init_date,
            "event_end_date"     : Event_Profile.event_end_date,
            "event_location" :   Event_Profile.event_location,
        }, where={"event_id": event_id})

    async def update_event_profile(self, event_id: str, Event_Profile: UpdateEvent):
        finalised_event_profile = Event_Profile.model_dump(exclude_unset=True, exclude_none=True)
        return await db.user.update(data=finalised_event_profile, where={"event_id": event_id})

    async def delete_event(self, event_id: str):
        return await db.event.update(data={
            "event_name"     :  None,
            "event_host"  :    None,
            "event_description"  :  None,
            "event_init_date"     :   None,
            "event_end_date"     :None,
            "event_location" :   None,
            "event_image_url" : None
        }, where={"event_id": event_id})
    


    async def upload_event_poster(self, event_id: str, poster_url: str):
        return await db.event.update(
           data={"poster_url": poster_url},
           where={"event_id": event_id}
    )

    async def upload_event_promo_reel(self, event_id: str, reel_url: str):
        return await db.event.update(
           data={"reel_url": reel_url},
           where={"event_id": event_id}
    )


event_user_service = Event_UserService()
