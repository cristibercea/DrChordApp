import os

def rename_guitarset_files(audio_dir, suffix):
    """
    Eliminates '_hex_cln' suffix GuitarSet audio files, to match jams/midi annotations
    :param audio_dir: audio files directory
    :param suffix: suffix of audio files to be renamed
    :return: None
    """
    if not os.path.exists(audio_dir):
        print(f"FAIL: {audio_dir} directory not found")
        return

    count = 0
    for filename in os.listdir(audio_dir):
        if suffix in filename:
            # Rename phase
            new_name = filename.replace(suffix, "")
            old_path = os.path.join(audio_dir, filename)
            new_path = os.path.join(audio_dir, new_name)
            try:
                os.rename(old_path, new_path)
                print(f"Renamed: {filename} -> {new_name}")
                count += 1
            except Exception as e:
                print(f"Failure when renaming {filename}: {e}")

    print(f"\nSUCCESS: {count} files were renamed.")

if __name__ == "__main__":
    path_to_audio = "C:/Users/Cristian/Downloads/GuitarSet_mono/audio"
    rename_guitarset_files(path_to_audio, "_mic")