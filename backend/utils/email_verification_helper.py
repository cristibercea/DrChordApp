import logging
from pydantic import SecretStr
from backend.utils.config_reader import config
from backend.service.utils.ServiceException import ServiceException
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType

async def send_verification_code_email(email: str, code: str) -> None:
    """
    Function that sends a verification email containing a code to verify someone's account
    :param email: email address of the recipient
    :param code: account verification code
    :return: None
    """
    logging.info(f"Configuring verification code email for {email}...")
    html_content = f"""
    <div style="font-family: Arial, sans-serif; text-align: center; padding: 20px;">
        <h2>Welcome to DrChord!</h2>
        <p>Account verification code:</p>
        <h1 style="background: #f4f4f4; padding: 15px; letter-spacing: 5px; color: #1976d2; border-radius: 8px;">
            {code}
        </h1>
        <p>Insert this code in the account verification section and then you are all set.</p>
    </div>
    """
    message = MessageSchema(
        subject="DrChord account verification code",
        recipients=[email],
        body=html_content,
        subtype=MessageType.html
    )
    is_true = lambda val: str(val).strip().lower() in ('true', '1', 'yes', 'on')
    try:
        logging.info(f"Creating verification code email for {email}...")
        email_config = config(section='email')
        logging.info(f'Sending verification code email to {email}...')
        await FastMail(
            ConnectionConfig(
                MAIL_USERNAME = str(email_config['username']),
                MAIL_PASSWORD = SecretStr(str(email_config['password'])),
                MAIL_FROM = str(email_config['from']),
                MAIL_PORT = int(str(email_config['port'])),
                MAIL_SERVER = str(email_config['server']),
                MAIL_STARTTLS = is_true(email_config['starttls']),
                MAIL_SSL_TLS = is_true(email_config['ssl_tls']),
                USE_CREDENTIALS = is_true(email_config['use_credentials']),
                VALIDATE_CERTS = is_true(email_config['validate_certs']),
            )
        ).send_message(message)
        logging.info(f"Verification code email sent to {email}.")
    except FileNotFoundError | RuntimeError as e:
        logging.fatal(e)
        raise ServiceException(e)