
LIST_USERS_DESC = """
This endpoint retrieves a list of all users. It requires authentication to
access. If successful, it returns a list of user information in the response
body. If no users are found, it returns a 204 No Content status code.
"""

GET_USER_BY_USERNAME_DESC = """
This endpoint retrieves a user by their username. Authentication is required
to access this endpoint. Upon successful authentication, it returns a JSON
response containing the details of the user identified by the provided
username.
"""

CREATE_USER_DESC = """
This endpoint allows the creation of a new user. Access is restricted to super
users only. Upon successful creation, it returns a JSON response containing
the details of the newly created user.
"""

PATCH_USER_DATA_DESC = """
This endpoint allows partial updates to the data of an already registered user.
Authentication is required to access this endpoint. Upon successful
authentication, it updates the user's bio and avatar data and returns a
JSON response containing the updated user details.
"""

CHANGE_USER_PASSWORD_DESC = """
This endpoint allows changing the password of the specified user.
Authentication is required to access this endpoint. Upon successful
authentication, it changes the password of the specified user and returns
a JSON response containing the updated user details.
"""

PASSWORD_RESET_EMAIL_DESC = """
This endpoint facilitates the initiation of the password reset process by
sending an email containing a password reset token to the specified email
address.
"""
