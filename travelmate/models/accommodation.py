from sqlalchemy import Column, Integer, String, Text, Float, ForeignKey
from sqlalchemy.orm import relationship
from ..models import Base

class Accommodation(Base):
    __tablename__ = 'accommodations'

    id = Column(Integer, primary_key=True)
    trip_id = Column(Integer, ForeignKey('trips.id'), nullable=False)
    name = Column(String(255), nullable=False)
    address = Column(String(255))
    price_per_night = Column(Float)
    count_night = Column(Integer)
    notes = Column(Text)

    trip = relationship('Trip', back_populates='accommodations')