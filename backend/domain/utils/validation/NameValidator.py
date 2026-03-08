import logging
from string import ascii_letters, digits
from backend.domain.utils.validation.AbstractValidator import AbstractValidator
from backend.domain.utils.validation.ValidationException import ValidationException


class NameValidator(AbstractValidator):
    def validate(self, name: str):
        logging.info(f"Validating Name: {name}")
        for c in name:
            if c not in ascii_letters+" _-"+digits:
                logging.warning(f"Invalid Name: {name}")
                raise ValidationException(f"Invalid username '{c}'")
        logging.info(f"Valid Name: '{name}'")
