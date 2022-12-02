import pytest

from io import BytesIO

from redact.v4 import OutputType, ServiceType


@pytest.mark.skip("unitl v4 is online")
class TestRedactRequests:
    def test_upload_from_disk(self, redact_requests, some_image):
        # GIVEN a Redact instance and a test image
        # WHEN the image comes from disk
        # THEN it can be posted without error
        redact_requests.post_job(
            file=some_image, service=ServiceType.blur, out_type=OutputType.images
        )

    def test_upload_from_memory(self, redact_requests, some_image):
        # GIVEN a Redact instance and a test image
        # WHEN the image comes from memory
        img = BytesIO(some_image.read())
        img.name = "in-mem.jpg"  # pretend to be a FileIO
        # THEN it can be posted without error by providing a name manually
        redact_requests.post_job(
            file=img, service=ServiceType.blur, out_type=OutputType.images
        )
