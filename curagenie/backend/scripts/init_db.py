from backend.database import engine, Base
from backend.models.genomic_data import GenomicData
from backend.models.prs_score import PrsScore
from backend.models.user import User
from backend.models.consent_record import ConsentRecord
# import other models as needed

Base.metadata.create_all(engine)
print("Database tables created.")
