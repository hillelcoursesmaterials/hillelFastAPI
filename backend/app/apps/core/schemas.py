from pydantic import BaseModel, Field

class IdSchema(BaseModel):
    id: int = Field(examples=[1234], gt=0)
