# class InvalidAuthorizationHeader(Exception):
#     """
#     Raised when a method was called on an websocket with a
#     WebSocketState.CONNECTING or WebSocketState.DISCONNECTED state,
#     that requires an  WebSocketState. connection.
#     """

#     def __init__(self, auth_header_pattern):
#         self.message = "Invalid "\
#             .format(auth_header_pattern)
