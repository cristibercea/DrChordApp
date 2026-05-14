import logging
from datetime import datetime
from unittest import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock, patch
from backend.domain.entities.User import User
from backend.repository.UserRepository import UserRepository
from backend.repository.utils.RepositoyException import RepositoryException
from backend.service.UserService import UserService
from backend.service.utils.ServiceException import ServiceException

logging.basicConfig(filename="service/testing/target/backend.log",
                    level=logging.INFO,
                    format='%(asctime)s - [%(levelname)s] - %(message)s',
                    datefmt='%d-%b-%y %H:%M:%S',
                    filemode='w')

class TestUserService(IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        # Mock the repository
        self.mock_repo = AsyncMock(spec=UserRepository)

        # System Under Test
        self.service = UserService(self.mock_repo)

        # Test data
        self.valid_user = User(1, "John Doe", "john@mail.com", "$2b$12$hashedpassword", datetime.now())

    # --- REGISTER USER ---
    @patch('backend.service.UserService._get_password_hash')
    async def test_register_user_valid_whitebox(self, mock_hash):
        """ Verify that the service passes a properly hashed password to the repository. """
        # Arrange
        mock_hash.return_value = "$2b$12$fakehashedpassword"
        self.mock_repo.create.return_value = User(1, "John", "john@mail.com", "$2b$12$fakehashedpassword", datetime.now())

        # Act
        await self.service.register_user("John", "john@mail.com", "MySecret123!")

        # Assert WhiteBox: Inspect the arguments passed to repo.create()
        called_args = self.mock_repo.create.call_args[0][0]
        self.assertEqual(called_args.get_name(), "John")
        self.assertEqual(called_args.get_password(), "$2b$12$fakehashedpassword")
        mock_hash.assert_called_once_with("MySecret123!")

    async def test_register_user_invalid_blackbox(self):
        """ Input an existing email (triggering DB constraint), expect a ServiceException. """
        # Arrange
        self.mock_repo.create.side_effect = RepositoryException("Email already exists")

        # Act & Assert
        with self.assertRaises(ServiceException):
            await self.service.register_user("Jane", "john@mail.com", "pass")

    # --- AUTHENTICATE USER ---
    @patch('backend.service.UserService._verify_password')
    @patch('backend.service.UserService._create_access_token')
    async def test_authenticate_user_valid_blackbox(self, mock_create_token, mock_verify):
        """ Input valid credentials, expect the token and user data to be returned. """
        # Arrange
        self.mock_repo.get_by_email.return_value = self.valid_user
        mock_verify.return_value = True  # Simulate password match
        mock_create_token.return_value = "fake_jwt_token"

        # Act
        result = await self.service.authenticate_user("john@mail.com", "correct_pass")

        # Assert
        self.assertEqual(result["token"], "fake_jwt_token")
        self.assertEqual(result["user"]["email"], "john@mail.com")

    async def test_authenticate_user_invalid_greybox(self):
        """ Simulate a database crash (RepositoryException) and ensure the Service
        catches it and re-raises it as a clean ServiceException to protect the UI. """
        # Arrange
        self.mock_repo.get_by_email.side_effect = RepositoryException("DB Timeout")

        # Act & Assert
        with self.assertRaises(ServiceException) as context:
            await self.service.authenticate_user("test@mail.com", "pass")
        self.assertIn("DB Timeout", str(context.exception))

    # --- UPDATE USER ---
    @patch('backend.service.UserService._verify_password')
    @patch('backend.service.UserService._get_password_hash')
    async def test_update_user_valid_greybox(self, mock_hash, mock_verify):
        """ We know the internal flow requires fetching the user, verifying the old password,
        and then updating. We mock the internal flow to simulate a successful password change. """
        # Arrange
        self.mock_repo.get_by_id.return_value = self.valid_user
        mock_verify.return_value = True  # Current password matches
        mock_hash.return_value = "new_hashed_password"
        self.mock_repo.update.return_value = None  # None means success in Repository

        # Act
        result = await self.service.update_user(1, "New John", "old_pass", "new_pass")

        # Assert
        self.assertEqual(result.get_name(), "New John")
        self.assertEqual(result.get_password(), "new_hashed_password")
        self.mock_repo.update.assert_called_once()

    @patch('backend.service.UserService._verify_password')
    async def test_update_user_invalid_whitebox(self, mock_verify):
        """ If the current password is wrong, verify that repo.update is NEVER called. """
        # Arrange
        self.mock_repo.get_by_id.return_value = self.valid_user
        mock_verify.return_value = False  # Current password does NOT match

        # Act
        with self.assertRaises(ServiceException):
            await self.service.update_user(1, "John", "wrong_pass", "new_pass")

        # Assert WhiteBox: Ensure update call is blocked in the Repository
        self.mock_repo.update.assert_not_called()

    # --- DELETE USER ---
    async def test_delete_user_valid_whitebox(self):
        """ Verify that the delete method calls the repository with the correct ID. """
        # Arrange
        self.mock_repo.delete.return_value = self.valid_user

        # Act
        await self.service.delete_user(1)

        # Assert
        self.mock_repo.delete.assert_called_once_with(1)

    async def test_delete_user_invalid_blackbox(self):
        """ Try to delete a non-existent user, expect an error. """
        # Arrange
        self.mock_repo.delete.return_value = None

        # Act & Assert
        with self.assertRaises(ServiceException):
            await self.service.delete_user(999)