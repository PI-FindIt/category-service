from contextlib import asynccontextmanager
from typing import (
    Type,
    Optional,
    Any,
    AsyncGenerator,
    LiteralString,
    cast,
)
from neo4j import AsyncSession, AsyncResult

from src.config.session import get_neo4j_session

from src.models.model import Category, CategoryBase, CategoryFilterModel


class CrudCategory:
    def __init__(self) -> None:
        self.model = Category
        self.label: LiteralString = "Category"

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

    async def _execute_query(
        self,
        query: LiteralString,
        parameters: dict[str, Any] | None,
        session: AsyncSession,
    ) -> AsyncResult:
        return await session.run(query, parameters)

    async def create(
        self, obj: CategoryBase, session: AsyncSession | None = None
    ) -> Category | None:
        properties = obj.model_dump()
        query: LiteralString = f"CREATE (n:{self.label} $props) RETURN n"
        async with self._get_session_context(session) as session_ctx:
            result = await self._execute_query(
                query, {"props": properties}, session_ctx
            )
            data = await result.single()

        return self.model(**data["n"]) if data else None

    async def get(
        self, name: str, session: AsyncSession | None = None
    ) -> Optional[Category]:
        query: LiteralString = f"MATCH (n:{self.label} {{name: $name}}) RETURN n"
        async with self._get_session_context(session) as session_ctx:
            result = await self._execute_query(query, {"name": name}, session_ctx)
            data = await result.single()

        return self.model(**data["n"]) if data else None

    async def get_all(self, session: AsyncSession | None = None) -> list[Category]:
        query: LiteralString = f"MATCH (n:{self.label}) RETURN n"
        async with self._get_session_context(session) as session_ctx:
            result = await self._execute_query(query, None, session_ctx)
            return [self.model(**record["n"]) async for record in result]

    async def update(
        self, id: str, obj: CategoryBase, session: AsyncSession | None = None
    ) -> Optional[Category]:
        properties = obj.model_dump(exclude_unset=True)
        query: LiteralString = (
            f"MATCH (n:{self.label} {{id: $id}}) SET n += $props RETURN n"
        )
        async with self._get_session_context(session) as session_ctx:
            result = await self._execute_query(
                query, {"id": id, "props": properties}, session_ctx
            )
            data = await result.single()
            return self.model(**data["n"]) if data else None

    async def delete(self, id: str, session: AsyncSession | None = None) -> bool:
        query: LiteralString = f"MATCH (n:{self.label} {{name: $id}}) DETACH DELETE n"
        async with self._get_session_context(session) as session_ctx:
            data = await self._execute_query(query, {"id": id}, session_ctx)
            return True

    async def find(
        self,
        filters: CategoryFilterModel | None = None,
        session: AsyncSession | None = None,
        limit: int = 100,
    ) -> list[Category]:
        where_clause: LiteralString = cast(  # type: ignore
            LiteralString,
            " AND ".join(
                [
                    f"n.{key} = ${key}"
                    for key in (filters.model_dump() if filters else {})
                ]
            ),
        )
        if where_clause:
            where_clause = f"WHERE {where_clause}"
        query: LiteralString = (
            f"MATCH (n:{self.label}) {where_clause} RETURN n LIMIT 100"
        )
        async with self._get_session_context(session) as session_ctx:
            result = await self._execute_query(
                query, filters.model_dump() if filters else None, session_ctx
            )
            return [self.model(**record["n"]) async for record in result]


crud_category = CrudCategory()
