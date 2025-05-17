from sqlalchemy import Column, Integer, String, Text, Date, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from ..models import Base

class TripMember(Base):
    __tablename__ = 'trip_members'

    id = Column(Integer, primary_key=True)
    trip_id = Column(Integer, ForeignKey('trips.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    role = Column(String(50), default='member')

    trip = relationship('Trip', back_populates='members')
    user = relationship('User', back_populates='trip_memberships')
