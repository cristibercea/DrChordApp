import asyncio,os,subprocess,logging
from backend.service.utils.midi_to_tabs import midi_to_tabs

class InferenceService:
    """InferenceService class - responsible with running transcription processes"""
    def __init__(self):
        self.__env_vars = os.environ.copy()
        self.__env_vars["TF_FORCE_GPU_ALLOW_GROWTH"] = "true"

    def __run_omnizart_async(self, audio_file_path: str, model_path: str, output_file: str) -> None:
        """
        Runs Omnizart framework on a separate thread which transcribes the audio file and saves it to the disk
        :param audio_file_path: the path to the audio file
        :param model_path: the path to the model
        :param output_file: the path to the output file
        :return: None
        """
        logging.info(f"[{self.__class__.__name__}]: Setting up Omnizart...")
        cmd = [
            "omnizart", "music", "transcribe", audio_file_path,
            "--model-path", model_path, "-o", output_file
        ]
        logging.info(f"[{self.__class__.__name__}]: Running Omnizart...")
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            env=self.__env_vars
        )
        if result.returncode != 0:
            error_msg = result.stderr.strip().split('\n')[-1].strip() if result.stderr else "Eroare necunoscută Omnizart"
            logging.error(f"[{self.__class__.__name__}]: Omnizart failed: {error_msg}")
            raise Exception(f"Omnizart failed: {error_msg}")
        logging.info(f"[{self.__class__.__name__}]: Omnizart finished successfully.")

    async def audio_to_midi(self, audio_file_path: str, guitar_model_path: str, output_dir: str) -> str:
        """
        Runs the transcription process (on a separate thread) that converts an Audio file to a MIDI file
        :param audio_file_path: the path to the audio file
        :param guitar_model_path: the path to the guitar model
        :param output_dir: the path to the output directory
        :return: the path to the generated midi file
        """
        logging.info(f"[{self.__class__.__name__}]: Running Audio to MIDI transcription process...")
        file_id = os.path.splitext(os.path.basename(audio_file_path))[0].split('.')[0]
        output_midi_path = output_dir+"/"+file_id+".mid"
        if os.path.exists(output_midi_path):
            try:
                logging.info(f"[{self.__class__.__name__}]: Remove existing output MIDI file, if existent.")
                os.remove(output_midi_path)
                logging.info(f"[{self.__class__.__name__}]: Removed already existing output MIDI file.")
            except: logging.info(f"[{self.__class__.__name__}]: No previous output MIDI file to erase.")
        await asyncio.to_thread(self.__run_omnizart_async, audio_file_path, guitar_model_path, output_midi_path)
        logging.info(f"[{self.__class__.__name__}]: Audio to MIDI transcription process finished successfully.")
        return output_midi_path

    async def midi_to_tab(self, midi_file_path: str, output_dir: str) -> str:
        """
        Runs the transcription process (on a separate thread) that converts a MIDI file to a text file with tabs
        and saves the tabs file to the disk.
        :param midi_file_path: the path to the MIDI file
        :param output_dir: the path to the output directory
        :return: path to the tabs file
        """
        logging.info(f"[{self.__class__.__name__}]: Running MIDI to Text Tabs transcription process...")
        path_to_tabs = await asyncio.to_thread(midi_to_tabs, midi_path=midi_file_path, tabs_folder=output_dir)
        logging.info(f"[{self.__class__.__name__}]: MIDI to Text Tabs transcription process finished successfully.")
        return str(path_to_tabs)