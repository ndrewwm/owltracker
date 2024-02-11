"""OwlTracker API"""

from fastapi import FastAPI
from sqlmodel import SQLModel
from app.database import engine
from app.routers.streak import streak
from app.routers.stats import stats

app = FastAPI()
app.include_router(streak)
app.include_router(stats)


@app.get("/")
def hello():
    return {"detail": "Hello!"}


SQLModel.metadata.create_all(engine)
