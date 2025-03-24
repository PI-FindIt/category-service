from typing import Optional

import strawberry
from pydantic import BaseModel as PydanticBaseModel
from sqlmodel import Field

from protobuf.connections import category_service_models
from src.models.base import BaseModel


@strawberry.type
class _CategoryAttr(PydanticBaseModel):
    name: str
    parent_id: int | None
    # see me parent must appear here


#TODO see here because of tye type of basemodel
@strawberry.input
class CategoryBase(BaseModel[category_service_models.Category], _CategoryAttr):
    __grpc_model__ = category_service_models.Category

    
@strawberry.type
class Category(BaseModel[category_service_models.Category], _CategoryAttr):
    id: int
    __grpc_model__ = category_service_models.Category
