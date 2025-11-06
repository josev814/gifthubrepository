import asyncio
import os
import pytest
from testcontainers.postgres import PostgresContainer
from testcontainers.rabbitmq import RabbitMqContainer
from testcontainers.redis import RedisContainer
from httpx import AsyncClient
from app.main import app
from app.database import create_engine, SQLModel, get_session

@pytest.fixture(scope="module")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="module")
def containers():
    with PostgresContainer("postgres:15") as pg, RabbitMqContainer("rabbitmq:3.11-management") as mq, RedisContainer("redis:7") as rd:
        os.environ["DATABASE_URL"] = pg.get_connection_url().replace("postgresql", "postgresql")
        os.environ["RABBITMQ_URL"] = mq.get_connection_url()
        os.environ["REDIS_URL"] = f"redis://{rd.get_container_host_ip()}:{rd.get_exposed_port(6379)}/0"
        yield

@pytest.mark.asyncio
async def test_reservation_flow(containers):
    # init db
    from app.database import engine
    SQLModel.metadata.create_all(engine)

    async with AsyncClient(app=app, base_url="http://test") as ac:
        # register user
        r = await ac.post("/api/register", json={"email":"u@test","password":"pass"})
        assert r.status_code == 200
        token = r.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        # create registry
        r = await ac.post("/api/registries/", json={"name":"r1"}, headers=headers)
        assert r.status_code == 200
        reg_id = r.json()["id"]
        # add gift
        r = await ac.post(f"/api/registries/{reg_id}/items", json={"title":"g1","description":"x"}, headers=headers)
        assert r.status_code == 200
        gift = r.json()
        # reserve
        r = await ac.post(f"/api/reservations/{gift['id']}", json={"duration_minutes":15}, headers=headers)
        assert r.status_code == 200
        # confirm
        r = await ac.post(f"/api/reservations/{gift['id']}/confirm", headers=headers)
        assert r.status_code == 200
