from typing import Callable, Awaitable, Type, TypeVar

import strawberry
from google.protobuf.message import Message
from grpc.aio import AioRpcError  # type: ignore

from src.config.session import get_neo4j_session
from src.crud.model import crud_model
from src.models.model import Category, CategoryBase

from protobuf.connections import (
    category_service_stub,
    category_service_models,
)
from src.models.base import BaseModel


async def make_grpc_call[T: BaseModel](  # type: ignore
    stub_method: Callable[[Message], Awaitable[Message]],
    response_model_cls: Type[T],
    *request_message: Message,
) -> T:
    """
    Make a gRPC call and return the response.

    :param stub_method: The gRPC method to call (e.g., ``GetModel``).
    :param response_model_cls: The response SQLModel class (e.g., ``Model``).
    :param request_message: The request message to send (e.g., ``category_service_models.ModelId(id=id)``).
    :return: The response SQLModel instance.
    """
    try:
        response = await stub_method(*request_message)
        return response_model_cls.from_grpc(response)
    except AioRpcError as e:
        raise Exception(e.details())


@strawberry.type
class Query:
    @strawberry.field
    # async def get_category(self, id: int) -> Category:
    #     return await make_grpc_call(
    #         category_service_stub.GetCategory,
    #         Category,
    #         category_service_models.CategoryId(id=id),
    #     )
    async def get_category(self, id: int) -> Category:
        cat = await crud_model.get(str(id))
        print(cat)
        return cat


    @strawberry.field
    async def find_by_name(self, name: str) -> list[Category]:
        filters = {"name": name}

        return await crud_model.find(filters)



@strawberry.type
class Mutation:
    @strawberry.mutation
    async def create_category(self, model: CategoryBase) -> Category:
        return await make_grpc_call(
            category_service_stub.CreateModel,
            Category,
            model.to_grpc(),
        )
