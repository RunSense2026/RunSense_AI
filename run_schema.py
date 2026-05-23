from pydantic import BaseModel


class RunData(BaseModel):
    pace: float
    heart_rate: int
    cadence: int
from pydantic import BaseModel


class RunData(BaseModel):

    user_id: str

    pace: float
    heart_rate: int
    cadence: int