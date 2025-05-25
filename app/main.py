from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import cloudinary
from app.config import settings
from app.routers import admin,auth,post,report
app = FastAPI()


# Include routers
app.include_router(admin.router)
app.include_router(auth.router)
app.include_router(post.router)
app.include_router(report.router)
# CORS config
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Cloudinary config
cloudinary.config(
    cloud_name=settings.CLOUD_Name,
    api_key=settings.API_KEY,
    api_secret=settings.API_SECRET,
)

@app.get("/")
def root() :
    return {"Hello ANAD"}
