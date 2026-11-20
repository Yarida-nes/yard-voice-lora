from typing import Literal, Optional

from pydantic import BaseModel, Field

Place = Literal["door_01", "door_02", "door_03", "door_04", "door_05", "door_06",
                "door_07", "door_08", "staging", "parking"]


class Command(BaseModel):
    action: Optional[Literal["move", "park", "release", "status"]] = Field(
        description="What the worker wants done, or null if unclear")
    unit: Optional[str] = Field(
        description="Trailer number as 4 digits, exactly as said, or null")
    to: Optional[Place] = Field(
        description="Where it goes: a door or staging for move, parking for park, else null")
