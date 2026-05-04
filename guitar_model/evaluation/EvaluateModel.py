import os,glob,pretty_midi,mir_eval,numpy as np


def extract_notes(midi_path: str):
    """
    Extract notes from a midi file.
    :param midi_path: path to midi file
    :return: extracted notes as numpy arrays
    """
    try: pm = pretty_midi.PrettyMIDI(midi_path)
    except Exception as e: print(f"Error while reading {midi_path}: {e}"); return np.empty((0, 2)), np.empty(0)

    intervals = []
    pitches_hz = []

    for inst in pm.instruments:
        if inst.is_drum: continue
        for note in inst.notes:
            intervals.append([note.start, note.end])
            pitches_hz.append(pretty_midi.note_number_to_hz(note.pitch)) # mir_eval uses absolute frequencies (Hz) for comparations

    if not intervals: return np.empty((0, 2)), np.empty(0)
    return np.array(intervals), np.array(pitches_hz)

def run_omnizart_model_evaluation():
    original_midis = "C:/Users/Cristian/Downloads/gs_real"
    generated_midis = "C:/Users/Cristian/Downloads/gs_midi"

    f1s = []
    precisions = []
    recalls = []

    print("Start model evaluation...")

    for orig in glob.glob(os.path.join(original_midis, "*.mid")):
        fname = os.path.basename(orig)
        generated_file = os.path.join(generated_midis, fname)

        if not os.path.exists(generated_file): continue

        ref_intervals, ref_pitches = extract_notes(orig)
        est_intervals, est_pitches = extract_notes(generated_file)

        # Calculates F1 score using Onset standard (50ms error tolerance on note strike)
        p, r, f1, _ = mir_eval.transcription.precision_recall_f1_overlap(
            ref_intervals, ref_pitches, est_intervals, est_pitches,
            onset_tolerance=0.05, pitch_tolerance=50.0, offset_ratio=None
        )

        print(f"{fname} -> F1: {f1 * 100:.2f}% (Precision: {p * 100:.1f}%, Recall: {r * 100:.1f}%)")

        f1s.append(f1)
        precisions.append(p)
        recalls.append(r)

    print("-" * 50)
    print(f"AVERAGE F1 SCORE (Piano to Guitar Transfer Learning): {np.mean(f1s) * 100:.2f}%")
    print(f"Average Precision: {np.mean(precisions) * 100:.2f}%")
    print(f"Average Recall: {np.mean(recalls) * 100:.2f}%")

if __name__ == '__main__': run_omnizart_model_evaluation()