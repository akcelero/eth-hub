from uuid import UUID

from pydantic import BaseModel


class BaseKey(BaseModel):
    id: UUID
    address: bytes
