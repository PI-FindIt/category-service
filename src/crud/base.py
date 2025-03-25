from contextlib import asynccontextmanager
from typing import Type, Generic, TypeVar, Optional, Any, AsyncGenerator
from pydantic import BaseModel
from neo4j import AsyncSession, AsyncResult

from src.config.session import get_neo4j_session

ModelType = TypeVar("ModelType", bound=BaseModel)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)


@asynccontextmanager
async def _get_session_context(
    session: AsyncSession | None = None,
) -> AsyncGenerator[AsyncSession, None]:
    if session is None:
        async with get_neo4j_session() as new_session:
            yield new_session
    else:
        yield session


class CRUDBaseNeo4j(Generic[ModelType, CreateSchemaType]):
    def __init__(self, model: Type[ModelType], label: str | None = None):
        self.model = model
        self.label = label or model.__name__

    @staticmethod
    @asynccontextmanager
    async def _get_session_context(
        session: AsyncSession | None = None,
    ) -> AsyncGenerator[AsyncSession, None]:
        if session is None:
            async with get_neo4j_session() as new_session:
                yield new_session
        else:
            yield session

    @staticmethod
    async def _execute_query(
        query: str, parameters: dict[str, Any], session: AsyncSession
    ) -> AsyncResult:
        return await session.run(query, parameters)

    async def create(
        self, obj: CreateSchemaType, session: AsyncSession | None = None
    ) -> ModelType | None:
        properties = obj.model_dump()
        query = f"CREATE (n:{self.label} $props) " "RETURN n"
        async with self._get_session_context(session) as session_ctx:
            result = await self._execute_query(
                query, {"props": properties}, session_ctx
            )
            data = await result.single()

        return self.model(**data["n"]) if data else None

    async def get(
        self, id: str, session: AsyncSession | None = None
    ) -> Optional[ModelType]:
        query = f"MATCH (n:{self.label} {{id: $id}}) " "RETURN n"
        async with self._get_session_context(session) as session_ctx:
            result = await self._execute_query(query, {"id": id}, session_ctx)
            data = await result.single()

        return self.model(**data["n"]) if data else None

    async def get_all(self, session: AsyncSession | None = None) -> list[ModelType]:
        query = f"MATCH (n:{self.label}) RETURN n"
        async with self._get_session_context(session) as session_ctx:
            result = await self._execute_query(query, {}, session_ctx)
            return [self.model(**record["n"]) async for record in result]

    async def update(
        self, id: str, obj: CreateSchemaType, session: AsyncSession | None = None
    ) -> Optional[ModelType]:
        properties = obj.model_dump(exclude_unset=True)
        query = f"MATCH (n:{self.label} {{id: $id}}) " "SET n += $props " "RETURN n"
        async with self._get_session_context(session) as session_ctx:
            result = await self._execute_query(
                query, {"id": id, "props": properties}, session_ctx
            )
            data = await result.single()
            return self.model(**data["n"]) if data else None

    async def delete(self, id: str, session: AsyncSession | None = None) -> bool:
        query = f"MATCH (n:{self.label} {{id: $id}}) " "DELETE n"
        async with self._get_session_context(session) as session_ctx:
            await self._execute_query(query, {"id": id}, session_ctx)
            return True  # TODO Assume success unless exception is raised

    async def find(
        self,
        filters: BaseModel | None = None,
        session: AsyncSession | None = None,
        limit: int = 100,
    ) -> list[ModelType]:
        where_clause = " AND ".join([f"n.{key} = ${key}" for key in filters.keys()])
        query = (
            f"MATCH (n:{self.label}) "
            f"WHERE {where_clause} "
            f"RETURN n LIMIT {limit}"
        )
        async with self._get_session_context(session) as session_ctx:
            result = await self._execute_query(query, filters, session_ctx)
            return [self.model(**record["n"]) async for record in result]
