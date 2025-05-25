from fastapi import APIRouter,Depends
from app import schemas
from app.utilities.OAuth2 import create_access_token,get_current_admin,verify_password,hash_password
from app.database import get_db
from sqlalchemy.orm import Session
from app import models,schemas
from fastapi.security import  OAuth2PasswordRequestForm
from datetime import datetime
from app.utilities.send_email import send_mail
import uuid
router = APIRouter(prefix="/auth", tags=["Authenticate"])


@router.post("/login")
def login(admin_credentials:OAuth2PasswordRequestForm=Depends(),db:Session = Depends(get_db)):
    try:
       admin = db.query(models.Admin).filter(models.Admin.email == admin_credentials.username).first()
       if not admin:
           return schemas.BaseOut(status=404,message="Admin with is email not found")
       if not verify_password(admin_credentials.password,admin.password):
            return schemas.BaseOut(status=400,message="Wrong password")
       access_token = create_access_token({"id":admin.id})
       return schemas.AccessToken(token_type="Bearer",access_token=access_token,status=200,message="Login successfuly")
    except Exception as error:
        return schemas.BaseOut(status_code=400, detail=str(error))

@router.post("/forget_password")
async def forget_password(data:schemas.ForgetPassword,db:Session=Depends(get_db)):
    try:
        admin = db.query(models.Admin).filter(models.Admin.email == data.email).first()
        if not admin:
            return schemas.BaseOut(status=404,message="Admin with is email not found")
        token = models.Token(token=uuid.uuid1(),admin_id=admin.id)
        db.add(token)
        await send_mail(schemas.MailData(
            emails=[admin.email],
            body={"name": f"{admin.first_name} {admin.last_name}","code":token.token},
            template="reset_password.html",
            subject="Reset Password",
        )) 
        db.commit()
        return schemas.BaseOut(status=200,message="Email send with successfuly")
    except Exception as error:
        db.rollback()
        return schemas.BaseOut(status=400,message="Email send failed. Please try again.")  
    

@router.patch("/confirm_account")
def confirm_account(confirm_data:schemas.ConfirmData,db:Session=Depends(get_db)):
    try:
        if confirm_data.password != confirm_data.confirm_password:
            return schemas.BaseOut(status=400,message="Password and confirm password must match.")
        token = db.query(models.Token).filter(models.Token.token == confirm_data.code).first()
        if token.isUsed:
            return schemas.BaseOut(status=400,message="Link already used")
        if (datetime.now() - token.created_at.replace(tzinfo=None)).days > 1:
            return schemas.BaseOut(status=400,message="Link expired")
        db.query(models.Admin).filter(models.Admin.id == token.admin_id).update({models.Admin.password:hash_password(confirm_data.password)})
        db.query(models.Token).filter(models.Token.id == token.id).update({models.Token.isUsed:True})
        db.commit()
        return schemas.BaseOut(status=200,message="Account confirmed successfuly")
    except Exception as error:
        return schemas.BaseOut(status=400,message="Confirm account failed. Please try again.")
    
@router.patch("/reset_password")
def reset_password(confirm_data:schemas.ConfirmData,db:Session=Depends(get_db)):
    try:
        if confirm_data.password != confirm_data.confirm_password:
            return schemas.BaseOut(status=400,message="Password and confirm password must match.")
        token = db.query(models.Token).filter(models.Token.token == confirm_data.code).first()
        if token.isUsed:
            return schemas.BaseOut(status=400,message="Link already used")
        if (datetime.now() - token.created_at.replace(tzinfo=None)).days > 1:
            return schemas.BaseOut(status=400,message="Link expired")
        db.query(models.Admin).filter(models.Admin.id == token.admin_id).update({models.Admin.password:hash_password(confirm_data.password)})
        db.query(models.Token).filter(models.Token.id == token.id).update({models.Token.isUsed:True})
        db.commit()
        return schemas.BaseOut(status=200,message="Password updated successfuly")
    except Exception as error:
        return schemas.BaseOut(status=400,message="Update password failed. Please try again.")