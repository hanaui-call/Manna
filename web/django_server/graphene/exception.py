class LogicalException(Exception):
    def __init__(self, message):
        super(LogicalException, self).__init__(message)
        self.message = message


class PermissionException(LogicalException):
    def __init__(self, message=""):
        super(PermissionException, self).__init__(f"permission denied: {message}")
