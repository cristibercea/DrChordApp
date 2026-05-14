import logging, asyncpg
from datetime import datetime
from unittest import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock, MagicMock
from backend.domain.entities.Song import Song
from backend.repository.SongRepository import SongRepository
from backend.domain.database.DrChordDatabase import DrChordDatabase
from backend.repository.utils.RepositoyException import RepositoryException

logging.basicConfig(filename="repository/testing/target/backend.log",
                    level=logging.INFO,
                    format='%(asctime)s - [%(levelname)s] - %(message)s',
                    datefmt='%d-%b-%y %H:%M:%S',
                    filemode='w')

class TestSongRepository(IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        # Mocked objects
        self.mock_db = MagicMock(spec=DrChordDatabase) # mocks the database
        self.mock_conn = AsyncMock() # mocks the connection to the database
        self.mock_db.get_connection.return_value = self.mock_conn # set the mocked connection as a return value for DB's get_connection()
        self.mock_tx = AsyncMock() # mocks a transaction
        self.mock_conn.transaction = MagicMock(return_value=self.mock_tx)

        # System Under Test
        self.repo = SongRepository(self.mock_db)

        # Test data
        self.valid_song_row = (1, 5, "My Song", "Rock", "path.mp3", datetime.now(), None, None, None, None)
        self.valid_song_obj = Song(*self.valid_song_row)

    # --- GET BY ID ---
    async def test_get_by_id_valid_blackbox(self):
        self.mock_conn.fetchrow.return_value = self.valid_song_row
        result = await self.repo.get_by_id(1)
        self.assertEqual(result.get_name(), "My Song")

    async def test_get_by_id_invalid_blackbox(self):
        self.mock_conn.fetchrow.return_value = None
        result = await self.repo.get_by_id(999)
        self.assertIsNone(result)

    # --- GET ALL PAGED BY USER ID ---
    async def test_get_all_paged_by_user_id_valid_greybox(self):
        """
        Makes the database to return a list of SQL tuples and tests if the repository maps them
        correctly to Song objects.
        """
        self.mock_conn.fetch.return_value = [
            (1, 5, "Song A", "Pop", "path1", datetime.now(), None, None, None, None),
            (2, 5, "Song B", "Jazz", "path2", datetime.now(), None, None, None, None)
        ]
        results = await self.repo.get_all_paged_by_user_id(user_id=5, limit=10, offset=0)
        self.assertEqual(len(results), 2)
        self.assertIsInstance(results[0], Song)
        self.assertEqual(results[1].get_name(), "Song B")

    async def test_get_all_paged_by_user_id_invalid_blackbox(self):
        self.mock_conn.fetch.side_effect = Exception("DB Crash")
        with self.assertRaises(RepositoryException):
            await self.repo.get_all_paged_by_user_id(5, 10, 0)

    # --- CREATE ---
    async def test_create_valid_whitebox(self):
        self.mock_conn.fetchval.return_value = 1
        await self.repo.create(self.valid_song_obj)
        called_sql = self.mock_conn.fetchval.call_args[0][0]
        self.assertTrue(called_sql.startswith("INSERT INTO songs"))

    async def test_create_invalid_blackbox(self):
        self.mock_conn.fetchval.side_effect = asyncpg.PostgresError("Constraint Violation")
        with self.assertRaises(RepositoryException):
            await self.repo.create(self.valid_song_obj)

    # --- UPDATE ---
    async def test_update_valid_blackbox(self):
        self.mock_conn.execute.return_value = "UPDATE 1"
        result = await self.repo.update(self.valid_song_obj)
        self.assertIsNone(result)

    async def test_update_invalid_blackbox(self):
        self.mock_conn.execute.return_value = "UPDATE 0"
        result = await self.repo.update(self.valid_song_obj)
        self.assertEqual(result.get_genre(), "Rock")

    # --- DELETE ---
    async def test_delete_valid_greybox(self):
        """
        Tests delete logic which uses SQL RETURNING syntax. Mocks fetchrow to return the deleted
        row and ensures that the repository returns deleted object.
        """
        self.mock_conn.fetchrow.return_value = self.valid_song_row
        result = await self.repo.delete(1)
        self.assertIsNotNone(result)
        self.assertEqual(result.get_id(), 1)
        self.assertIsInstance(result, Song)

    async def test_delete_invalid_blackbox(self):
        self.mock_conn.fetchrow.return_value = None
        result = await self.repo.delete(999)
        self.assertIsNone(result)