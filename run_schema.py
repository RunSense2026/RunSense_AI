from pydantic import BaseModel


class RunData(BaseModel):
    pace: float
    heart_rate: int
    cadence: int
