from sqlalchemy import create_engine
from travelmate.models import Base  # pastikan ini dari declarative_base()

# Ganti dengan info koneksi PostgreSQL kamu
DATABASE_URL = 'postgresql://postgres:root@localhost:5432/travelmate_db'
engine = create_engine(DATABASE_URL)

# Drop semua tabel
Base.metadata.drop_all(bind=engine)
print("✅ Semua tabel berhasil di-drop.")

# Buat ulang semua tabel
Base.metadata.create_all(bind=engine)
print("✅ Semua tabel berhasil dibuat ulang.")
