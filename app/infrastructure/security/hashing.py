import logging

import bcrypt

logger = logging.getLogger(__name__)


def hash_password(password: str) -> bytes:
    logger.debug("hashing password")
    salt: bytes = bcrypt.gensalt()
    pwd_bytes: bytes = password.encode()
    return bcrypt.hashpw(pwd_bytes, salt)


def validate_password(
    password: str,
    hashed_password: bytes,
) -> bool:
    """
    Function for validating non encoded password
    :param password: string from client
    :param hashed_password: password that was got from database
    :return: True if password is valid, False otherwise
    """
    logger.debug("validating password")
    return bcrypt.checkpw(
        password=password.encode(),
        hashed_password=hashed_password,
    )
