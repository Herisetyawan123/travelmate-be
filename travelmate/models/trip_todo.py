from sqlalchemy import Column, Integer, String, ForeignKey, Enum
from sqlalchemy.orm import relationship
from ..models import Base

class TripTodo(Base):
    __tablename__ = 'trip_todos'

    id = Column(Integer, primary_key=True)
    trip_id = Column(Integer, ForeignKey('trips.id'), nullable=False)
    category = Column(String(100), nullable=False)
    description = Column(String(255), nullable=False)
    status = Column(Enum('done', 'not_yet', name='todo_status'), nullable=False, default='not_yet')

    trip = relationship('Trip', back_populates='todos')
