from pydantic import BaseModel, Field
from typing import List


class DepartmentModel(BaseModel):
    name: str
    status_id: int = Field(default=1)
    description: str
