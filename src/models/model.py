from typing import Optional

import strawberry
from pydantic import BaseModel


@strawberry.input
class CategoryBase(BaseModel):
    name: str

    @property
    def friendly_name(self) -> str:
        return (
            self.name.replace("-", " ")
            .replace("en:", "")
            .replace("pt:", "")
            .capitalize()
        )


@strawberry.type
class Category(CategoryBase):
    pass


@strawberry.input
class CategoryFilterModel(CategoryBase):
    _optional_fields = {
        field: Optional[field_type]
        for field, field_type in CategoryBase.__annotations__.items()
    }
    __annotations__ = _optional_fields
