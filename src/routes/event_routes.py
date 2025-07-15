from fastapi import APIRouter, UploadFile, File
from fastapi.responses import JSONResponse, FileResponse
from models.events import CreateEvent, UpdateEvent
from services.events_service import event_user_service
import os

router = APIRouter()

# @router.get("/status_of_user_route")
# async def status():
#     return {"message": "user route is up"}

@router.patch("/setup_event_profile")
async def setup_event_profile(event_profile: CreateEvent):
    event = await event_user_service.create_event_profile(event_profile)
    if event:
        return JSONResponse({
            "message": "Profile setup successful",
            "profile": event_profile.model_dump()
        })
    return JSONResponse({"message": "Event not found"}, status_code=404)

@router.patch("/update_event_profile/{event_id}")
async def update_event_profile(event_id: str, event_profile: UpdateEvent):
    event = await event_user_service.update_event_profile(event_id, event_profile)
    if event:
        return JSONResponse({
            "message": "Details updated successfully",
            "profile": event.model_dump()
        })
    return JSONResponse({"message": "User not found"}, status_code=404)

@router.patch("/delete_event/{event_id}")
async def delete_event(event_id: str):
    event = await event_user_service.delete_event(event_id)
    if event:
        return JSONResponse({
            "message": "Event deleted",
            "profile": event.model_dump()
        })
    return JSONResponse({"message": "User not found"}, status_code=404)


@router.patch("/upload_event_poster/{event_id}")
async def upload_event_poster(event_id: str, poster: UploadFile = File(...)):
    uploads_dir = "poster_uploads"
    os.makedirs(uploads_dir, exist_ok=True)

    poster_path = f"{uploads_dir}/{event_id}_{poster.filename}"
    with open(poster_path, "wb") as f:
        f.write(await poster.read())



    event = await event_user_service.upload_event_poster(event_id, poster_path)

    if event:
        return JSONResponse({
            "message": "Profile picture uploaded successfully",
            "Event_details": event.model_dump()
        })
    return JSONResponse({"message": "poster not found"}, status_code=404)


@router.get("/event_posters/{filename}")
def get_poster(event_id:str, filename: str):
    return FileResponse(f"poster_uploads/{event_id}_{filename}")



@router.patch("/upload_event_reel/{event_id}")
async def upload_event_reel(event_id: str, reel: UploadFile = File(...)):
    uploads_dir = "promo_reel_uploads"
    os.makedirs(uploads_dir, exist_ok=True)

    reel_path = f"{uploads_dir}/{event_id}_{reel.filename}"
    with open(reel_path, "wb") as f:
        f.write(await reel.read())



    event = await event_user_service.upload_event_poster(event_id, reel_path)

    if event:
        return JSONResponse({
            "message": "Promo reel uploaded successfully",
            "Event_details": event.model_dump()
        })
    return JSONResponse({"message": "promo_reel not found"}, status_code=404)


@router.get("/event_promo_reel/{filename}")
def get_promo_reel(event_id:str, filename: str):
    return FileResponse(f"promo_reel_uploads/{event_id}_{filename}")