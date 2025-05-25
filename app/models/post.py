from app.database import Base
from sqlalchemy import Column,String,Integer

class Post(Base):
    __tablename__="posts"
    id= Column(Integer,primary_key=True,nullable=False)
    title= Column(String,nullable=False)
    description= Column(String,nullable=False)
    image_link= Column(String,nullable=False)
    image_id = Column(String,nullable=False)