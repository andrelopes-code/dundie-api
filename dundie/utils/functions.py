from dundie.serializers import UserPatchRequest
from dundie.models import User


def apply_user_patch(user: User, patch_data: UserPatchRequest) -> None:
    """
    Updates the user object with the provided patch data.

    Args:
        user (User): The user object to be updated.
        patch_data (UserPatchRequest): The patch data containing
        attributes and their new values.
    """
    for atribute, value in patch_data:
        if value is not None:
            setattr(user, atribute, value)
