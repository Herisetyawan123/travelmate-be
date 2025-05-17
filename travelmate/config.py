import os
from dotenv import load_dotenv

load_dotenv()  # load .env file

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://rtoot:root@localhost:5432/travelmate_db")
