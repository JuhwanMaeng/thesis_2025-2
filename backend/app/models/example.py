from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from bson import ObjectId


class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")


class ExampleModel(BaseModel):
    id: Optional[PyObjectId] = None
    name: str
    description: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class ExampleCreate(BaseModel):
    name: str
    description: Optional[str] = None


class ExampleUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

