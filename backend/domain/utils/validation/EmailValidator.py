import re, logging
from backend.domain.utils.validation.AbstractValidator import AbstractValidator
from backend.domain.utils.validation.ValidationException import ValidationException


class EmailValidator(AbstractValidator):
    def validate(self, email: str):
        logging.info(f"Validating Email: {email}")
        email = email.strip()
        if email == "":
            logging.warning("Email is empty")
            raise ValidationException("Email is required")
        email_regex = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(email_regex, email):
            logging.warning(f"Invalid Email Format: {email}")
            raise ValidationException(f"Invalid email format: '{email}'")
        logging.info(f"Valid Email: '{email}'")