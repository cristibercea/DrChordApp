import os, logging, numpy as np
from unittest import TestCase
from backend.service.utils.midi_to_tabs import midi_to_tabs

np.seterr(divide="ignore")
logging.basicConfig(filename="service/testing/target/backend.log",
                    level=logging.INFO,
                    format='%(asctime)s - [%(levelname)s] - %(message)s',
                    datefmt='%d-%b-%y %H:%M:%S',
                    filemode='w')

class TestTutTutMidiToTabs(TestCase):
    def setUp(self):
        # Test data
        self.data_dir = "service/testing/data"
        self.test_midi_path = self.data_dir+"/test.mid"
        self.test_tabs_path = self.data_dir+"/test.txt"

    def test_midi_to_tabs_non_mocked_valid(self):
        """ Test a successful, non-mocked MIDI to Tabs transcription using TutTut.
        The generated tabs will be available in /backend/service/testing/data """
        # Arrange
        self.assertTrue(os.path.exists(self.test_midi_path))  # there must be a valid MIDI file in the data directory
        os.remove(self.test_tabs_path) if os.path.exists(self.test_tabs_path) else None  # do a cleanup before re-running the test
        self.assertFalse(os.path.exists(self.test_tabs_path))  # the est can now be run, if this does not fail

        # Act
        logging.info(f'MIDI_TO_TABS_TEST: File converted to tabs in: {midi_to_tabs(midi_path=self.test_midi_path, tabs_folder=self.data_dir)}')

        # Assert
        self.assertTrue(os.path.exists(self.test_tabs_path))
