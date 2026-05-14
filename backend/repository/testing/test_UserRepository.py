import logging, asyncpg
from datetime import datetime
from unittest import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock, MagicMock
from backend.domain.entities.User import User
from backend.repository.UserRepository import UserRepository
from backend.domain.database.DrChordDatabase import DrChordDatabase
from backend.repository.utils.RepositoyException import RepositoryException

logging.basicConfig(filename="repository/testing/target/backend.log",
                    level=logging.INFO,
                    format='%(asctime)s - [%(levelname)s] - %(message)s',
                    datefmt='%d-%b-%y %H:%M:%S',
                    filemode='w')

class TestUserRepository(IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        # Mocked objects
        self.mock_db = MagicMock(spec=DrChordDatabase)  # mocks the database
        self.mock_conn = AsyncMock()  # mocks the connection to the database
        self.mock_db.get_connection.return_value = self.mock_conn  # set the mocked connection as a return value for DB's get_connection()
        self.mock_tx = AsyncMock()  # mocks a transaction
        self.mock_conn.transaction = MagicMock(return_value=self.mock_tx)

        # System Under Test
        self.repo = UserRepository(self.mock_db)

        # Test data
        self.valid_user_row = (1, "John Doe", "john@example.com", "hashed_pwd", datetime.now())
        self.valid_user_obj = User(*self.valid_user_row)

    # --- GET BY ID ---
    async def test_get_by_id_valid_blackbox(self):
        self.mock_conn.fetchrow.return_value = self.valid_user_row
        result = await self.repo.get_by_id(1)
        self.assertEqual(result.get_name(), "John Doe")

    async def test_get_by_id_invalid_blackbox(self):
        self.mock_conn.fetchrow.return_value = None
        result = await self.repo.get_by_id(999)
        self.assertIsNone(result)

    # --- GET BY EMAIL ---
    async def test_get_by_email_valid_blackbox(self):
        self.mock_conn.fetchrow.return_value = self.valid_user_row
        result = await self.repo.get_by_email("john@example.com")
        self.assertEqual(result.get_id(), 1)

    async def test_get_by_email_invalid_greybox(self):
        """
        If the network fails, asyncpg raises PostgresError.
        Tests if repository catches this exception and raises it as a RepositoryException.
        """
        self.mock_conn.fetchrow.side_effect = asyncpg.PostgresError("Connection lost")

        with self.assertRaises(RepositoryException) as context:
            await self.repo.get_by_email("test@mail.com")
        self.assertIn("Database error", str(context.exception))

    # --- CREATE ---
    async def test_create_valid_blackbox(self):
        self.mock_conn.fetchval.return_value = 1
        new_user = User(-1, "Jane", "jane@mail.com", "pwd", datetime.now())
        result = await self.repo.create(new_user)
        self.assertEqual(result.get_id(), 1)

    async def test_create_invalid_blackbox(self):
        self.mock_conn.fetchval.side_effect = Exception("Generic DB Failure")
        with self.assertRaises(RepositoryException):
            await self.repo.create(self.valid_user_obj)

    # --- UPDATE ---
    async def test_update_valid_blackbox(self):
        self.mock_conn.execute.return_value = "UPDATE 1"
        result = await self.repo.update(self.valid_user_obj)
        self.assertIsNone(result)

    async def test_update_invalid_greybox(self):
        """ The execute() method returns an operation status string. If the id does not exist, it returns 'UPDATE 0'.
        Tests if the internal logic treats this case correctly (return None). """
        self.mock_conn.execute.return_value = "UPDATE 0"
        result = await self.repo.update(self.valid_user_obj)
        self.assertEqual(result.get_email(), "john@example.com")

    # --- DELETE ---
    async def test_delete_valid_blackbox(self):
        self.mock_conn.fetchrow.return_value = self.valid_user_row
        result = await self.repo.delete(1)
        self.assertEqual(result.get_email(), "john@example.com")

    async def test_delete_invalid_blackbox(self):
        self.mock_conn.fetchrow.return_value = None
        result = await self.repo.delete(999)
        self.assertIsNone(result)