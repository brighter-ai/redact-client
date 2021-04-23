import pytest

from redact import RedactRequests, OutputType, ServiceType, JobArguments, Region, RedactResponseError

from integration.mock_server import mock_redact_server


@pytest.mark.parametrize(argnames='service', argvalues=[ServiceType.blur, ServiceType.dnat])
def test_proper_job_args_are_sent_to_server(some_image, service: ServiceType):

    # GIVEN a (mocked) Redact server and a job to send there
    out_type = OutputType.archives
    job_args = JobArguments(region=Region.mainland_china, face=False, license_plate=False, speed_optimized=True)

    with mock_redact_server(expected_path=f'{service.value}/v3/{out_type.value}', expected_job_args=job_args):

        # WHEN the job is posted
        # THEN the server receives the expected job arguments (otherwise a 500 is returned and an error thrown)
        redact_requests = RedactRequests()
        redact_requests.post_job(file=some_image,
                                 service=service,
                                 out_type=out_type,
                                 job_args=job_args)


def test_mock_server_gives_error_on_unexpected_argument(some_image):

    # GIVEN job parameters
    service = ServiceType.blur
    out_type = OutputType.images
    job_args = JobArguments(face=True)

    # AND GIVEN a (mocked) Redact server to send them to
    with mock_redact_server(expected_path=f'{service.value}/v3/{out_type.value}', expected_job_args=job_args):

        # WHEN a different job is posted
        posted_job_args = JobArguments(face=False)
        assert job_args != posted_job_args

        # THEN the server returns an error
        with pytest.raises(RedactResponseError):
            redact_requests = RedactRequests()
            redact_requests.post_job(file=some_image,
                                     service=service,
                                     out_type=out_type,
                                     job_args=posted_job_args)


def test_mock_server_gives_error_on_unexpected_service(some_image):

    # GIVEN job parameters
    service = ServiceType.blur
    out_type = OutputType.images
    job_args = JobArguments(face=True)

    # AND GIVEN a (mocked) Redact server to send them to
    with mock_redact_server(expected_path=f'{service.value}/v3/{out_type.value}', expected_job_args=job_args):

        # WHEN the job is posted to the wrong service endpoint
        posted_service = ServiceType.dnat

        # THEN the server returns an error
        with pytest.raises(RedactResponseError):
            redact_requests = RedactRequests()
            redact_requests.post_job(file=some_image,
                                     service=posted_service,
                                     out_type=out_type,
                                     job_args=job_args)
