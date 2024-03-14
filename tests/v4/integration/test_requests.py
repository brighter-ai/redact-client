import pytest

from redact.errors import RedactResponseError
from redact.v4 import JobArguments, OutputType, RedactRequests, Region, ServiceType
from tests.v4.integration.mock_server import mock_redact_server

API_VERSION = "v4"


@pytest.mark.parametrize(
    argnames="service", argvalues=[ServiceType.blur, ServiceType.dnat]
)
def test_proper_job_args_are_sent_to_server(
    some_image, service: ServiceType, redact_url
):
    # GIVEN a (mocked) Redact server and a job to send there
    out_type = OutputType.archives
    job_args = JobArguments(
        region=Region.mainland_china,
        face=False,
        license_plate=False,
        speed_optimized=True,
        vehicle_recorded_data=False,
        single_frame_optimized=False,
        lp_determination_threshold=0.2,
        face_determination_threshold=0.2,
        status_webhook_url=redact_url,
    )

    with mock_redact_server(
        expected_path=f"{service.value}/{API_VERSION}/{out_type.value}",
        expected_job_args=job_args,
    ):
        # WHEN the job is posted
        # THEN the server receives the expected job arguments (otherwise a 500 is returned and an error thrown)
        redact_requests = RedactRequests()
        redact_requests.post_job(
            file=some_image,
            service=service,
            out_type=out_type,
            job_args=job_args,
        )


def test_mock_server_gives_error_on_unexpected_argument(some_image):
    # GIVEN job parameters
    service = ServiceType.blur
    out_type = OutputType.images
    expected_job_args = JobArguments(face=True)

    # AND GIVEN a (mocked) Redact server to send them to
    with mock_redact_server(
        expected_path=f"{service.value}/{API_VERSION}/{out_type.value}",
        expected_job_args=expected_job_args,
    ):
        # WHEN a different job is posted
        posted_job_args = JobArguments(face=False)
        assert expected_job_args != posted_job_args

        # THEN the server returns an error
        with pytest.raises(RedactResponseError):
            redact_requests = RedactRequests()
            redact_requests.post_job(
                file=some_image,
                service=service,
                out_type=out_type,
                job_args=posted_job_args,
            )


def test_mock_server_gives_error_on_unexpected_service(some_image):
    # GIVEN job parameters
    service = ServiceType.blur
    out_type = OutputType.images
    job_args = JobArguments(face=True)

    # AND GIVEN a (mocked) Redact server to send them to
    with mock_redact_server(
        expected_path=f"{service.value}/{API_VERSION}/{out_type.value}",
        expected_job_args=job_args,
    ):
        # WHEN the job is posted to the wrong service endpoint
        posted_service = ServiceType.dnat

        # THEN the server returns an error
        with pytest.raises(RedactResponseError):
            redact_requests = RedactRequests()
            redact_requests.post_job(
                file=some_image,
                service=posted_service,
                out_type=out_type,
                job_args=job_args,
            )


def test_mock_server_receives_headers(some_image):
    # GIVEN additional header values
    service = ServiceType.blur
    out_type = OutputType.images
    job_args = JobArguments(face=True)

    custom_headers = {"foo": "boo", "hello": "world"}

    # AND GIVEN a (mocked) Redact server to validate them
    with mock_redact_server(
        expected_path=f"{service.value}/{API_VERSION}/{out_type.value}",
        expected_headers_contain=custom_headers,
    ):
        # WHEN request is created with additional headers
        redact_requests = RedactRequests(custom_headers=custom_headers)

        # THEN the server validates the existance of the additional ehader values beeing present
        redact_requests.post_job(
            file=some_image,
            service=service,
            out_type=out_type,
            job_args=job_args,
        )
