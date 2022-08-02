import time
import uuid
import uvicorn

from contextlib import contextmanager
from fastapi import FastAPI, Request, Response
from multiprocessing import Process
from typing import Optional

from redact import JobArguments, JobPostResponse


@contextmanager
def mock_redact_server(
    expected_path: Optional[str] = None,
    expected_job_args: Optional[JobArguments] = None,
):
    """
    Context manager that starts a mock Redact server (127.0.0.1:8787) which returns a 500 error when the request does
    not look as expected.
    """

    app = FastAPI()

    @app.post("/{path:path}")
    def get_all_routes(request: Request):
        return _mock_redact_request_handler(
            request=request,
            expected_path=expected_path,
            expected_job_args=expected_job_args,
        )

    server = Process(
        target=uvicorn.run, args=(app,), kwargs={"port": 8787}, daemon=True
    )
    server.start()
    time.sleep(2)  # wait for server to be started
    yield
    server.terminate()
    server.join()


def _mock_redact_request_handler(
    request: Request,
    expected_path: Optional[str] = None,
    expected_job_args: Optional[JobArguments] = None,
) -> Response:
    """
    Handle requests by taking a look at the requested path and the query arguments and comparing them to expected ones.
    If there is a mismatch, a 500 message with details is returned.
    """

    # path
    actual_path = request.path_params["path"]
    if expected_path and actual_path != expected_path:
        return Response(
            status_code=500,
            content=f"Accessed path {actual_path} != expected path {expected_path}",
        )

    # job_args
    actual_job_args = JobArguments.parse_obj(request.query_params)
    if expected_job_args and actual_job_args != expected_job_args:
        return Response(
            status_code=500,
            content=f"Received query args {repr(actual_job_args)} != expected query args {repr(expected_job_args)}",
        )

    return Response(
        status_code=200, content=JobPostResponse(output_id=uuid.uuid4()).json()
    )
