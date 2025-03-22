from typing import Type, Generic, TypeVar, Optional, Any
from pydantic import BaseModel
from neo4j import AsyncSession, AsyncResult

ModelType = TypeVar("ModelType", bound=BaseModel)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDBaseNeo4j(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType], label: str | None = None):
        self.model = model
        self.label = label or model.__name__

    @staticmethod
    async def _execute_query(
            query: str, parameters: dict[str, Any], session: AsyncSession
    ) -> AsyncResult:
        return await session.run(query, parameters)

    async def create(self, obj: CreateSchemaType, session: AsyncSession) -> ModelType | None:
        properties = obj.model_dump()
        query = (
            f"CREATE (n:{self.label} $props) "
            "RETURN n"
        )
        result = await self._execute_query(query, {"props": properties}, session)
        data = await result.single()

        return self.model(**data["n"]) if data else None

    async def get(self, id: str, session: AsyncSession) -> Optional[ModelType]:
        query = (
            f"MATCH (n:{self.label} {{id: $id}}) "
            "RETURN n"
        )
        result = await self._execute_query(query, {"id": id}, session)
        data = await result.single()
        return self.model(**data["n"]) if data else None

    async def get_all(self, session: AsyncSession) -> list[ModelType]:
        query = f"MATCH (n:{self.label}) RETURN n"
        result = await self._execute_query(query, {}, session)
        return [self.model(**record["n"]) async for record in result]

    async def update(
            self, id: str, obj: UpdateSchemaType, session: AsyncSession
    ) -> Optional[ModelType]:
        properties = obj.model_dump(exclude_unset=True)
        query = (
            f"MATCH (n:{self.label} {{id: $id}}) "
            "SET n += $props "
            "RETURN n"
        )
        result = await self._execute_query(query, {"id": id, "props": properties}, session)
        data = await result.single()
        return self.model(**data["n"]) if data else None

    async def delete(self, id: str, session: AsyncSession) -> bool:
        query = (
            f"MATCH (n:{self.label} {{id: $id}}) "
            "DELETE n"
        )
        await self._execute_query(query, {"id": id}, session)
        return True  # Assume success unless exception is raised

    async def find(
            self,
            filters: dict[str, Any],
            session: AsyncSession,
            limit: int = 100
    ) -> list[ModelType]:
        where_clause = " AND ".join([f"n.{key} = ${key}" for key in filters.keys()])
        query = (
            f"MATCH (n:{self.label}) "
            f"WHERE {where_clause} "
            f"RETURN n LIMIT {limit}"
        )
        result = await self._execute_query(query, filters, session)
        return [self.model(**record["n"]) async for record in result]
