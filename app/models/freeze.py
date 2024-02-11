"""The streak-freeze table."""

import datetime
from pydantic import BaseModel, Field as field, computed_field, model_validator
from sqlmodel import SQLModel, Field, Session, select
from app.database import engine


class FreezeReport(BaseModel):
    """An incoming freeze report."""

    date_: str = field(default=None, exclude=True, alias="date")
    used: int = field(default=1, ge=0, le=1)

    @computed_field
    @property
    def date(self) -> datetime.date:
        if not self.date_:
            return datetime.date.today()
        return datetime.date.fromisoformat(self.date_)

    @model_validator(mode="after")
    def check_date(self) -> "FreezeReport":
        """Check that the date is today or earlier."""

        if self.date > datetime.date.today():
            raise ValueError("Future date passed.")
        return self


class Freeze(SQLModel, table=True):
    """The freeze table."""

    __tablename__ = "freezes"

    date: datetime.date = Field(primary_key=True)
    used: int


def upsert_freeze(freeze: Freeze):
    """Add/update the usage of a streak freeze."""

    with Session(engine) as session:
        query = select(Freeze).where(Freeze.date == freeze.date)
        row = session.exec(query).first()

        if row:
            row.used = freeze.used
            session.add(row)
            session.commit()
            session.refresh(row)
        else:
            session.add(freeze)
            session.commit()
            session.refresh(freeze)

