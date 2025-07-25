from sqlalchemy import Column, String, DateTime, ForeignKey
from .database import Base
import datetime

class ConsentRecord(Base):
    __tablename__ = 'consent_records'
    id = Column(String, primary_key=True)  # UUID or unique string
    user_id = Column(String, ForeignKey('users.id'), nullable=False)
    feature_id = Column(String, nullable=False)
    consent_version = Column(String, nullable=False)
    agreed_at = Column(DateTime, default=datetime.datetime.utcnow)
    ip_address = Column(String)
