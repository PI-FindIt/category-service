from contextlib import asynccontextmanager
from typing import AsyncGenerator

from neo4j import (
    AsyncGraphDatabase,
    AsyncSession as Neo4jAsyncSession,
)

from src.config.settings import settings


class Neo4jSession:
    def __init__(self) -> None:
        self.driver = AsyncGraphDatabase.driver(
            settings.NEO4J_URL,
            auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD),
            database=settings.NEO4J_DB,
        )

    @asynccontextmanager
    async def get_session(self) -> AsyncGenerator[Neo4jAsyncSession, None]:
        async with self.driver.session() as session:
            yield session

    async def close(self) -> None:
        await self.driver.close()


neo4j_session = Neo4jSession()


@asynccontextmanager
async def get_neo4j_session() -> AsyncGenerator[Neo4jAsyncSession, None]:
    async with neo4j_session.get_session() as session:
        yield session


async def init_neo4j_db() -> None:
    async with get_neo4j_session() as session:
        # Like alembic for neo4j mas mais à pata hihihi
        await session.execute_write(
            lambda tx: tx.run(
                "CREATE CONSTRAINT unique_category_id IF NOT EXISTS "
                "FOR (c:Category) REQUIRE c.id IS UNIQUE"
            )
        )

        await session.execute_write(
            lambda tx: tx.run(
                """
                LOAD CSV WITH HEADERS FROM 'file:///categories.csv' AS row
                MERGE (c:Category {name: row.name })
                SET c.name = row.name;
                """
            )
        )

        await session.execute_write(
            lambda tx: tx.run(
                """
                LOAD CSV WITH HEADERS FROM 'file:///categories.csv' AS row
                MATCH (child:Category {name: row.name})
                WHERE row.parent_name IS NOT NULL
                MATCH (parent:Category {name: row.parent_name})
                MERGE (child)-[:SUBCATEGORY_OF]->(parent);
                """
            )
        )
