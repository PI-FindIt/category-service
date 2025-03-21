import uuid
from typing import Type

from sqlmodel import select, SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

from src.config.session import get_postgres_session


class CRUDBase[
    ModelType: SQLModel,
    CreateSchemaType: SQLModel,
    PrimaryKeyType: (int, str, uuid.UUID, tuple[str, str]),
]:
    def __init__(
        self,
        model: Type[ModelType],
    ):
        """
        Default methods to Create, Read, Update & Delete (CRUD).

        :param model: The SQLModel model to use.
        :type model: SQLModel
        """
        self.model = model

    async def _add_to_db(
        self, obj: ModelType, session: AsyncSession | None = None
    ) -> ModelType:
        if session is not None:
            session.add(obj)
            await session.commit()
            await session.refresh(obj)
            return obj

        async with get_postgres_session() as session:
            session.add(obj)
            await session.commit()
            await session.refresh(obj)
            return obj

    async def create(self, obj: CreateSchemaType) -> ModelType:
        db_obj = self.model.model_validate(obj)
        return await self._add_to_db(db_obj)

    async def get(
        self, id: PrimaryKeyType, session: AsyncSession | None = None
    ) -> ModelType | None:
        if session is not None:
            return await session.get(self.model, id)
        async with get_postgres_session() as session:
            return await session.get(self.model, id)

    async def get_all(self) -> list[ModelType]:
        async with get_postgres_session() as session:
            result = await session.exec(select(self.model))
            return list(result.all())

    async def update(
        self, id: PrimaryKeyType, obj: CreateSchemaType
    ) -> ModelType | None:
        db_obj = await self.get(id)
        if db_obj is None:
            return None

        db_obj.sqlmodel_update(obj)

        return await self._add_to_db(db_obj)

    async def delete(self, id: PrimaryKeyType) -> bool:
        obj = await self.get(id)
        if obj is None:
            return False

        async with get_postgres_session() as session:
            await session.delete(obj)
            await session.commit()
            return True
