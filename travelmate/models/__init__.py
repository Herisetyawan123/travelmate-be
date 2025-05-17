from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session, declarative_base
from ..config import DATABASE_URL


engine = create_engine(DATABASE_URL, echo=True)

SessionLocal = scoped_session(sessionmaker(bind=engine))

Base = declarative_base()

from .user import User
from .trip import Trip
from .trip_member import TripMember
