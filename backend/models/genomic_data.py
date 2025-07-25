from sqlalchemy import Column, String, DateTime, JSON, ForeignKey
from database import Base
import datetime

class GenomicData(Base):
    __tablename__ = 'genomic_data'
    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey('users.id'), nullable=False)
    file_name = Column(String, nullable=False)
    s3_key = Column(String, nullable=False)
    file_type = Column(String, nullable=False)
    upload_date = Column(DateTime, default=datetime.datetime.utcnow)
    status = Column(String, default='uploaded')
    metadata_json = Column(JSON)
