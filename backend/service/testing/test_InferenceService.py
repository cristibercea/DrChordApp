import logging
from unittest import IsolatedAsyncioTestCase
from unittest.mock import patch, MagicMock
from backend.service.InferenceService import InferenceService

logging.basicConfig(filename="service/testing/target/backend.log",
                    level=logging.INFO,
                    format='%(asctime)s - [%(levelname)s] - %(message)s',
                    datefmt='%d-%b-%y %H:%M:%S',
                    filemode='w')

class TestInferenceService(IsolatedAsyncioTestCase):
    def setUp(self):
        # System Under Test
        self.service = InferenceService()

    # --- AUDIO TO MIDI ---
    @patch('backend.service.InferenceService.subprocess.run')
    @patch('backend.service.InferenceService.os.path.exists')
    @patch('backend.service.InferenceService.os.remove')
    async def test_audio_to_midi_valid_whitebox(self, mock_remove, mock_exists, mock_subprocess_run):
        """ Verify the service correctly formats the terminal command
        to run Omnizart and handles existing files properly. """
        # Arrange
        mock_exists.return_value = True  # Pretend an old MIDI file already exists
        audio_path = "test_audio.mp3"
        model_path = "models/guitar"
        out_dir = "out"
        mock_process = MagicMock()
        mock_process.returncode = 0 # Simulate a successful subprocess execution (return code 0)
        mock_subprocess_run.return_value = mock_process

        # Act
        result = await self.service.audio_to_midi(audio_path, model_path, out_dir)

        # Assert
        mock_exists.assert_called_once()
        mock_remove.assert_called_once_with("out/test_audio.mid")  # Ensures cleanup logic works
        called_cmd = mock_subprocess_run.call_args[0][0]  # Verify the command sent to the terminal was built perfectly
        self.assertEqual(called_cmd[0], "omnizart")
        self.assertEqual(called_cmd[2], "transcribe")
        self.assertEqual(called_cmd[3], audio_path)
        self.assertEqual(result, "out/test_audio.mid")  # Verify resulted MIDI path

    @patch('backend.service.InferenceService.subprocess.run')
    @patch('backend.service.InferenceService.os.path.exists')
    async def test_audio_to_midi_invalid_blackbox(self, mock_exists, mock_subprocess_run):
        """ Simulate a crash inside the Omnizart subprocess and ensure
        the service catches the stderr output and raises an Exception. """
        # Arrange
        mock_exists.return_value = False
        mock_process = MagicMock()
        mock_process.returncode = 1  # Simulate a FAILED subprocess execution (return code 1)
        mock_process.stderr = "CUDA Out Of Memory"
        mock_subprocess_run.return_value = mock_process

        # Act & Assert
        with self.assertRaises(Exception) as context:
            await self.service.audio_to_midi("test.mp3", "model", "out")
        self.assertIn("Omnizart failed: CUDA Out Of Memory", str(context.exception)) # Verify our error wrapper intercepted the crash message

    # --- MIDI TO TAB ---
    @patch('backend.service.InferenceService.midi_to_tabs')
    async def test_midi_to_tab_valid_whitebox(self, mock_midi_to_tabs):
        """ Ensure the midi-to-tab translation thread is called properly. """
        # Arrange
        midi_path = "track.mid"
        out_dir = "tabs"
        mock_midi_to_tabs.return_value = "tabs/track_tab.txt"  # Simulate successful conversion

        # Act
        result = await self.service.midi_to_tab(midi_path, out_dir)

        # Assert
        mock_midi_to_tabs.assert_called_once_with(midi_path=midi_path, tabs_folder=out_dir)
        self.assertEqual(result, "tabs/track_tab.txt")

    @patch('backend.service.InferenceService.midi_to_tabs')
    async def test_midi_to_tab_invalid_blackbox(self, mock_midi_to_tabs):
        """ Simulate a failure in the internal midi_to_tabs parser
        and ensure the exception bubbles up safely. """

        # Arrange
        mock_midi_to_tabs.side_effect = Exception("Invalid MIDI Headers")  # Force the script to crash (e.g. invalid midi format)

        # Act & Assert
        with self.assertRaises(Exception) as context:
            await self.service.midi_to_tab("corrupt.mid", "tabs")
        self.assertIn("Invalid MIDI Headers", str(context.exception))
