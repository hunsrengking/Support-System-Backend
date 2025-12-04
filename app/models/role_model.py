from pydantic import BaseModel
from typing import List

class RoleCreateReq(BaseModel):
    name: str
    description: str


class RolePermsReq(BaseModel):
    permissions: List[int]
