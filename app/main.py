"""OwlTracker API"""

from fastapi import FastAPI
from sqlmodel import SQLModel
from app.database import engine
from app.routers.streak import owl as streak
from app.routers.stats import owl as stats

app = FastAPI()
app.include_router(streak)
app.include_router(stats)

SQLModel.metadata.create_all(engine)
