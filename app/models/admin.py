from app.database import Base
from sqlalchemy import Column,String,Integer,Boolean,text


class Admin(Base):
    __tablename__="admins"
    id=Column(Integer,nullable=False,primary_key=True)
    first_name=Column(String,nullable=False)
    last_name=Column(String,nullable=False)
    email=Column(String,nullable=False,unique=True)
    password=Column(String,nullable=True)
    isActive=Column(Boolean, nullable=False,server_default=text("false"))