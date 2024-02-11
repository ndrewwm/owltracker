""""""

from datetime import date, timedelta
from pydantic import BaseModel, NonNegativeInt, Field as field, computed_field, model_validator
from sqlmodel import SQLModel, Field, Session, select
from app.database import engine


class WeeklyReport(BaseModel):
    """An incoming weekly report."""

    date_start_: str = field(alias="date_start", exclude=True)
    date_end_: str = field(alias="date_end", exclude=True)
    exp: NonNegativeInt = field(default=None)
    current_streak: NonNegativeInt = field(default=None)
    num_freezes: NonNegativeInt = field(default=None, lt=8)
    num_lessons: NonNegativeInt = field(default=None)
    num_minutes: NonNegativeInt = field(default=None)

    @computed_field
    @property
    def date_start(self) -> date:
        return date.fromisoformat(self.date_start_)

    @computed_field
    @property
    def date_end(self) -> date:
        return date.fromisoformat(self.date_end_)

    @model_validator(mode="after")
    def check_dates(self) -> "WeeklyReport":
        """Ensure that the start date is a week less than the end-date."""

        if self.date_start != self.date_end - timedelta(days=6):
            raise ValueError("Invalid dates provided.")
        return self


class WeeklyStats(SQLModel, table=True):
    """Table for the weekly stats report."""

    __tablename__ = "weekly_stats"

    date_start: date = Field(primary_key=True)
    date_end: date = Field(primary_key=True)
    exp: NonNegativeInt = Field(nullable=True)
    current_streak: NonNegativeInt = Field(nullable=True)
    num_freezes: NonNegativeInt = Field(nullable=True)
    num_lessons: NonNegativeInt = Field(nullable=True)
    num_minutes: NonNegativeInt = Field(nullable=True)


def upsert_weekly(week: WeeklyStats) -> None:
    """Add/update a new weekly report."""

    with Session(engine) as session:
        query = select(WeeklyStats).where(
            WeeklyStats.date_start == week.date_start,
            WeeklyStats.date_end == week.date_end,
        )
        row = session.exec(query).first()
        if row:
            row.exp = week.exp
            row.current_streak = week.current_streak
            row.num_freezes = week.num_freezes
            row.num_lessons = week.num_lessons
            row.num_minutes = week.num_minutes

            session.add(row)
            session.commit()
            session.refresh(row)
        else:
            session.add(week)
            session.commit()
            session.refresh(week)
