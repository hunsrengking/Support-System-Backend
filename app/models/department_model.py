from pydantic import BaseModel
from typing import List

class DepartmentModel(BaseModel):
    name: str
    status_id: int
    description: str