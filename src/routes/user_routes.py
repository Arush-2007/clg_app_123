from fastapi import APIRouter, UploadFile, File
from fastapi.responses import JSONResponse, FileResponse
from models.user import Set_Up_Profile, Update_Profile
from services.user_service import user_service
import os

router = APIRouter()

@router.get("/status_of_user_route")
async def status():
    return {"message": "user route is up"}

@router.patch("/setup_profile/{user_id}")
async def setup_profile(user_id: str, profile: Set_Up_Profile):
    user = await user_service.create_profile(user_id, profile)
    if user:
        return JSONResponse({
            "message": "Profile setup successful",
            "profile": user.model_dump()
        })
    return JSONResponse({"message": "User not found"}, status_code=404)

@router.patch("/update_profile/{user_id}")
async def update_profile(user_id: str, profile: Update_Profile):
    user = await user_service.update_profile(user_id, profile)
    if user:
        return JSONResponse({
            "message": "Profile updated successfully",
            "profile": user.model_dump()
        })
    return JSONResponse({"message": "User not found"}, status_code=404)

@router.patch("/delete_profile_fields/{user_id}")
async def delete_profile_fields(user_id: str):
    user = await user_service.delete_profile(user_id)
    if user:
        return JSONResponse({
            "message": "Profile fields cleared",
            "profile": user.model_dump()
        })
    return JSONResponse({"message": "User not found"}, status_code=404)


@router.patch("/upload_profile_picture/{user_id}")
async def upload_profile_picture(user_id: str, image: UploadFile = File(...)):
    uploads_dir = "uploads"
    os.makedirs(uploads_dir, exist_ok=True)

    file_path = f"{uploads_dir}/{user_id}_{image.filename}"
    with open(file_path, "wb") as f:
        f.write(await image.read())



    user = await user_service.upload_profile_picture(user_id, file_path)

    if user:
        return JSONResponse({
            "message": "Profile picture uploaded successfully",
            "user": user.model_dump()
        })
    return JSONResponse({"message": "User not found"}, status_code=404)


@router.get("/uploads/{filename}")
def get_image(user_id:str, filename: str):
    return FileResponse(f"uploads/{user_id}_{filename}")