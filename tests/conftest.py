from collections.abc import AsyncGenerator

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from src.core.config import settings
from src.core.models.db_helper import db_helper
from src.core.models.model_base import Base
from src.main import main_app
from tests.insert_data_in_tables import insert_data

test_db_url = "postgresql+asyncpg://test:twitter_password@{:s}:5432/test".format(
    settings.db.db_host
)

# Создание тестовых движка и сессии
test_engine = create_async_engine(test_db_url, poolclass=NullPool, echo=False)
test_async_session = async_sessionmaker(
    bind=test_engine, expire_on_commit=False
)


async def override_get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with test_async_session() as session:
        yield session


main_app.dependency_overrides[db_helper.session_getter] = (
    override_get_async_session
)


@pytest_asyncio.fixture(autouse=True, scope="session")
async def prepare_database():
    """
    Очищаем базу данных от таблиц (на всякий случай).
    Создаём таблицы в базе данных из моделей.
    Наполняем таблицы данными
    После завершения тестирования, очищаем базу данных.
    """
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
        await insert_data(conn)
        await conn.commit()
    yield
    # async with test_engine.begin() as conn:
    #     await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(scope="session")
async def ac() -> AsyncGenerator[AsyncClient, None]:
    """
    Создаём асинхронный HTTP-клиент для выполнения тестов.
    """
    async with AsyncClient(
        transport=ASGITransport(app=main_app),
        base_url="http://test",
    ) as async_test_client:
        yield async_test_client
