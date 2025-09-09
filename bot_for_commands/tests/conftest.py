import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

from bot_for_commands.database.models import Base
from bot_for_commands.database.common import create_tables, clear_tables
from bot_for_commands.config_reader import config
from bot_for_commands.cache import Cache
from bot_for_commands.tests.inputs import inst_list


@pytest.fixture()
async def test_session():
    test_engine = create_async_engine(config.test_db_address.get_secret_value())
    session = AsyncSession(test_engine, expire_on_commit=False)

    yield session
    await clear_tables(session)


@pytest.fixture(scope='session', autouse=True)
async def create_and_delete_tables():
    test_engine = create_async_engine(config.test_db_address.get_secret_value())
    session = AsyncSession(test_engine, expire_on_commit=False)

    await create_tables(test_engine)
    yield session
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture()
def test_cache():
    cache = Cache()
    yield cache
    cache._cache = {}

