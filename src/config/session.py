from contextlib import asynccontextmanager
from typing import AsyncGenerator

from neo4j import (
    AsyncGraphDatabase,
    AsyncSession as Neo4jAsyncSession,
)

from src.config.migrations import MigrationRunner
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
        runner = MigrationRunner(session)
        await runner.initialize()
        await runner.upgrade()
        # runner.create_migration("add_constraint")
        # runner.downgrade("20231020123456_add_constraint.cypher")
