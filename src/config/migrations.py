import os
import re
from datetime import datetime

from neo4j import Record, AsyncSession, AsyncManagedTransaction


class MigrationRunner:
    def __init__(self, session: AsyncSession, *, migration_dir: str = "migrations"):
        self.session = session
        self.migration_dir = migration_dir
        self._ensure_migrations_directory()

    def _ensure_migrations_directory(self) -> None:
        os.makedirs(self.migration_dir, exist_ok=True)

    async def initialize(self) -> None:
        await self._initialize_migration_graph()

    async def _initialize_migration_graph(self) -> None:
        await self.session.execute_write(self._create_constraint)
        await self.session.execute_write(self._create_initial_schema)

    @staticmethod
    async def _create_constraint(tx: AsyncManagedTransaction) -> None:
        await tx.run(
            """
            CREATE CONSTRAINT unique_migration_version IF NOT EXISTS 
            FOR (m:Migration) 
            REQUIRE m.version IS UNIQUE
        """
        )

    @staticmethod
    async def _create_initial_schema(tx: AsyncManagedTransaction) -> None:
        # Add any initial schema setup here
        pass

    def create_migration(self, name: str) -> None:
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"{timestamp}_{name}.cypher"
        path = os.path.join(self.migration_dir, filename)

        content = """# --- !Ups
# Add your UP migration Cypher here


# --- !Downs
# Add your DOWN migration Cypher here
"""
        with open(path, "w") as f:
            f.write(content)
        print(f"Created migration: {filename}")

    async def get_applied_migrations(self) -> list[str]:
        result = await self.session.execute_read(self._get_applied_versions)
        return [record["version"] for record in result]

    @staticmethod
    async def _get_applied_versions(tx: AsyncManagedTransaction) -> list[Record]:
        result = await tx.run(
            "MATCH (m:Migration) RETURN m.version as version ORDER BY version"
        )
        return [record async for record in result]

    def get_available_migrations(self) -> list[str]:
        files = os.listdir(self.migration_dir)
        migrations = []
        for f in sorted(files):
            if f.endswith(".cypher") and re.match(r"^\d+_.+\.cypher$", f):
                migrations.append(f)
        return migrations

    async def upgrade(self, target: str | None = None) -> None:
        applied = set(await self.get_applied_migrations())
        available = self.get_available_migrations()

        to_apply = [m for m in available if m not in applied]
        if target:
            try:
                target_index = available.index(target)
                to_apply = available[: target_index + 1]
            except ValueError:
                raise ValueError(f"Target migration {target} not found")

        for migration in to_apply:
            await self._apply_migration(migration)

    async def _apply_migration(self, filename: str) -> None:
        path = os.path.join(self.migration_dir, filename)
        with open(path, "r") as f:
            content = f.read()

        up_part = re.search(r"# --- !Ups(.+?)# --- !Downs", content, re.DOTALL)
        down_part = re.search(r"# --- !Downs(.+)$", content, re.DOTALL)

        if not up_part or not down_part:
            raise ValueError(f"Invalid migration file format in {filename}")

        up_cypher = up_part.group(1).strip()

        try:
            # Execute upgrade
            await self.session.execute_write(lambda tx: tx.run(up_cypher))
            # Record migration
            await self.session.execute_write(
                lambda tx: tx.run(
                    "CREATE (m:Migration {version: $version, applied_at: datetime()})",
                    version=filename,
                )
            )
            print(f"Applied migration: {filename}")
        except Exception as e:
            print(f"Failed to apply migration {filename}: {str(e)}")
            raise

    async def downgrade(self, target: str) -> None:
        applied = await self.get_applied_migrations()
        if target not in applied:
            raise ValueError(
                f"Target migration {target} not found in applied migrations"
            )

        target_index = applied.index(target)
        to_revert = reversed(applied[target_index + 1 :])

        for migration in to_revert:
            await self._revert_migration(migration)

    async def _revert_migration(self, filename: str) -> None:
        path = os.path.join(self.migration_dir, filename)
        with open(path, "r") as f:
            content = f.read()

        down_part = re.search(r"# --- !Downs(.+)$", content, re.DOTALL)
        if not down_part:
            raise ValueError(f"No Down section found in {filename}")

        down_cypher = down_part.group(1).strip()

        try:
            # Execute downgrade
            await self.session.execute_write(lambda tx: tx.run(down_cypher))
            # Remove migration record
            await self.session.execute_write(
                lambda tx: tx.run(
                    "MATCH (m:Migration {version: $version}) DELETE m",
                    version=filename,
                )
            )
            print(f"Reverted migration: {filename}")
        except Exception as e:
            print(f"Failed to revert migration {filename}: {str(e)}")
            raise
