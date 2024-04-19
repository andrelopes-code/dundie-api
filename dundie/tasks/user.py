import smtplib
from datetime import timedelta
from smtplib import SMTPAuthenticationError, SMTPException
from time import sleep

from sqlmodel import Session, select

from dundie.auth.functions import create_access_token
from dundie.config import settings
from dundie.db import engine
from dundie.models.user import User
from dundie.templates import env


def _send_email_debug(email: str, message: str):
    sleep(2)
    with open('mail.log', 'a') as f:
        f.write(
            f'>>> START EMAIL {email} <<<\n{message}\n>>> ENDOF EMAIL <<<\n\n'
        )
        f.flush()


def send_email_smtp(email: str, message: str):
    """
    Send email via SMTP.

    Args:
        email (str): Recipient's email address.
        message (str): Email message to be sent.

    Raises:
        SMTPAuthenticationError: If authentication fails.
        SMTPException: If an SMTP error occurs during sending.
    """
    try:
        with smtplib.SMTP_SSL(
            host=settings.email.smtp_server, port=settings.email.smtp_port
        ) as server:

            server.login(
                settings.email.smtp_user, settings.email.smtp_password
            )
            server.sendmail(
                from_addr=settings.email.smtp_sender,
                to_addrs=email,
                msg=message.encode('utf-8'),
            )

    except SMTPAuthenticationError as e:
        raise SMTPAuthenticationError(f'The SMTP authentication failed: {e}')

    except SMTPException as e:
        raise SMTPException(f'An error ocurred while sending SMTP email: {e}')


def send_email(email: str, message: str):
    """Choose which function to run based on DEBUG_MODE"""

    if settings.email.debug_mode is True:
        _send_email_debug(email, message)
    else:
        send_email_smtp(email, message)


def try_to_send_password_reset_email(email: str):
    """
    Try to send password reset email.

    Args:
        email (str): User's email address.

    Returns:
        None: If user not found or email fails to send.

    >>> try_to_send_password_reset_email('example@email.com')

    Notes:
        - Retrieves user by email from database.
        - Generates password reset token with expiry.
        - Constructs email template with reset URL and token.
        - Sends email to user's email address.
    """
    with Session(engine) as session:
        stmt = select(User).where(User.email == email)
        user = session.exec(stmt).first()

        if not user:
            return

        expire = settings.security.RESET_PASS_TOKEN_EXPIRE_MINUTES

        # Generate password reset token with expiry time
        pwd_reset_token = create_access_token(
            data={'sub': user.username},
            expires_delta=timedelta(minutes=expire),
            scope='pwd_reset',
        )

        # Render email template with reset URL and token
        template = env.get_template('password_reset_email.j2')
        context = {
            'sender': settings.email.smtp_sender,
            'to': user.email,
            'url': settings.security.PWD_RESET_URL,
            'pwd_reset_token': pwd_reset_token,
            'expire': expire,
            'recipient': user.name,
        }

        send_email(email=user.email, message=template.render(**context))
