import logging, os.path
from datetime import datetime, timezone
from backend.domain.entities.Song import Song
from backend.domain.utils.validation.AbstractValidator import AbstractValidator
from backend.domain.utils.validation.NameValidator import NameValidator
from backend.domain.utils.validation.ValidationException import ValidationException


class SongValidator(AbstractValidator):
    def validate(self, song: Song):
        logging.info(f"Validating Song: {song}")
        if song is None:
            logging.warning("The Song is None")
            raise ValidationException("The song is None")
        errors = []
        if song.get_user_id() is None: errors.append("The Song's user reference is None")
        if song.get_name() is None: errors.append("The Song's name is None")
        if song.get_genre() is None: errors.append("The Song's genre is None")
        if song.get_recording_path() is None: errors.append("The Song's recording path is None")
        if song.get_recording_date() is None: errors.append("The Song's recording date is None")
        if (song.get_generated_date() is None and song.get_tabs_path() is not None) or \
                (song.get_tabs_path() is None and song.get_generated_date() is not None):
            errors.append("The Song's tabs generation is invalid")

        if errors:
            logging.warning(f"Invalid Song: {errors}")
            raise ValidationException(errors)

        nameValidator = NameValidator()
        try: nameValidator.validate(song.get_name())
        except ValidationException as e: errors.append(e.__str__())
        try: nameValidator.validate(song.get_genre())
        except ValidationException as e: errors.append(e.__str__())
        if not os.path.isfile(song.get_recording_path()):
            errors.append("The Song's recording path does not exist on the server")
        if song.get_recording_date() >= datetime.now(timezone.utc):
            errors.append("The Song's recording date can not be in the future")
        if song.get_tabs_path().strip() and not os.path.isfile(song.get_tabs_path()):
            errors.append("The Song's tabs path does not exist on the server")
        if song.get_generated_date() and song.get_generated_date() >= datetime.now(timezone.utc):
            errors.append("The Song's tabs generation date can not be in the future")

        if errors:
            logging.warning(f"Invalid Song: {errors}")
            raise ValidationException(errors)
        logging.info(f"Valid Song: {song}")
