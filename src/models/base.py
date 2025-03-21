from typing import Type, Self

from google.protobuf.json_format import MessageToDict
from google.protobuf.message import Message
from sqlmodel import SQLModel


class BaseModel[T: Message](SQLModel):
    """A superclass that acts as SQLModel, Strawberry GraphQL type and converts to gRPC Messages."""

    __grpc_model__: Type[T]

    def to_grpc(self) -> T:
        """Convert SQLModel instance to gRPC message."""
        return self.__grpc_model__(**self.model_dump())

    # def to_grpc(self) -> T:
    #     """Convert SQLModel instance to gRPC message, ensuring no None values."""
    #     data = {k: v if v is not None else "" for k, v in self.model_dump().items() if
    #             k in self.__grpc_model__.__annotations__}
    #     return self.__grpc_model__(**data)

    @classmethod
    def from_grpc(cls, grpc_message: Message) -> Self:
        """Convert gRPC message to SQLModel instance."""
        if grpc_message is None:
            return None
        return cls(**MessageToDict(grpc_message, preserving_proto_field_name=True))
