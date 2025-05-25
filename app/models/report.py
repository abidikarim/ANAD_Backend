from app.database import Base
from sqlalchemy import Column,String,Integer

class Report(Base):
    __tablename__="reports"
    id= Column(Integer,primary_key=True,nullable=False)
    first_name= Column(String,nullable=False)
    last_name= Column(String,nullable=False)
    email= Column(String,nullable=False)
    phone= Column(String,nullable=False)
    description= Column(String,nullable=False)