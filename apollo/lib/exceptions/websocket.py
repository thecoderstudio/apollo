class SendAfterConnectionClosure(Exception):
    def __init__(self, message="Can't send after connection is closed"):
        self.message = message
