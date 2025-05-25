from fastapi import UploadFile
import cloudinary.uploader
from app.schemas import CloudinaryUploadResult 

async def upload_to_cloudinary(file: UploadFile) -> CloudinaryUploadResult:
    result = cloudinary.uploader.upload(file.file, folder="posts")
    return CloudinaryUploadResult(secure_url=result["secure_url"], public_id=result["public_id"])