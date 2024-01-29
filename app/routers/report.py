"""The /report paths, used for uploading data."""

from datetime import date
from fastapi import APIRouter, HTTPException
from sqlmodel import Session, select
from app.database import engine
from app.models.freeze import Freeze

rpt = APIRouter(prefix="/report")


# TODO: need to create a schema for lists of dates
@rpt.get("/freeze")
def get_freeze(dt: date | list[date]) -> list[Freeze] | list:
    """Check the status of a date."""

    if not isinstance(dt, list):
        dt = list(dt)

    with Session(engine) as session:
        query = select(Freeze).where(Freeze.date in dt)
        rows = session.exec(query).all()

    return rows


@rpt.post("/freeze", status_code=201)
def report_freeze(freeze: Freeze | list[Freeze]):
    """Report the usage of a streak freeze."""

    if not isinstance(freeze, list):
        freezes = list(freeze)

    with Session(engine) as session:
        for freeze in freezes:
            session.add(freeze)
        session.commit()

    return {"detail": "Usage recorded."}


@rpt.patch("/freeze")
def update_freeze(freeze: Freeze) -> Freeze:
    """Update the usage value for a given day."""

    with Session(engine) as session:
        query = select(Freeze).where(Freeze.date == freeze.date)
        row = session.exec(query).first()

        if not row:
            raise HTTPException(400, detail=f"No record for {freeze.date} found.")

        row.used = freeze.used
        session.add(row)
        session.commit()
        session.refresh(row)
    
    return row


@rpt.delete("/freeze")
def delete_freeze(date: date):
    """Delete the record for a given date."""

    with Session(engine) as session:
        query = select(Freeze).where(Freeze.date == date)
        row = session.exec(query).first()
