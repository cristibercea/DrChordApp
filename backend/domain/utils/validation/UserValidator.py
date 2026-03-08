import logging
from datetime import datetime, timezone
from backend.domain.entities.User import User
from backend.domain.utils.validation.AbstractValidator import AbstractValidator
from backend.domain.utils.validation.EmailValidator import EmailValidator
from backend.domain.utils.validation.NameValidator import NameValidator
from backend.domain.utils.validation.ValidationException import ValidationException


class UserValidator(AbstractValidator):
    def validate(self, user: User):
        logging.info(f"Validating User: {user}")
        if user is None:
            logging.warning("The User is None")
            raise ValidationException("The User is None")
        errors = []
        if user.get_name() is None: errors.append("The User's name is None")
        if user.get_email() is None: errors.append("The User's email is None")
        if user.get_password() is None: errors.append("The User's password is None")
        if user.get_date_joined() is None: errors.append("The User's register date is None")
        if errors:
            logging.warning(f"Invalid User: {user}")
            raise ValidationException(errors)

        emailValidator = EmailValidator()
        try: emailValidator.validate(user.get_email())
        except ValidationException as e: errors.append(e.__str__())
        nameValidator = NameValidator()
        try: nameValidator.validate(user.get_name())
        except ValidationException as e: errors.append(e.__str__())
        if user.get_date_joined() >= datetime.now(timezone.utc):
            errors.append("The User's register date can not be in the future")

        if errors:
            logging.warning(f"Invalid User: {user}")
            raise ValidationException(errors)
        logging.info(f"Valid User: {user}")
