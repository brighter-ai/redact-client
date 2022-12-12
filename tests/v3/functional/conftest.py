import pytest

from redact.settings import Settings
from redact.v3 import OutputType, RedactInstance, RedactJob, RedactRequests, ServiceType

settings = Settings()


@pytest.fixture
def redact_requests(redact_url, optional_api_key) -> RedactRequests:
    return RedactRequests(redact_url=redact_url, api_key=optional_api_key)


@pytest.fixture(params=[ServiceType.dnat, ServiceType.blur, ServiceType.extract])
def any_img_redact_inst(redact_url, optional_api_key, request) -> RedactInstance:
    service = request.param
    output_type = (
        OutputType.overlays if service == ServiceType.extract else OutputType.images
    )
    return RedactInstance.create(
        service=service,
        output_type=output_type,
        redact_url=redact_url,
        api_key=optional_api_key,
    )


@pytest.fixture
def job(any_img_redact_inst, some_image) -> RedactJob:
    return any_img_redact_inst.start_job(file=some_image)
