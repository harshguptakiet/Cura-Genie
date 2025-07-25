from sqlalchemy import Column, String, Float, DateTime, ForeignKey
from database import Base
import datetime

class PrsScore(Base):
    __tablename__ = 'prs_scores'
    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey('users.id'), nullable=False)
    genomic_data_id = Column(String, ForeignKey('genomic_data.id'), nullable=False)
    disease_type = Column(String, nullable=False)
    score = Column(Float, nullable=False)
    calculation_date = Column(DateTime, default=datetime.datetime.utcnow)
