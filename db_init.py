import logging

from pymongo import MongoClient


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
        self.user = config["db_user"]
        self.password = config["db_pass"]
        self.host = config["db_host"]
        self.port = config["db_port"]
        self.logger = logging.getLogger("zz-8")

    def connection(self):
        """
        Creates the mongo client

        Returns True
        """
        connect_string = (
            f"mongodb://{self.user}:{self.password}@{self.host}:{self.port}/zz8",
        )
        try:
            self.client = MongoClient(connect_string)
            self.logger.info("Connected to mongo")
            return True
        except Exception as ex:
            self.logger.error(f"An execption occured\n{ex}")
            return True

    def db_init(self):
        """
        Sets up the database and creates
        it, if it doesn't already exist

        Returns True
        """
        self.db = self.client.zz8
        self.logger.info("Connected to zz8 db")
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

        # Sets up the query dict
        query = {"uuid": user_id}

        # Queries for that user
        # then pulls only interests
        # out of the resulting dict
        try:
            interests = self.db.users.find_one(query)["interests"]
            self.logger.info(f"Retrieved interests for {user_id}")
        except:
            interests = []
            self.logger.warning(f"No interests stored for {user_id}")

        self.logger.info("Returning interests list")
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
        self.db.users
        doc = {"uuid": user_id, "interests": interests}

        self.db.users.insert_one(doc).inserted_id

        return True

    def update_user_interests(self, user_id, interests):
        """
        Updates a dictionary of the uuid and interests

        Attributes:
            user_id (int)
            interests (list [])

        Output:
            True
        """

        # Creates a representation
        # of the mongo db
        self.db.users

        query = {"uuid": user_id}
        newvalues = {"$set": {"uuid": user_id, "interests": interests}}

        self.db.users.update_one(query, newvalues)

        return True

    def get_channel_prefs(self):
        """
        Return every guild and the channel prefs
        for those guilds

        :return: Top level element is the guild uuid
        second level element is a list of the uuids
        of each channel
        :rtype: dict
        """
        guild_channels = {}
        try:
            prefs = self.db.guilds.find()
            self.logger.info("Retrieved the preferences for all guilds")
            for guild in prefs:
                guild_channels[guild] = guild["ignored_channels"]
        except:
            prefs = {}
            self.logger.warning("No guild interests stored currently")

        self.logger.info("Returning Preferences")
        return guild_channels

    def get_guild_prefs(self, guild):
        query = {"guild": guild}

        try:
            guild = self.db.guilds.find_one(query)["ignored_channels"]
            self.logger.info(f"Retrieved preferences for {guild}")
        except:
            guild = []
            self.logger.warning(f"No interests stored for {guild}")

        self.logger.inf("Returning guild list")
        return guild

    def store_guild_channel_prefs(self, guild, ignored_channels):
        """
        Stores the guild preferences

        :param guild: The uuid of a guild
        :type guild: int
        :param ignored_channels: The preferences for a guild
        :type ingored_channels: list
        """

        self.db.guilds
        db_dict = {"guild": guild, "ignored_channels": ignored_channels}
        self.db.guilds.insert_one(db_dict).inserted_id

        return True

    def update_guild_prefs(self, guild, pref_type, prefs):
        """
        Updates a guilds preferences

        :param guild: UUID of a guild
        :type guild: int
        :param prefs: The preferences for a guild
        :type prefs: dict
        :return: Returns true
        :rtype: Boolean
        """
        self.db.guilds

        query = {"guild": guild}
        newvalues = {"$set": {"guild": guild, pref_type: prefs}}

        self.db.guilds.update_one(query, newvalues)

        return True
