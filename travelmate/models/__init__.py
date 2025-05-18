from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session, declarative_base
from ..config import DATABASE_URL


engine = create_engine(DATABASE_URL, echo=True)

SessionLocal = scoped_session(sessionmaker(bind=engine))

Base = declarative_base()

from .user import User
from .trip import Trip
from .trip_member import TripMember
from .destination import Destination
from .expense import Expense
from .comment import Comment
from .itinerary import Itinerary
from .itinerary import Activity
from .trip_todo import TripTodo
from .notification import Notification
