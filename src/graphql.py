import strawberry
from graphql import GraphQLError

from src.crud import crud_category, CrudCategory
from src.model import Category, CategoryInput

crud = CrudCategory()


@strawberry.type
class Query:
    @strawberry.field()
    async def category(self, name: str) -> Category | None:
        obj = await crud_category.get(name)
        if obj is None:
            return None
        return Category(**obj.model_dump())

    @strawberry.field()
    async def categories(self, name: str, depth: int = -1) -> list[Category]:
        objects = await crud_category.find(name, depth)
        return [Category(**obj.model_dump()) for obj in objects]


@strawberry.type
class Mutation:
    @strawberry.mutation()
    async def create_category(self, model: CategoryInput) -> Category:
        obj = await crud.create(model.to_pydantic())
        if obj is None:
            raise GraphQLError(
                "CategoryModel already exists", extensions={"code": "NOT_FOUND"}
            )
        return Category(**obj.model_dump())

    @strawberry.mutation()
    async def update_category(self, name: str, model: CategoryInput) -> Category:
        obj = await crud.update(name, model.to_pydantic())
        if obj is None:
            raise GraphQLError(
                "CategoryModel not found", extensions={"code": "NOT_FOUND"}
            )
        return Category(**obj.model_dump())

    @strawberry.mutation()
    async def delete_category(self, name: str) -> bool:
        return await crud.delete(name)
