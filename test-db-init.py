import pytest
from pytest_mongodb.plugin import mongomock
from pytest_mongodb.plugin import pymongo
from db_init import zz8_db


config = {
    "db_user": "test",
    "db_pass": "test",
    "db_host": "127.0.0.1",
    "db_port": 27017,
}


class Testdb:
    @pytest.fixture
    def db(self):
        db = zz8_db(config)
        return db

    def test_one(self, db):
        assert db.user == config["db_user"]
        assert db.password == config["db_pass"]
        assert db.host == config["db_host"]
        assert db.port == config["db_port"]

    def test_two(self, db):
        db.connection()
        assert isinstance(db.client, pymongo.mongo_client.MongoClient)

    def test_three(self, db):
        db.connection()
        db.db_init()
        assert isinstance(db.db, pymongo.database.Database)

    def test_something(self, mongodb):
        assert "users" in mongodb.list_collection_names()

    def test_four(self, db, mongodb):
        # we need to test retrieval, not pymongo
        db.db = mongodb
        player1 = db.get_user_interests(124434)
        player2 = db.get_user_interests(12345)
        player3 = db.get_user_interests(98765)
        # Assert the types first
        assert isinstance(player1, list)
        assert isinstance(player2, list)
        assert isinstance(player3, list)

        # Assert the content next
        assert player1 == ["tech", "punk"]
        assert player2 == ["red"]
        assert player3 == []

    def test_five(self, db, mongodb):
        # Sets up our mongodb mock
        db.db = mongodb

        # Sets up the test parameters
        test1_ints = ["space", "pokemon"]
        test1_uuid = 99999
        test2_ints = ["makeup", "massages", "nail polish"]
        test2_uuid = 754323
        test1 = db.store_user_interests(test1_uuid, test1_ints)
        test2 = db.store_user_interests(test2_uuid, test2_ints)

        assert test1 == True
        assert test2 == True
        find1 = {"uuid": test1_uuid}
        assert mongodb.users.find_one(find1)
        interests = mongodb.users.find_one(find1)["interests"]
        assert interests == test1_ints

        find2 = {"uuid": test2_uuid}
        assert mongodb.users.find_one(find2)
        interests = mongodb.users.find_one(find2)["interests"]
        assert interests == test2_ints

    def test_six(self, db, mongodb):
        # Sets up our mongodb mock
        db.db = mongodb

        # Sets up the test parameters
        test1_ints = ["red", "blue"]
        test1_uuid = 124434
        test2_ints = [1234, "purple"]
        test2_uuid = 12345

        test1 = db.update_user_interests(test1_uuid, test1_ints)
        test2 = db.update_user_interests(test2_uuid, test2_ints)

        # Test it
        assert test1 == True
        assert test2 == True
        find1 = {"uuid": test1_uuid}
        assert mongodb.users.find_one(find1)
        interests = mongodb.users.find_one(find1)["interests"]
        assert interests == test1_ints

        find2 = {"uuid": test2_uuid}
        assert mongodb.users.find_one(find2)
        interests = mongodb.users.find_one(find2)["interests"]
        assert interests == test2_ints
