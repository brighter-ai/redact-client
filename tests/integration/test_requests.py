import pytest

from redact import RedactRequests, OutputType, ServiceType, JobArguments, Region

from integration.mock_server import mock_redact_server


@pytest.mark.parametrize(argnames='service', argvalues=[ServiceType.blur, ServiceType.dnat])
def test_proper_job_args_are_request(some_image, service: ServiceType):

    # GIVEN a Redact server
    job_args = JobArguments(region=Region.mainland_china, face=False, license_plate=False, speed_optimized=True)
    with mock_redact_server(expected_path=f'{service.value}/v3/archives', expected_job_args=job_args):

        # WHEN a job is posted
        # THEN the server receives the expected job arguments (otherwise a 500 is returned and an error thrown)
        redact_requests = RedactRequests()
        redact_requests.post_job(file=some_image,
                                 service=service,
                                 out_type=OutputType.archives,
                                 job_args=job_args)
