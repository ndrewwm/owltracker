"""The streak freeze endpoints."""

import datetime
from fastapi import APIRouter, HTTPException
from sqlmodel import Session, select, between, or_, and_
from sqlalchemy.exc import IntegrityError, NoResultFound
from app.database import engine
from app.models.freeze import FreezeReport, Freeze, upsert_freeze

streak = APIRouter(prefix="/owl/streak")


@streak.get("/freeze", tags=["freezes"])
def get_freeze(date: datetime.date = datetime.date.today()) -> Freeze:
    """Check the status of a date."""

    with Session(engine) as session:
        query = select(Freeze).where(Freeze.date == date)
        row = session.exec(query).first()

    if not row:
        raise HTTPException(status_code=204)

    return row


@streak.get("/freezes", tags=["freezes"])
def get_freezes(
    start: datetime.date = datetime.date(1900, 1, 1),
    end: datetime.date = datetime.date(2999, 12, 31),
    used: int | None = None,
) -> list[Freeze]:
    """Get the results for a set of dates."""

    with Session(engine) as session:
        query = select(Freeze).where(
            and_(
                between(Freeze.date, start, end),
                or_(Freeze.used == used, used is None),
            )
        )
        rows = session.exec(query).all()

    if not rows:
        raise HTTPException(status_code=204)

    return rows


@streak.put("/freeze", tags=["freezes", "report"])
def report_freeze(data: FreezeReport) -> dict[str, str]:
    """Report the usage of a streak freeze."""

    freeze = Freeze(**data.model_dump())
    upsert_freeze(freeze)

    return {"detail": f"Freeze recorded for date: {freeze.date}."}


@streak.put("/freezes", tags=["freezes", "report"])
def report_freezes(data: list[FreezeReport]) -> dict[str, str]:
    """Report the usage of multiple streak freezes."""

    freezes = [Freeze(**freeze.model_dump()) for freeze in data]
    for freeze in freezes:
        upsert_freeze(freeze)

    return {"detail": f"{len(freezes)} freezes recorded."}


@streak.delete("/freeze", tags=["freezes"])
def delete_freeze(date: datetime.date = datetime.date.today()) -> dict[str, str]:
    """Delete the record for a given date."""

    with Session(engine) as session:
        try:
            query = select(Freeze).where(Freeze.date == date)
            row = session.exec(query).one()
        except NoResultFound as err:
            raise HTTPException(status_code=204) from err

        session.delete(row)
        session.commit()

    return {"detail": "Freeze deleted."}


@streak.delete("/freezes", tags=["freezes"])
def delete_freezes(start: datetime.date, end: datetime.date) -> dict[str, str]:
    """Delete several records between a start and end date."""

    with Session(engine) as session:
        query = select(Freeze).where(between(Freeze.date, start, end))
        rows = session.exec(query).all()

        if not rows:
            raise HTTPException(status_code=204)

        for row in rows:
            session.delete(row)

        session.commit()

    return {"detail": f"{len(rows)} freezes deleted."}

