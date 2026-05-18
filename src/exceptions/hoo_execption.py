
class HooException(Exception):
    def __init__(self, message="异常", code=412):
        self.message = message
        self.code = code
        super().__init__(message)

    def __str__(self):
        return self.message