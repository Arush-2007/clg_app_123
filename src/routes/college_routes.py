from fastapi import APIRouter
from services.college_service import college_service, CollegeAlreadyExistError
from models.college import College_Register, College_Club_Update
from fastapi.responses import JSONResponse

router = APIRouter()

@router.patch("/college_registering_endpoint")
async def college_registering(object: College_Register):
    try:
        dbcollege = college_service.register_college(object)
    
        return JSONResponse({
            "message": "College Profile setup successful",
            "College profile": dbcollege.model_dump()
        })
    
    except CollegeAlreadyExistError as e:
        return JSONResponse({
            "message": str(e)
        }, status_code=409)



@router.patch("/college_updating_endpoint")
async def college_registering(object: College_Club_Update):
    dbcollege_updated = college_service.update_college_details(object)
    
    return JSONResponse({
        "message": "College Profile updated successful",
        "College profile": dbcollege_updated.model_dump()
    })
    
