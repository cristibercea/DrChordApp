import logging, os
from unittest import IsolatedAsyncioTestCase
from unittest.mock import patch, MagicMock
from backend.service.FileService import FileService

logging.basicConfig(filename="service/testing/target/backend.log",
                    level=logging.INFO,
                    format='%(asctime)s - [%(levelname)s] - %(message)s',
                    datefmt='%d-%b-%y %H:%M:%S',
                    filemode='w')

class TestFileService(IsolatedAsyncioTestCase):
    def setUp(self):
        # System Under Test
        self.file_service = FileService()

        # Test data
        self.test_filename = "test_audio.mp3"
        self.test_relative_path = f"recordings/{self.test_filename}" # simulate a relative path exactly as it would be saved in the database
        self.expected_full_path = os.path.join(self.file_service.get_base_songs_dir(),self.test_relative_path.split('songs/')[-1]) # Dynamically calculate the exact path the OS expects (handles Windows \ vs Linux / automatically)

    # --- SAVE RECORDING ---
    @patch('backend.service.FileService.shutil.copyfileobj')
    @patch('builtins.open', new_callable=MagicMock)
    async def test_save_recording_valid_whitebox(self, mock_open, mock_copy):
        """ Verify that saving a file calls the correct OS methods
        to ensure the file is written to the disk. """
        # Arrange
        mock_upload_file = MagicMock()
        mock_upload_file.filename = self.test_filename

        # Act
        result = await self.file_service.save_recording(mock_upload_file)

        # Assert WhiteBox: Check internal file operations
        mock_open.assert_called_once()
        mock_copy.assert_called_once()
        self.assertTrue(result.startswith("recordings/")) # The saved file gets a UUID, so only check the directory prefix and the extension
        self.assertTrue(result.endswith(".mp3"))

    @patch('builtins.open', new_callable=MagicMock)
    async def test_save_recording_invalid_blackbox(self, mock_open):
        """ Simulate a catastrophic OS failure (e.g., Disk Full / Permission Denied)
        and ensure the service raises a proper error. """
        # Arrange
        mock_upload_file = MagicMock()
        mock_upload_file.filename = "corrupted.mp3"
        mock_open.side_effect = PermissionError("Access Denied to Folder") # mock open() to throw an OS-level PermissionError when trying to write to the hard disk

        # Act & Assert
        with self.assertRaises(PermissionError):
            await self.file_service.save_recording(mock_upload_file)

    # --- DELETE FILE ---
    @patch('backend.service.FileService.os.remove')
    @patch('backend.service.FileService.os.path.exists')
    def test_delete_file_valid_whitebox(self, mock_exists, mock_remove):
        """ Verify that if a file exists, the OS remove function is triggered exactly once. """
        # Arrange
        mock_exists.return_value = True  # Pretend the file is actually on the disk

        # Act
        self.file_service.delete_file(self.test_relative_path)

        # Assert
        mock_exists.assert_called_once_with(self.expected_full_path)
        mock_remove.assert_called_once_with(self.expected_full_path)

    @patch('backend.service.FileService.os.remove')
    @patch('backend.service.FileService.os.path.exists')
    def test_delete_file_invalid_blackbox(self, mock_exists, mock_remove):
        """ If the file does not exist, the service should quietly skip deletion
        or raise a controlled error without crashing the backend. """
        # Arrange
        mock_exists.return_value = False  # File is missing
        ghost_path = "ghost_file.txt"

        # Act
        self.file_service.delete_file(ghost_path)

        # Assert BlackBox: OS remove must NEVER be called if the file doesn't exist
        mock_remove.assert_not_called()