from fastapi import APIRouter
from models.user import CreateUser, UpdateUser
from services import auth
from services.auth_service import UserAlreadyExistError, auth_service
from uuid import uuid4
from fastapi.responses import JSONResponse

router = APIRouter()

@router.get('/status_of_authentication_server')
async def status():
    return {
        "message": "user route is up"
    }

@router.put("/")
async def create_user(user: CreateUser):
    try:
        user_id = str(uuid4())
        dbuser = await auth.create_user(user_id, user)

        return JSONResponse({
            "message": "User created",
            "user": dbuser.model_dump()
        })
    except UserAlreadyExistError as e:
        return JSONResponse({
            "message": str(e)
        }, status_code=409)
    
# Doubt yeh hh ki can I directly this UserAlreadyexistError for paasword as well rather than Email

# @router.patch("/Update_Password")
# async def update_paasword(user: UpdateUser):
#     try:
#         dbuser = await auth.update_user(user_id , user)

#         return JSONResponse({
#             "message": "Paasword Updated",
#             "user_details": dbuser.model_dump()
#         })
#     except UserAlreadyExistError as e:
#         return JSONResponse({
#             "message": str(e)
#         }, status_code=409)    