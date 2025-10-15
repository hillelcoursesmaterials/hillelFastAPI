from pydantic import BaseModel, Field


class IdSchema(BaseModel):
    id: int = Field(examples=[1234], gt=0)


class InstanceVersion(BaseModel):
    version: int = Field(examples=[33, 88], gt=0)
