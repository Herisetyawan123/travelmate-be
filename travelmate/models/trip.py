from sqlalchemy import Column, Integer, String, Text, Date, Boolean, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from ..models import Base

class Trip(Base):
    __tablename__ = 'trips'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    start_date = Column(Date)
    end_date = Column(Date)
    is_private = Column(Boolean, default=False)
    initial_budget = Column(Numeric(12, 2), default=0.00)

    thumbnail = Column(String(255))  

    owner_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    owner = relationship('User', back_populates='owned_trips')
    members = relationship('TripMember', back_populates='trip', cascade='all, delete-orphan')
    destinations = relationship('Destination', back_populates='trip')
    expenses = relationship('Expense', back_populates='trip', cascade='all, delete-orphan')
    comments = relationship('Comment', back_populates='trip', cascade='all, delete-orphan')
    itineraries = relationship('Itinerary', back_populates='trip', cascade='all, delete-orphan')
