import json
from fastapi import APIRouter, Depends, File, Form, UploadFile
from app import schemas
from app.database import get_db
from sqlalchemy.orm import Session
from app import models
from sqlalchemy import or_
from app.utilities.upload_file import upload_to_cloudinary
import cloudinary.uploader
from app.utilities.OAuth2 import get_current_admin

router = APIRouter(prefix="/post",tags=["Post"])

@router.get("")
def get_posts(pg_params:schemas.PaginationParams = Depends(),db:Session = Depends(get_db)):
    try:
        skip = (pg_params.page_number - 1) * pg_params.page_size
        limit = pg_params.page_size
        query = db.query(models.Post)
        if pg_params.name_substr:
            query = query.filter(or_(models.Post.title.ilike(f"%{pg_params.name_substr}%"),models.Post.description.ilike(f"%{pg_params.name_substr}%")))
        total_records = query.count()
        total_pages = (total_records + limit - 1) // limit
        posts = query.offset(skip).limit(limit).all()
        return schemas.PostsOut(
            status=200,
            message="Posts fetched successfully",
            page_size=pg_params.page_size,
            page_number=pg_params.page_number,
            total_pages=total_pages,
            total_records=total_records,
            list=posts
        )
    except Exception as error:
        return schemas.BaseOut(status=400,message="Somthing went wrong")

@router.post("", response_model=schemas.BaseOut)
async def create_post(post_data: str = Form(...), image: UploadFile = File(...), db: Session = Depends(get_db),current_admin = Depends(get_current_admin)):
    try:
        upload_result=None
        # Step 1: Parse post_data
        post_dict = json.loads(post_data)
        post_schema = schemas.PostBase(**post_dict)
        # Step 2: Upload image to Cloudinary
        upload_result = await upload_to_cloudinary(image)
        # Step 3: Create Post in DB
        new_post = models.Post(
            title=post_schema.title,
            description=post_schema.description,
            image_link=upload_result.secure_url,
            image_id=upload_result.public_id
            )
        db.add(new_post)
        db.commit()
        db.refresh(new_post)
        return schemas.BaseOut(status=201, message="Post created successfully")
    except Exception as e:
        db.rollback()
        if upload_result:
            cloudinary.uploader.destroy(upload_result.public_id)
        return schemas.BaseOut(status_code=400, message="Somthing went wrong. Please try again.")


@router.put("/{id}", response_model=schemas.BaseOut)
async def update_post(id: int, post_data: str = Form(...), image: UploadFile = File(None), db: Session = Depends(get_db),current_admin = Depends(get_current_admin)):
    try:
        upload_result=None
        # Get existing post
        post = db.query(models.Post).filter(models.Post.id == id).first()
        if not post:
            return schemas.BaseOut(status=404,message="Post not found")
        # Parse JSON post data
        post_dict = json.loads(post_data)
        post_schema = schemas.PostBase(**post_dict)
        # If a new image is uploaded
        if image:
            # Delete old image if tracked with public_id
            if post.image_id:
                    cloudinary.uploader.destroy(post.image_id)
            # Upload new image
            upload_result = await upload_to_cloudinary(image)
            post.image_link = upload_result.secure_url
            post.image_id = upload_result.public_id
        # Update other fields
        post.title = post_schema.title
        post.description = post_schema.description
        db.commit()
        db.refresh(post)
        return schemas.BaseOut(status=200, message="Post updated successfully")
    except Exception as e:
        db.rollback()
        if upload_result:
            cloudinary.uploader.destroy(upload_result.public_id)
        return schemas.BaseOut(status_code=400, message="Somthing went wrong. Please try again.")

@router.delete("/{post_id}", response_model=schemas.BaseOut)
def delete_post(post_id: int, db: Session = Depends(get_db),current_admin = Depends(get_current_admin)):
    try:
        # Fetch post from DB
        post = db.query(models.Post).filter(models.Post.id == post_id).first()
        if not post:
            return schemas.BaseOut(status_code=404, message="Post not found")
        # Delete image from Cloudinary if exists
        if post.image_id:
                cloudinary.uploader.destroy(post.image_id)
        # Delete post from DB
        db.delete(post)
        db.commit()
        return schemas.BaseOut(status=200, message="Post deleted successfully")
    except Exception as e:
        db.rollback()
        return schemas.BaseOut(status_code=500, message="Somthing went wrong. Please try again.")