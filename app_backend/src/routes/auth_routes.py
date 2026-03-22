from fastapi import APIRouter
from models.user import CreateUser, UpdateUser
from services import auth
from services.auth_service import UserAlreadyExistError, auth_service, DifferentPasswordNeeded, UserNotFoundError, InvalidCredentialsError
from uuid import uuid4
from fastapi.responses import JSONResponse

router = APIRouter()

@router.get('/status_of_authentication_server')
async def status():
    return {
        "message": "user route is up"
    }

@router.put("/User_Auth")
async def create_user(user: CreateUser):
    try:
        user_id = str(uuid4())
        dbuser = await auth.create_user(user_id, user)

        return JSONResponse({
            "Success": "True",
            "message": "User created"
        })
    except UserAlreadyExistError as e:
        return JSONResponse({
            "message": str(e)
        }, status_code=409)
    

@router.put("/Password_Update/{user_id}")
async def update_user_endpoint(user: UpdateUser, user_id :str):
    try:
        dbuser = await auth.update_user(user_id, user)

        return JSONResponse({
            "Success": "True",
            "message": "User passwoed updated"
        })
    except DifferentPasswordNeeded as e:
        return JSONResponse({
            "message" : str(e)
        }, status_code=409)
    

@router.put("/User_Log_in")
async def user_login_endpoint(user_log_r : CreateUser):
    try:
        result = await auth.login_user_detailed(user_log_r)
        if result == True:
            return JSONResponse({
                "is_login_valid" : "Yes"
            })
        
    except (UserNotFoundError, InvalidCredentialsError) as e:
        return JSONResponse({
            "message": str(e)
        }, status_code=401)

