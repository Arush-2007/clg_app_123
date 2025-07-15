from dotenv import load_dotenv
import os

load_dotenv()

DEBUG = os.getenv("DEBUG", True)