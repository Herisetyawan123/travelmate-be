from sqlalchemy import Column, Integer, String, Text, Date, ForeignKey
from sqlalchemy.orm import relationship
from ..models import Base

class Itinerary(Base):
    __tablename__ = 'itineraries'

    id = Column(Integer, primary_key=True)
    trip_id = Column(Integer, ForeignKey('trips.id'), nullable=False)
    day_name = Column(String(10), nullable=False)
    
    trip = relationship('Trip', back_populates='itineraries')
    activities = relationship('Activity', back_populates='itinerary', cascade='all, delete-orphan', order_by='Activity.order')

class Activity(Base):
    __tablename__ = 'activities'

    id = Column(Integer, primary_key=True)
    itinerary_id = Column(Integer, ForeignKey('itineraries.id'), nullable=False)
    order = Column(Integer, nullable=False)  # nomor urut kegiatan dalam hari
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)

    itinerary = relationship('Itinerary', back_populates='activities')
