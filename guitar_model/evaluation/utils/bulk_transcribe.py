import os,glob,subprocess, shutil
from concurrent.futures import as_completed,ThreadPoolExecutor
from typing_extensions import Any
env_vars = os.environ.copy()
env_vars["TF_FORCE_GPU_ALLOW_GROWTH"] = "true"


def transcribe_single(wav, folder_output, model_path):
    """
    Process a single .wav file and return the status of the midi transcription.
    :param wav: path to .wav file
    :param folder_output: MIDI output folder path
    :param model_path: omnizart model path
    :return: status of the transcription as a string
    """
    filename = os.path.basename(wav)
    basename = os.path.splitext(filename)[0]
    result = subprocess.run(["omnizart", "music", "transcribe", wav, "--model-path", model_path],capture_output=True, text=True, env=env_vars)

    if result.returncode == 0:
        generated = glob.glob(os.path.join("../../..", f"{basename}*.mid"))
        if generated:
            output_path = os.path.join(folder_output, f"{basename}.mid")
            if os.path.exists(output_path):
                try: os.remove(output_path)
                except Any: pass
            shutil.move(generated[0], output_path)
            return f"[SUCCESS] {filename} moved to {folder_output}"
        else: return f"[WARNING] Transcription finished. MIDI not found for: {filename}"
    else: return f"[ERROR] {filename} | Reason: "+result.stderr.strip().split('\n')[-1].strip()

def bulk_transcribe(folder_audio: str, folder_output: str, model_path: str, max_workers: int = 2) -> None:
    """
    Utility function for bulk and parallel omnizart music transcription. It is used for generating MIDI files from WAV files.
    Generated MIDI files were used to calculate omnizart transcription model performance metrics (Recall, Precision, F1-score).
    :param max_workers: maximum number of threads to use
    :param folder_audio: audio folder path
    :param folder_output: output folder path
    :param model_path: omnizart model path
    :return: None
    """
    #
    if not os.path.exists(folder_output): os.makedirs(folder_output)
    wavs = glob.glob(os.path.join(folder_audio, "*.wav"))
    if not wavs: print(f"No .wav file in: {folder_audio}"); return
    print(f"Found {len(wavs)} audio files. Processing...")

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(transcribe_single, wav, folder_output, model_path) for wav in wavs]
        for future in as_completed(futures): print(future.result())

    print("=" * 40)
    print(f"Bulk transcribe over. MIDI path: {folder_output}")

# Test run
if __name__ == "__main__":
    bulk_transcribe(
        folder_audio="C:/Users/Cristian/Downloads/GuitarSet_mono/train_data",
        folder_output="C:/Users/Cristian/Downloads/gs_midi2",
        model_path="../../music",
        max_workers=4
    )