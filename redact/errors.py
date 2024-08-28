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


class RedactReadTimeout(Exception):
    def __init__(self) -> None:
        super(RedactReadTimeout, self).__init__()
        self.msg = "Request timed out. The file upload may have completed successfully despite the timeout. Please check the status endpoint for a new job to confirm whether the upload was successful"

    def __str__(self):
        return self.msg
