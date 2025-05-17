from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, Text
from sqlalchemy.orm import relationship
from ..models import Base

class Expense(Base):
    __tablename__ = 'expenses'

    id = Column(Integer, primary_key=True)
    trip_id = Column(Integer, ForeignKey('trips.id'), nullable=False)
    name = Column(String(255), nullable=False)  # Nama atau deskripsi expense
    amount = Column(Float, nullable=False)      # Nominal biaya
    date = Column(Date)                          # Tanggal pengeluaran/perkiraan
    category = Column(String(100))               # Kategori seperti transport, food, dll
    notes = Column(Text)                         # Catatan tambahan

    trip = relationship('Trip', back_populates='expenses')
