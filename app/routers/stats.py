"""The weekly stats endpoints."""

import datetime
from fastapi import APIRouter, HTTPException
from sqlmodel import Session, select, between
from sqlalchemy.exc import IntegrityError, NoResultFound
from app.database import engine
from app.models.weekly import WeeklyReport, WeeklyStats, upsert_weekly

stats = APIRouter(prefix="/owl/stats")


@stats.get("/week", tags=["weekly stats"])
def get_week(date_end: datetime.date | None = None) -> WeeklyStats:
    """Get a weekly report, based on the supplied date. Defaults to today."""

    # c.f. https://stackoverflow.com/a/51721530
    if not date_end:
        date_end = datetime.date.today() - datetime.timedelta(
            days=((datetime.date.today().isoweekday() + 1) % 7)
        )

    with Session(engine) as session:
        query = select(WeeklyStats).where(WeeklyStats.date_end == date_end)
        row = session.exec(query).first()

    if not row:
        raise HTTPException(status_code=204)

    return row


@stats.get("/weeks", tags=["weekly stats"])
def get_weeks(
    start: datetime.date = datetime.date(1900, 1, 1),
    end: datetime.date = datetime.date(2999, 12, 31),
) -> list[WeeklyStats]:
    """Get a range of weekly reports, based on start/end dates."""

    with Session(engine) as session:
        query = select(WeeklyStats).where(
            between(WeeklyStats.date_end, start, end)
        )
        rows = session.exec(query).all()

    if not rows:
        raise HTTPException(status_code=204)

    return rows


@stats.put("/week", tags=["weekly stats", "report"])
def report_week(data: WeeklyReport) -> dict[str, str]:
    """Report on a single week of activity."""

    week = WeeklyStats(**data.model_dump())
    upsert_weekly(week)

    return {"detail": "Week recorded."}


@stats.put("/weeks", tags=["weekly stats", "report"])
def report_weeks(data: list[WeeklyReport]) -> dict[str, str]:
    """Report on one or more weeks of activity. Meant to store metrics provided via Duolingo's
    weekly email."""

    data = [WeeklyStats(**week.model_dump()) for week in data]
    for week in data:
        upsert_weekly(week)

    return {"detail": f"{len(data)} weeks recorded."}


@stats.delete("/week", tags=["weekly stats"])
def delete_week():
    """"""


@stats.delete("/weeks", tags=["weekly stats"])
def delete_week():
    """"""
