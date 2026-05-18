
"""
7777 算法服务无法访问
"""
class AdminClientService415(Exception):
    def __init__(self, message="依赖的服务无法访问", code=415):
        self.message = message
        self.code = code
        super().__init__(message)

    def __str__(self):
        return self.message