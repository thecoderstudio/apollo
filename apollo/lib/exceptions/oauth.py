class AuthorizationHeaderNotFound(Exception):
    """Exception raised when no authorization header is found"""

    def __init__(self):
        self.message = "No authorization header found"


class InvalidAuthorizationMethod(Exception):
    """
    Exception raised when the authorization method
    is not what was expected
    """

    def __init__(self, auth_method):
        self.message = "Wrong authorization method, expected method: {}"\
                .format(auth_method)


class InvalidAuthorizationHeader(Exception):
    """
    Raised when the authorization header is not what was expected.
    """

    def __init__(self, auth_header_pattern):
        self.message = "Invalid authorization header, expected pattern: {}"\
                .format(auth_header_pattern)
