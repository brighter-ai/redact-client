import time
import uuid
from contextlib import contextmanager
from multiprocessing import Process
from typing import Optional

import uvicorn
from fastapi import FastAPI, Request, Response

from redact.v4 import JobArguments, JobPostResponse


def _mock_server_main(
    expected_path: Optional[str] = None,
    expected_job_args: Optional[JobArguments] = None,
    expected_form_content: Optional[dict] = None,
):
    app = FastAPI()

    @app.post("/{path:path}")
    async def get_all_routes(request: Request):
        return await _mock_redact_request_handler(
            request=request,
            expected_path=expected_path,
            expected_job_args=expected_job_args,
            expected_form_content=expected_form_content,
        )

    uvicorn.run(app=app, port=8787)


@contextmanager
def mock_redact_server(
    expected_path: Optional[str] = None,
    expected_job_args: Optional[JobArguments] = None,
    expected_form_content: Optional[dict] = None,
):
    """
    Context manager that starts a mock Redact server (127.0.0.1:8787) which returns a 500 error when the request does
    not look as expected.
    """

    server = Process(
        target=_mock_server_main,
        args=(
            expected_path,
            expected_job_args,
            expected_form_content,
        ),
        daemon=True,
    )
    server.start()
    time.sleep(2)  # wait for server to be started
    yield
    server.terminate()
    server.join()


async def _mock_redact_request_handler(
    request: Request,
    expected_path: Optional[str] = None,
    expected_job_args: Optional[JobArguments] = None,
    expected_form_content: Optional[dict] = None,
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

    if expected_form_content is not None:
        form = await request.form()
        success = True
        for key in expected_form_content:
            if key not in form:
                success = False
                continue
            file = form[key]
            val = await file.read()
            if repr(val) != repr(expected_form_content[key]):
                raise ValueError(
                    f"Failed comparison: Expected: {expected_form_content[key]} != {val}"
                )

        if not success:
            return Response(
                status_code=500,
                content=f"Received form content {repr(form)} != expected query args {repr(expected_form_content)}",
            )

    return Response(
        status_code=200, content=JobPostResponse(output_id=uuid.uuid4()).model_dump_json()
    )
