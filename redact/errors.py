from typing import Optional

from httpx import Response


class RedactConnectError(Exception):
    def __init__(self, msg: Optional[str] = None):
        super(RedactConnectError, self).__init__()
        self.msg = msg

    def __str__(self):
        return self.msg


class RedactResponseError(Exception):
    def __init__(self, response: Response, msg: Optional[str] = None):
        super().__init__()
        self.response: Response = response
        self.msg = msg

    @property
    def status_code(self) -> int:
        return self.response.status_code

    def __str__(self) -> str:
        s = str(self.response)
        if self.msg:
            s = s + " " + self.msg
        return s
