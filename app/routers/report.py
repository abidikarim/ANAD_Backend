from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app import schemas, models
from app.database import get_db

router = APIRouter(prefix="/report", tags=["Report"])

@router.get("", response_model=schemas.ReportsOut)
def get_reports(pg_params: schemas.PaginationParams = Depends(), db: Session = Depends(get_db)):
    try:
        skip = (pg_params.page_number - 1) * pg_params.page_size
        limit = pg_params.page_size
        query = db.query(models.Report)
        if pg_params.name_substr:
            name_filter = f"%{pg_params.name_substr}%"
            query = query.filter(or_(models.Report.first_name.ilike(name_filter),models.Report.last_name.ilike(name_filter),models.Report.email.ilike(name_filter)))
        total_records = query.count()
        reports = query.offset(skip).limit(limit).all()
        total_pages = (total_records + limit - 1) // limit
        return schemas.ReportsOut(
            status=200,
            message="Reports fetched successfully",
            page_size=limit,
            page_number=pg_params.page_number,
            total_pages=total_pages,
            total_records=total_records,
            list=reports
        )
    except Exception as error:
        return schemas.BaseOut(status=400,message="Somthing went wrong.")

@router.post("", response_model=schemas.BaseOut)
def create_report(report: schemas.ReportCreate, db: Session = Depends(get_db)):
    try:
        new_report = models.Report(**report.model_dump())
        db.add(new_report)
        db.commit()
        db.refresh(new_report)
        return schemas.BaseOut(status=201, message="Report send successfully")
    except Exception as error:
        db.rollback()
        return schemas.BaseOut(status=400,message="Somthing went wrong.")