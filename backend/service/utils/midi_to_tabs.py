import pretty_midi, logging
from pathlib import Path
from tuttut.logic.tab import Tab
from tuttut.logic.theory import Tuning

def format_tabs_file(file_path: Path, measures_per_row: int = 4) -> None:
    """
    Reads a tab file and converts it to a formatted tab file, with only 'measures_per_row' measures on a single tab row
    :param file_path: path to tab file
    :param measures_per_row: number of measures per row
    :return: None
    """
    logging.info("Reading tab file.")
    with open(file_path, 'r', encoding='utf-8') as f: lines = [line.strip() for line in f.readlines()]
    tab_lines = [line for line in lines if '|' in line and len(line) > 10]
    if not tab_lines:
        logging.warning("No tabs found.")
        return
    logging.info("Processing tabs.")
    line0 = tab_lines[0] #High E sting; we use it for measure bar finding
    pipe_indices = [i for i, c in enumerate(line0) if c == '|']

    # Find separated '|' characters; this way '||' is ignored
    valid_end_pipes = []
    for k in range(len(pipe_indices) - 1):
        if pipe_indices[k + 1] - pipe_indices[k] > 1:
            valid_end_pipes.append(pipe_indices[k + 1])

    # Find where a cut shall be made in the tab row
    cut_points = []
    for i in range(measures_per_row - 1, len(valid_end_pipes), measures_per_row):
        cut_points.append(valid_end_pipes[i])

    # If there are measures left behind, they are added at the end of the cut list
    if not cut_points or cut_points[-1] != valid_end_pipes[-1]:
        cut_points.append(valid_end_pipes[-1])

    # Extract the string names
    prefixes = [line[:line.find('|')] for line in tab_lines]
    formatted_blocks = []
    start_idx = line0.find('|')
    prev_cut = start_idx

    # Rebuild the formatted tab
    for cut in cut_points:
        block = []
        for idx, line in enumerate(tab_lines):
            prefix = prefixes[idx]
            if prev_cut == start_idx:
                segment = line[0:cut + 1]
            else:
                segment = prefix + "|" + line[prev_cut + 1:cut + 1]
            block.append(segment)

        # Unite the strings in one block, then save it
        formatted_blocks.append("\n".join(block))
        prev_cut = cut

    # Mark the last tab griff with '||' instead of a single '|'
    last_block = [line.strip()+'|' for line in formatted_blocks[-1].split('\n')]
    formatted_blocks[-1] = "\n".join(last_block)
    logging.info("Tabs formatted. Writing to file.")

    # Overwrite the initial unformatted tabs file
    with open(file_path, 'w', encoding='utf-8') as f: f.write("\n\n".join(formatted_blocks) + "\n")
    logging.info("Writing formatted tabs file finished.")

def midi_to_tabs(midi_path: str, tabs_folder: str = "./songs/tabs") -> Path:
    """
    Converts a guitar midi file to a text file with ASCII tabs and locates it in the tabs_folder
    :param midi_path: path to midi file
    :param tabs_folder: folder where tabs should be stored
    :return: path to the newly generated tabs text file
    """
    logging.info(f"Converting midi file {midi_path} to a formatted tabs file.")
    weights = {'b': 1, 'height': 1, 'length': 1, 'n_changed_strings': 1} # these values are provided in the setup of tuttut standard cli script
    midi = Path(midi_path)
    midi_data = pretty_midi.PrettyMIDI(midi.as_posix())
    tab = Tab(midi.stem, Tuning(), midi_data, weights=weights, output_dir=tabs_folder) #creates a tab object with the name of the midi file
    tab.to_ascii() #generates the tabs text file
    path_to_tabs = Path(tabs_folder) / f"{midi.stem}.txt"
    format_tabs_file(path_to_tabs, measures_per_row=2)
    logging.info(f"Tabs file saved in {path_to_tabs}.")
    return path_to_tabs
