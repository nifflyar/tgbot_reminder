from datetime import datetime, time
from typing import Optional, List

from pydantic import BaseModel, ConfigDict, Field, ValidationError, conlist, field_validator, validator



class DesciptionSchema(BaseModel):
    description: str = Field(max_length=36)



class TimeSchema(BaseModel):
    time: str

    @field_validator("time")
    @classmethod
    def normalize_time(cls, v: str) -> str:
        try:
            h, m = map(int, v.strip().split(":"))
            if not (0 <= h <= 23 and 0 <= m <= 59):
                raise ValueError
            return f"{h:02}:{m:02}"
        except:
            raise ValueError


class IntervalSchema(BaseModel):
    interval: int = Field(ge=15, le=300)


class DateSchema(BaseModel):
    date_ : str

    @validator("date_")
    def validate_date(cls, v):
        try:
            year = datetime.now().year
            try:
                return datetime.strptime(f"{v}/{year}", "%d/%m/%Y").date()
            except ValueError:
                return datetime.strptime(f"{v}/2024", "%d/%m/%Y").date()
        except Exception:
            raise ValueError("Дата должна быть в формате DD/MM")


class MonthSchema(BaseModel):
    month: int = Field(ge=1, le=12)
