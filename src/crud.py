from contextlib import asynccontextmanager
from typing import (
    Optional,
    Any,
    AsyncGenerator,
    LiteralString,
    Literal,
)

from neo4j import AsyncSession, AsyncResult

from src.config.session import get_neo4j_session
from src.model import CategoryModel


class CrudCategory:
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
        self, obj: CategoryModel, session: AsyncSession | None = None
    ) -> CategoryModel | None:
        properties = obj.model_dump()
        query: LiteralString = "CREATE (n:Category $props) RETURN n"
        async with self._get_session_context(session) as session_ctx:
            result = await self._execute_query(
                query, {"props": properties}, session_ctx
            )
            data = await result.single()

        return CategoryModel(**data["n"]) if data else None

    async def get(
        self, name: str, session: AsyncSession | None = None
    ) -> Optional[CategoryModel]:
        query: LiteralString = "MATCH (n:Category {name: $name}) RETURN n"
        async with self._get_session_context(session) as session_ctx:
            result = await self._execute_query(query, {"name": name}, session_ctx)
            data = await result.single()
        return CategoryModel(**data["n"]) if data else None

    async def get_all(self, session: AsyncSession | None = None) -> list[CategoryModel]:
        query: LiteralString = "MATCH (n:Category) RETURN n"
        async with self._get_session_context(session) as session_ctx:
            result = await self._execute_query(query, None, session_ctx)
            return [CategoryModel(**record["n"]) async for record in result]

    async def update(
        self, name: str, obj: CategoryModel, session: AsyncSession | None = None
    ) -> Optional[CategoryModel]:
        properties = obj.model_dump(exclude_unset=True)
        query: LiteralString = (
            "MATCH (n:Category {name: $name}) SET n += $props RETURN n"
        )
        async with self._get_session_context(session) as session_ctx:
            result = await self._execute_query(
                query, {"name": name, "props": properties}, session_ctx
            )
            data = await result.single()
            return CategoryModel(**data["n"]) if data else None

    async def delete(self, name: str, session: AsyncSession | None = None) -> bool:
        query: LiteralString = "MATCH (n:Category {name: $name}) DETACH DELETE n"
        async with self._get_session_context(session) as session_ctx:
            await self._execute_query(query, {"name": name}, session_ctx)
            return True

    async def find(
        self,
        name: str,
        session: AsyncSession | None = None,
    ) -> list[CategoryModel]:
        query: LiteralString = (
            "MATCH (n:Category) WHERE n.name CONTAINS $name RETURN n LIMIT 100"
        )
        async with self._get_session_context(session) as session_ctx:
            result = await self._execute_query(query, {"name": name}, session_ctx)
            return [CategoryModel(**record["n"]) async for record in result]

    async def get_hierarchy(
        self,
        hierarchy: Literal["children", "parents"],
        name: str,
        session: AsyncSession | None = None,
    ) -> list[CategoryModel]:
        a: LiteralString = "m" if hierarchy == "children" else "n"
        b: LiteralString = "n" if hierarchy == "children" else "m"

        query: LiteralString = (
            f"MATCH (n:Category)-[r:SUBCATEGORY_OF]-> (m:Category) WHERE {a}.name = $name RETURN {b}"
        )
        async with self._get_session_context(session) as session_ctx:
            result = await self._execute_query(query, {"name": name}, session_ctx)
            return [CategoryModel(**record[b]) async for record in result]


crud_category = CrudCategory()
