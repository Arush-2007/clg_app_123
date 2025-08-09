# from src.models import college
from models.college import College_Register, College_Club_Update
from utils.prisma import db
from prisma_client.errors import UniqueViolationError


class CollegeAlreadyExistError(Exception):
    def __init__(self, value: str):
        self.value = value
        super().__init__(f"College with name {self.value} already exist")       

class CollegeService:
    def __init__(self):
        pass

    async def register_college(self, college : College_Register):
        try:
            return await db.college.create(data ={
            "college_name" : college.college_name,
            "clubs_registered" : college.clubs_recognized
        })

        except UniqueViolationError as e:
            raise CollegeAlreadyExistError(college.college_name)


    async def update_college_details(self, college_name:str, college : College_Club_Update):
        finalised_college_details = college.model_dump(exclude_unset=True, exclude_none=True)
        return await db.college.update(data = finalised_college_details, where = {"college name" : college_name})


college_service = CollegeService()           