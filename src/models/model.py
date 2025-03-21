from typing import Optional

import strawberry
from pydantic import BaseModel as PydanticBaseModel
from sqlmodel import Field

from protobuf.connections import category_service_models
from src.models.base import BaseModel


@strawberry.type
class _ModelAttr(PydanticBaseModel):
    example: str


@strawberry.input
class ModelBase(BaseModel[category_service_models.ModelBase], _ModelAttr):
    __grpc_model__ = category_service_models.ModelBase


@strawberry.type
class Model(BaseModel[category_service_models.Model], _ModelAttr, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    __grpc_model__ = category_service_models.Model
