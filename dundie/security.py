from passlib.context import CryptContext

pass_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


def verify_password(plain_pass: str, hashed_pass: str) -> bool:
    """
    Verify if a plain password matches a hashed password.

    Args:
        plain_pass (str): The plain password to be verified.
        hashed_pass (str): The hashed password to be compared against.

    Returns:
        bool: True if the plain password matches the hashed password,
        False otherwise.
    """
    return pass_context.verify(plain_pass, hashed_pass)


def get_password_hash(plain_pass: str) -> str:
    """
    Generate a password hash from a plain password.

    Args:
        plain_pass (str): The plain password to be hashed.

    Returns:
        str: The hashed password.
    """
    return pass_context.hash(plain_pass)


class HashedPassword(str):
    """
    Represents a hashed password.

    This class inherits from the built-in `str` class and provides a mechanism
    to validate and hash passwords.

    Methods:
        __get_validators__:
            Generates a validator function that will be used to validate the
            input.

        validate:
            Validates the input and returns a new instance with the hashed
            password.

    Usage:
        hashed_pw = HashedPassword.validate("password123")
        print(hashed_pw)  # Output: HashedPassword('hashed_password')

    """

    @classmethod
    def __get_validators__(cls):
        """
        Generates a validator function that will be used to validate the input.

        This function is a generator that yields a validator function.
        The validator function will be called in the order specified to
        validate the input. Each validator function will receive the value
        returned from the previous validator function as input.

        Returns:
            generator: A generator that yields the validator function.

        """
        # one or more validators may be yielded which will be called in the
        # order to validate the input, each validator will receive as an input
        # the value returned from the previous validator
        yield cls.validate

    @classmethod
    def validate(cls, v):
        """
        Class method to validate the input and return a new instance with
        the hashed password.

        Parameters:
            v (str): The input string to be validated and hashed.

        Returns:
            Instance: A new instance with the hashed password.
        """
        if not isinstance(v, str):
            raise TypeError("string required")

        hashed_password = get_password_hash(v)

        return cls(hashed_password)
