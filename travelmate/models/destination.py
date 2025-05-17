from sqlalchemy import Column, Integer, String, Float, Text, ForeignKey
from sqlalchemy.orm import relationship
from ..models import Base

class Destination(Base):
    __tablename__ = 'destinations'

    id = Column(Integer, primary_key=True)
    trip_id = Column(Integer, ForeignKey('trips.id'), nullable=False)
    name = Column(String(255), nullable=False)           # Nama tempat tujuan
    latitude = Column(Float, nullable=False)              # Koordinat lintang
    longitude = Column(Float, nullable=False)             # Koordinat bujur
    address = Column(String(255))                          # Alamat lengkap (opsional)
    description = Column(Text)                             # Deskripsi atau info detail
    notes = Column(Text)                                   # Catatan tambahan

    trip = relationship('Trip', back_populates='destinations')
