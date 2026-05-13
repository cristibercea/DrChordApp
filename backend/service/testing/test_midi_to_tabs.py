import os
from backend.service.utils.midi_to_tabs import midi_to_tabs

if __name__ == '__main__':
    assert os.path.exists("./data/test.mid")
    print("File converted to tabs in: ", midi_to_tabs(midi_path="./data/test.mid", tabs_folder="./data"))
    assert os.path.exists("./data/test.txt")
