import asyncio,os,glob,shutil,subprocess
from typing_extensions import Any
from backend.service.utils.midi_to_tabs import midi_to_tabs


class InferenceService:
    def __init__(self):
        self.env_vars = os.environ.copy()
        self.env_vars["TF_FORCE_GPU_ALLOW_GROWTH"] = "true"

    def _run_omnizart_sync(self, audio_file_path: str, output_file: str) -> bool:
        """Rulează Omnizart normal (va fi chemată de un thread separat)"""
        model_path = "../guitar_model/music"

        cmd = [
            "omnizart", "music", "transcribe",
            audio_file_path,
            "--model-path", model_path,
            "-o", output_file
        ]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            env=self.env_vars
        )
        if result.returncode != 0:
            error_msg = result.stderr.strip().split('\n')[-1].strip() if result.stderr else "Eroare necunoscută Omnizart"
            raise Exception(f"Omnizart a eșuat: {error_msg}")
        return True

    async def audio_to_midi(self, audio_file_path: str, output_dir: str) -> str:
        """Rulează Omnizart pe fundal folosind fire de execuție."""
        file_id = os.path.splitext(os.path.basename(audio_file_path))[0].split('.')[0]
        output_midi_path = output_dir+"/"+file_id+".mid"
        if os.path.exists(output_midi_path):
            try: os.remove(output_midi_path)
            except: pass
        await asyncio.to_thread(self._run_omnizart_sync, audio_file_path, output_midi_path)
        return output_midi_path

    async def midi_to_tab(self, midi_file_path: str, output_dir: str) -> str:
        """Apelează codul tău nativ Python pentru TutTut într-un thread separat."""
        path_to_tabs = await asyncio.to_thread(midi_to_tabs, midi_path=midi_file_path, tabs_folder=output_dir)
        return str(path_to_tabs)