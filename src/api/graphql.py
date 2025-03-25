from typing import Any

import strawberry

from src.crud.model import crud_category, CrudCategory
from src.models.model import Category, CategoryFilterModel, CategoryBase

crud = CrudCategory()


@strawberry.type
class Query:
    @strawberry.field
    async def category(self, name: str) -> Category | None:
        return await crud_category.get(name)

    @strawberry.field
    async def categories(
        self, filter: CategoryFilterModel | None = None
    ) -> list[Category]:
        return await crud_category.find(filter)


@strawberry.type
class Mutation:
    @strawberry.mutation
    async def create_category(self, model: CategoryBase) -> Category:
        obj = await crud.create(model)
        if obj is None:
            raise Exception("Not found")
        return obj

    @strawberry.mutation
    async def update_category(self, id: str, model: CategoryBase) -> Category:
        obj = await crud.update(id, model)
        if obj is None:
            raise Exception("Not found")
        return obj

    @strawberry.mutation
    async def delete_category(self, id: str) -> bool:
        return await crud.delete(id)
