from fastapi import APIRouter
from src.services.clubs_service import clubs_service, ClubAlreadyExistError, ClubDoseNotExistError
from models.clubs import RegisterClub, UpdateClub
from fastapi.responses import JSONResponse

router = APIRouter()

@router.patch('/club_registering_endpoint')
async def club_registering(club : RegisterClub):
    try:
        club = clubs_service.register_club(club)
        if club:
            return JSONResponse ({
                "message" : "Club registered",
                "club_profile": club.model_dump()
            })
    except ClubAlreadyExistError as e:
        return JSONResponse({
            "message" : str(e)
        }, status_code= 409)
    
# @router.patch('/club_updating_endpoint/{club_id}')
# async def club_updating(club_id :str,club : UpdateClub):
#     try:
#         unupdated_club = clubs_service.get_club_by_id(club_id)
#         club = clubs_service.update_club_details(club_id, club)
#         if club != unupdated_club:
#             return JSONResponse ({
#                 "message" : "Club registered",
#                 "club_profile": club.model_dump()
#             })
        
#         if club == unupdated_club:
#             return JSONResponse({
#                 "message": "No changes detected - club data was already up to date",
#                 "club_profile": club.model_dump()
#             })
#     except ClubDoseNotExistError as e:
#         return JSONResponse({
#             "message" : str(e)
#         }, status_code= 409)    

# @router.patch('/club_updating_endpoint/{club_id}')
# async def club_updating(club_id :str,club : UpdateClub):
#     club_dict = club.model_dump(exclude_unset=True)

#     if not club_dict:
