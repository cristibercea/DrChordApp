import os
from backend.service.utils.midi_to_tabs import midi_to_tabs

if __name__ == '__main__':
    assert os.path.exists("C:/Users/Cristian/Downloads/nierx.mid")
    print("File converted to tabs in: ",midi_to_tabs(midi_path="C:/Users/Cristian/Downloads/nierx.mid", tabs_folder="C:/Users/Cristian/Downloads"))
    assert (os.path.exists("C:/Users/Cristian/Downloads/nierx.txt")
            or os.path.exists("C:/Users/Cristian/Downloads/nierx.pdf")
            or os.path.exists("C:/Users/Cristian/Downloads/nierx.docx")
            or os.path.exists("C:/Users/Cristian/Downloads/nierx.odt"))
