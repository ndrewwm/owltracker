"""The streak-freeze table."""

from sqlmodel import SQLModel, Field
from datetime import date

class Freeze(SQLModel, table=True):
    """The freeze table."""

    __tablename__ = "freezes"

    date: date = Field(default=date.today(), primary_key=True)
    used: bool = Field(default=True)
