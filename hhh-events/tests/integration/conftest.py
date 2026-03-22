from collections.abc import AsyncGenerator, Generator

import pytest
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection
from testcontainers.mongodb import MongoDbContainer

_RS_NAME = "rs0"


@pytest.fixture(scope="module")
def mongo_container() -> Generator[MongoDbContainer, None, None]:
    container = MongoDbContainer("mongo:7")
    container.with_command(f"mongod --replSet {_RS_NAME} --bind_ip_all")
    with container:
        # Initialize single-node replica set
        from pymongo import MongoClient

        client = MongoClient(container.get_connection_url(), directConnection=True)
        client.admin.command(
            "replSetInitiate",
            {
                "_id": _RS_NAME,
                "members": [{"_id": 0, "host": f"localhost:{container.get_exposed_port(27017)}"}],
            },
        )
        # Wait for primary election
        import time

        for _ in range(30):
            status = client.admin.command("replSetGetStatus")
            if any(m["stateStr"] == "PRIMARY" for m in status["members"]):
                break
            time.sleep(0.5)
        client.close()
        yield container


@pytest.fixture(scope="module")
def mongo_uri(mongo_container: MongoDbContainer) -> str:
    port = mongo_container.get_exposed_port(27017)
    return f"mongodb://localhost:{port}/?replicaSet={_RS_NAME}&directConnection=true"


@pytest.fixture
async def events_collection(mongo_uri: str) -> AsyncGenerator[AsyncIOMotorCollection, None]:
    client = AsyncIOMotorClient(mongo_uri)
    db = client["test_hhh_events"]
    collection = db["events"]
    yield collection
    await collection.drop()
    client.close()


@pytest.fixture
async def token_collection(mongo_uri: str) -> AsyncGenerator[AsyncIOMotorCollection, None]:
    client = AsyncIOMotorClient(mongo_uri)
    db = client["test_subscriber_db"]
    collection = db["resume_tokens"]
    yield collection
    await collection.drop()
    client.close()
