import logging

from pymongo import MongoClient

logger = logging.getLogger("zz-8")
logger.setLevel(logging.INFO)
c_handler = logging.StreamHandler()
f_handler = logging.FileHandler("zz-8.log")
c_handler.setLevel(logging.INFO)
f_handler.setLevel(logging.INFO)

formatter = logging.Formatter("%(asctime)s %(levelname)8s %(message)s")

c_handler.setFormatter(formatter)
f_handler.setFormatter(formatter)

logger.addHandler(c_handler)
logger.addHandler(f_handler)


class zz8_db(object):
    """
    This class connects to the mongo database.
    If the database doesn't exist, pymongo
    will create it.
    """

    def __init__(self, config):
        """
        The constructor for zz8_db_init class.

        Config should be a dict{} containing the
        below variables

        Parameters:
            user (str): The username for proper db conns
            pass (str): The password for proper db conns
            host (str): The hostname for proper db conns
            port (int): The port for proper db conns
            db   (str): The port for proper db conns
        """
        self.user = config["user"]
        self.password = config["pass"]
        self.host = config["host"]
        self.port = config["port"]
        self.logger = logging.getLogger("zz-8")

    def connection(self):
        """
        Creates the mongo client

        Returns True
        """
        connect_string = (
            f"mongodb://{self.user}:{self.password}",
            f"@{self.host}:{self.port}/zz8",
        )

        self.client = MongoClient(connect_string)
        self.logger.INFO("Connected to mongo")
        return True

    def db_init(self):
        """
        Sets up the database and creates
        it, if it doesn't already exist

        Returns True
        """
        self.db = self.client["zz8"]
        self.logger.INFO("Connected to zz8 db")
        return True

    def get_user_interests(self, user_id):
        """
        Queries mongo for the specified user

        Attributes:
            user (int)

        Output:
            interests (list [])
        """
        # Creates a representation
        # of the mongo db
        users = self.db.users

        # Sets up the query dict
        query = {"user_id": user_id}

        # Queries for that user
        # then pulls only interests
        # out of the resulting dict
        interests = users.find_one(query)["interests"]
        self.logger.INFO("Returning interests list")

        return interests

    def store_user_interests(self, user_id, interests):
        """
        Stores a dictionary of the uuid and interests

        Attributes:
            user_id (int)
            interests (list [])

        Output:
            True
        """

        # Creates a representation
        # of the mongo db
        users = self.db.users
        doc = {"uuid": user_id, "interests": interests}

        user_id = users.insert_one(doc).inserted_id

        return True
