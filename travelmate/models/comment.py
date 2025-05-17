from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from ..models import Base

class Comment(Base):
    __tablename__ = 'comments'

    id = Column(Integer, primary_key=True)
    trip_id = Column(Integer, ForeignKey('trips.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relasi ke trip
    trip = relationship('Trip', back_populates='comments')

    # Relasi ke user yang membuat komentar
    user = relationship('User')
