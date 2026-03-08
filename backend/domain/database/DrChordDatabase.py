import logging, psycopg2
from psycopg2 import sql
from backend.domain.database.utils.db_config import config

def _create_db_if_not_exists(db_name, user, password, host="localhost"):
    """
    Create a new PostgreSQL DB with a given name
    """
    conn = psycopg2.connect(dbname="postgres",user=user,password=password,host=host)
    conn.autocommit = True
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = %s", (db_name,))
    if not cur.fetchone():
        logging.info(f"Database {db_name} does not exist. Creating...")
        cur.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(db_name)))
        logging.info("Success.")
    else: logging.info(f"Database {db_name} already exists.")
    cur.close()
    conn.close()

def _drop_db_force(db_name, user, password, host="localhost"):
    """
    Close any connection to the given PostgreSQL DB and drop it
    """
    conn = psycopg2.connect(dbname="postgres", user=user, password=password, host=host)
    conn.autocommit = True
    cur = conn.cursor()
    try:
        cur.execute("""
                    SELECT pg_terminate_backend(pg_stat_activity.pid) FROM pg_stat_activity
                    WHERE pg_stat_activity.datname = %s AND pid <> pg_backend_pid()
                    """, (db_name,))
        logging.info(f"Erasing database '{db_name}'...")
        cur.execute(sql.SQL("DROP DATABASE IF EXISTS {}").format(sql.Identifier(db_name)))
        logging.info("Succes.")
    except Exception as e: logging.error(e)
    finally:
        cur.close()
        conn.close()


class DrChordDatabase:
    """
    This class is responsible for connecting to the DRChord database. It creates and deletes a PostgreSQL database,
    creates and retrieves database connections and offers versioning.
    """
    def __init__(self, db_config_file_path: str | None = None):
        try: self.__connection_params = config(filename=db_config_file_path)
        except FileNotFoundError as e:
            logging.fatal(e)
            exit(1)
        self.__version = 1
        self.__connection = None

    def __del__(self): self.__disconnect()

    def __connect(self):
        logging.info("Connecting to the database...")
        self.__connection = psycopg2.connect(**self.__connection_params)

    def __disconnect(self):
        logging.info("Disconnecting from the database...")
        self.__connection.close() if self.__connection is not None else None
        self.__connection_params = None
        self.__connection = None
        self.__cursor = None

    def get_version(self):
        """
        Gets the version of DRChord database
        :return: database version
        """
        return self.__version

    def set_version(self, version: int):
        """
        Set the version of the database
        :param version: version of the database
        """
        self.__version = version

    def get_connection(self) -> psycopg2._T_conn:
        """
        Gets the connection to the database if it already exists, otherwise creates it and returns it
        :return: The connection to the database
        """
        if self.__connection is None: self.__connect()
        return self.__connection

    def delete(self):
        """
        Delete DRChord database and clean any dependencies
        :return: None
        """
        self.__version = 1
        _drop_db_force(self.__connection_params["database"], self.__connection_params["user"], self.__connection_params["password"])

    def create(self): #TODO
        """
        Create DRChord database, if it doesn't exist
        :return: None
        """
        self.__version = 1
        _create_db_if_not_exists(self.__connection_params["database"], self.__connection_params["user"], self.__connection_params["password"])
        self.__connect()
        self.__connection.autocommit = True
        cursor = self.__connection.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL,
                date_joined TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            
            CREATE TABLE IF NOT EXISTS songs (
                id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
                user_id BIGINT NOT NULL,
                name TEXT NOT NULL,
                genre TEXT NOT NULL,
                recording_path TEXT NOT NULL,
                date_recorded TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                tabs_path TEXT,
                date_generated TIMESTAMP,
            )
            
            ALTER TABLE songs ADD CONSTRAINT fk_user_id FOREIGN KEY (user_id) REFERENCES users(id)
            
            CREATE INDEX idx_users_email ON users (email)
            CREATE INDEX idx_songs_user_id_and_generated_date ON songs(user_id, date_generated)
            CREATE INDEX idx_songs_user_id_and_recorded_date ON songs(user_id, date_recorded)
            CREATE INDEX idx_songs_user_id_and_name ON songs(user_id, name)
            CREATE INDEX idx_songs_user_id_and_genre ON songs(user_id, genre)
            CREATE INDEX idx_songs_recording_path ON songs(recording_path)
            CREATE INDEX idx_songs_tabs_path ON songs(tabs_path)
        """)

        logging.info(f"Created desired schema inside database '{self.__connection_params['database']}'")
        self.__connection.autocommit = False
