from typing import Callable, Awaitable, Type, TypeVar

import strawberry
from google.protobuf.message import Message
from grpc.aio import AioRpcError  # type: ignore
from src.models.model import Model, ModelBase

from protobuf.connections import (
    service_name_stub,
    service_name_models,
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
    :param request_message: The request message to send (e.g., ``service_name_models.ModelId(id=id)``).
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
    async def get_model(self, id: int) -> Model:
        return await make_grpc_call(
            service_name_stub.GetModel,
            Model,
            service_name_models.ModelId(id=id),
        )


@strawberry.type
class Mutation:
    @strawberry.mutation
    async def create_model(self, model: ModelBase) -> Model:
        return await make_grpc_call(
            service_name_stub.CreateModel,
            Model,
            model.to_grpc(),
        )
