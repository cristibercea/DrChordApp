import logging
from datetime import datetime, timedelta
from unittest import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock, MagicMock, patch
from backend.domain.entities.Song import Song
from backend.repository.SongRepository import SongRepository
from backend.service.SongService import SongService
from backend.service.utils.ServiceException import ServiceException
from backend.service.FileService import FileService
from backend.service.InferenceService import InferenceService

logging.basicConfig(filename="service/testing/target/backend.log",
                    level=logging.INFO,
                    format='%(asctime)s - [%(levelname)s] - %(message)s',
                    datefmt='%d-%b-%y %H:%M:%S',
                    filemode='w')

class TestSongService(IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        # Mock the repository
        self.mock_repo = AsyncMock(spec=SongRepository)
        self.service = SongService(self.mock_repo, FileService(), InferenceService())

        # Name mangling to mock the internal private FileService and InferenceService
        self.mock_file_service = AsyncMock()
        self.mock_file_service.get_base_songs_dir = MagicMock(return_value="songs/")
        self.mock_file_service.get_midis_dir = MagicMock(return_value="midis/")
        self.mock_file_service.get_tabs_dir = MagicMock(return_value="tabs/")
        self.mock_inference_service = AsyncMock()
        self.service._SongService__file_service = self.mock_file_service
        self.service._SongService__inference_service = self.mock_inference_service

        # Test data
        self.valid_song = Song(1, 5, "My Riff", "Rock",
                               "songs/track.mp3", datetime.now()  - timedelta(minutes=5),
                               "tabs/track_tab.txt", datetime.now(),
                               "midis/track.mid", datetime.now())

    # --- CREATE SONG ---
    async def test_create_song_valid_greybox(self):
        """ Test orchestration: if DB save succeeds, the physical file must NOT be deleted. """
        # Arrange
        mock_file = MagicMock()
        mock_file.filename = "test.mp3"
        self.mock_file_service.save_recording.return_value = "songs/test.mp3"
        self.mock_repo.create.return_value = self.valid_song

        # Act
        await self.service.create_song(5, "Riff", "Rock", mock_file)

        # Assert
        self.mock_file_service.save_recording.assert_called_once()
        self.mock_file_service.delete_file.assert_not_called()

    async def test_create_song_invalid_greybox(self):
        """ Test orchestration rollback: if physical file is saved, but DB fails,
        the service MUST delete the physical file to prevent server storage leaks. """
        # Arrange
        mock_file = MagicMock()
        mock_file.filename = "test.mp3"
        self.mock_file_service.save_recording.return_value = "songs/test.mp3"
        self.mock_repo.create.return_value = None  # Simulate DB failure

        # Act & Assert
        with self.assertRaises(ServiceException) as context:
            await self.service.create_song(5, "Riff", "Rock", mock_file)

        self.assertIn("Database error", str(context.exception))
        self.mock_file_service.delete_file.assert_called_once_with("songs/test.mp3")

    # --- TRIGGER TAB GENERATION (ML ORCHESTRATION) ---
    @patch('backend.service.SongService.ws_manager', new_callable=AsyncMock)  # Patch the WebSocket manager globally
    async def test_trigger_tab_generation_valid_whitebox(self, mock_ws_manager):
        """ Verify the AI pipeline flow: audio_to_midi -> midi_to_tab -> DB update -> WS Success """
        # Arrange
        song_without_tabs = Song(1, 5, "My Riff", "Rock", "songs/track.mp3", datetime.now(), None, None, None, None)
        self.mock_repo.get_by_id.return_value = song_without_tabs
        self.mock_inference_service.audio_to_midi.return_value = "/absolute/path/to/midis/track.mid" # Mock the AI MIDI predictions
        self.mock_inference_service.midi_to_tab.return_value = "/absolute/path/to/tabs/track_tab.txt" # Mock the AI tabs predictions
        self.mock_repo.update.return_value = None  # Update success

        # Act
        await self.service.trigger_tab_generation(1, 5)

        # Assert WhiteBox: Check if the AI pipeline was triggered correctly
        self.mock_inference_service.audio_to_midi.assert_called_once()
        self.mock_inference_service.midi_to_tab.assert_called_once()

        # Assert (WebSocket success message was sent)
        ws_call_args = mock_ws_manager.send_personal_message.call_args[0][0]
        self.assertIn("TAB_READY", ws_call_args)

    @patch('backend.service.SongService.ws_manager', new_callable=AsyncMock)
    async def test_trigger_tab_generation_invalid_greybox(self, mock_ws_manager):
        """ Simulate an AI crash (e.g., OutOfMemory). The service should catch it
        and send a TAB_FAILED WebSocket event to the client instead of completely crashing. """
        # Arrange
        self.mock_repo.get_by_id.return_value = self.valid_song
        self.mock_inference_service.audio_to_midi.side_effect = Exception("CUDA Out of Memory") # Simulate AI model crash

        # Act
        await self.service.trigger_tab_generation(1, 5)

        # Assert (the fallback WebSocket message)
        ws_call_args = mock_ws_manager.send_personal_message.call_args[0][0]
        self.assertIn("TAB_FAILED", ws_call_args)
        self.assertIn("Song update failed after tabs generation", ws_call_args)

    # --- UPDATE SONG ---
    async def test_update_song_valid_whitebox(self):
        """ Ensure the updated song object contains the preserved physical paths. """
        # Arrange
        self.mock_repo.get_by_id.return_value = self.valid_song
        self.mock_repo.update.return_value = None

        # Act
        await self.service.update_song(1, 5, "New Riff", "Jazz")

        # Assert
        called_song_obj = self.mock_repo.update.call_args[0][0]
        self.assertEqual(called_song_obj.get_name(), "New Riff")
        self.assertEqual(called_song_obj.get_recording_path(), "songs/track.mp3")

    async def test_update_song_invalid_blackbox(self):
        """ Try to update a song that belongs to another user. Expect Unauthorized. """
        # Arrange
        self.mock_repo.get_by_id.return_value = self.valid_song  # belongs to user_id = 5

        # Act & Assert
        with self.assertRaises(ServiceException) as context:
            await self.service.update_song(1, 999, "Hacker Riff", "Metal")
        self.assertIn("permission", str(context.exception))

    # --- DELETE SONG ---
    async def test_delete_song_valid_greybox(self):
        """ Test cascading physical deletion. If a song is deleted, the service MUST
        attempt to delete the audio file, the MIDI, the base TXT tab, and its generated variants. """
        # Arrange
        self.mock_repo.get_by_id.return_value = self.valid_song
        self.mock_repo.delete.return_value = self.valid_song

        # Act
        await self.service.delete_song(1, 5)

        # Assert (physical cleanup logic)
        delete_calls = [call[0][0] for call in self.mock_file_service.delete_file.call_args_list]
        self.assertIn("songs/track.mp3", delete_calls)
        self.assertTrue(any("tabs/track_tab.pdf" in c for c in delete_calls))  # Checks for derivatives

    async def test_delete_song_invalid_whitebox(self):
        """ If user lacks permission, verify that NEITHER the DB nor the File System is touched. """
        # Arrange
        self.mock_repo.get_by_id.return_value = self.valid_song  # User 5

        # Act
        with self.assertRaises(ServiceException): await self.service.delete_song(1, 888)  # User 888

        # Assert
        self.mock_repo.delete.assert_not_called()
        self.mock_file_service.delete_file.assert_not_called()