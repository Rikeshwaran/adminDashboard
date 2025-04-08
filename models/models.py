from sqlalchemy import create_engine, Column, Integer, String, Date, JSON
from sqlalchemy.ext.declarative import declarative_base
import os

Base = declarative_base()
DATABASE_URL = "mysql+mysqlconnector://root:2004@localhost/admindashboard"

class Project(Base):
    __tablename__ = 'projects'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    entry_id = Column(String(255))
    status = Column(String(50))
    start_date = Column(Date)
    end_date = Column(Date)
    file_paths = Column(JSON)
    planned_bys = Column(JSON)
    planned_ats = Column(JSON)
    revision_ids = Column(JSON)

engine = create_engine(DATABASE_URL)
Base.metadata.create_all(bind=engine)