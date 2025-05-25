from fastapi import APIRouter,Depends
from app.database import get_db
from app import schemas,models
from sqlalchemy.orm import Session
from app.utilities.send_email import send_mail
from app.utilities.OAuth2 import hash_password
import uuid
router = APIRouter(prefix="/admin",tags=["Admin"])

@router.post("")
async def create_admin(admin_data:schemas.AdminBase,db:Session=Depends(get_db)):
    try:
        # Check if email already exists
        existing_admin = db.query(models.Admin).filter(models.Admin.email == admin_data.email).first()
        if existing_admin:
            return schemas.BaseOut(status=400,message="Admin with this email already exists")
        # Create a new Admin object from Pydantic data
        new_admin = models.Admin(**admin_data.model_dump())
        db.add(new_admin)
        db.flush()
        new_token = models.Token(token=uuid.uuid1(),admin_id=new_admin.id)
        db.add(new_token)
        # Send email
        await send_mail(schemas.MailData(
            emails=[new_admin.email],
            body={"name": f"{new_admin.first_name} {new_admin.last_name}","code":new_token.token},
            template="confirm_account.html",
            subject="Confirm Account",
        ))   
        db.commit()
        return schemas.BaseOut(status=201,message="Admin account created successfully. And activation email has been sent.")
    except Exception as error:
        db.rollback()
        return schemas.BaseOut(status=400,message="Admin creation failed. Please try again.")

@router.get("/{id}")
def get_by_id(id:int,db:Session = Depends(get_db)):
    try:
        admin = db.query(models.Admin).filter(models.Admin.id == id).first()
        if admin:
            return schemas.AdminOut(id=admin.id,first_name=admin.first_name,last_name=admin.last_name,email=admin.email,status=200,message="Admin fetched")
        return schemas.BaseOut(status=404,message="Admin not found")
    except Exception as error:
        return schemas.BaseOut(status=400,message="Somthing went wrong.")

@router.put("/{id}")
def edit(id:int,data:schemas.AdminUpdate,db:Session = Depends(get_db)):
    try:
        if data.password != data.confirm_password:
            return schemas.BaseOut(status=400,message="Password and confirm password must match.")
        admin_db = db.query(models.Admin).filter(models.Admin.email == data.email, models.Admin.id != id).first()
        if admin_db:
            return schemas.BaseOut(status=400,message="This email already used.")
        data_dict = data.model_dump()
        data_dict.pop("confirm_password")
        data_dict["password"] = hash_password(data_dict["password"])
        updated = db.query(models.Admin).filter(models.Admin.id == id).update(data_dict)
        if not updated:
            return schemas.BaseOut(status=400,message="Update admin failed. Please try again.")
        db.commit()
        return schemas.BaseOut(status=200,message="Admin updated successfuly.")
    except Exception as error:
        db.rollback()
        return schemas.BaseOut(status=400,message="Somthing went wrong. Please try again.")
        
