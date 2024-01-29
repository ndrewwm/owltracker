"""OwlTracker API"""

from fastapi import FastAPI
from sqlmodel import SQLModel
from app.routers.report import rpt
from app.database import engine

app = FastAPI()
app.include_router(rpt)

SQLModel.metadata.create_all(engine)
