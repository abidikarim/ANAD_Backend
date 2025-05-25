from typing import Any, Dict, List, Optional
from pydantic import BaseModel, EmailStr
class OurBaseModel(BaseModel):
    class Config:
        from_attributes = True


class BaseOut(OurBaseModel):
    status:int
    message:str

class PagedResponse(BaseOut):
    page_size:int
    page_number:int
    total_pages:int
    total_records:int

class PayloadData(OurBaseModel):
    id:int

class AccessToken(BaseOut):
    access_token:str
    token_type:str

class AdminBase(OurBaseModel):
    first_name:str
    last_name:str
    email:EmailStr

class AdminOut(AdminBase,BaseOut):
    id:int

class AdminUpdate(AdminBase):
    password:str
    confirm_password:str

class MailData(OurBaseModel):
    emails: List[EmailStr]
    body: Dict[str, Any]
    template: str
    subject: str


class ConfirmData(OurBaseModel):
    password:str
    confirm_password:str
    code:str

class ForgetPassword(OurBaseModel):
    email:str


class PostBase(OurBaseModel):
    title:str
    description:str

class PostOut(PostBase):
    id:int
    image_link:str
    image_id:str

class PostsOut(PagedResponse):
    list:List[PostOut]

class PaginationParams(BaseModel):
    name_substr:Optional[str]=None
    page_number:int =1
    page_size:int = 10

class CloudinaryUploadResult(BaseModel):
    secure_url: str
    public_id: str

class ReportCreate(OurBaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone: str
    description: str

class ReportOut(ReportCreate):
    id:int

class ReportsOut(PagedResponse):
    list:List[ReportOut]