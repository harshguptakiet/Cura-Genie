from sqlalchemy import Column, String, DateTime
from database import Base
import datetime

class User(Base):
    __tablename__ = 'users'
    id = Column(String, primary_key=True)  # UUID or unique string
    firebase_uid = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    role = Column(String, default='user')
    registration_date = Column(DateTime, default=datetime.datetime.utcnow)
