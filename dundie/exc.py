
class SystemDefaultUserNotFound(Exception):
    """Raised when the system default user is not found."""

    def __init__(self, message="System default user not found."):
        self.message = message
        super().__init__(self.message)
