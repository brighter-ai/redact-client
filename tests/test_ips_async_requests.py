import pytest

from io import BytesIO

from ips_client.data_models import ServiceType, OutputType


@pytest.mark.asyncio
class TestIPSAsyncRequests:

    async def test_upload_from_disk(self, ips_async, test_image):
        # GIVEN an IPS instance and a test image
        # WHEN the image comes from disk
        # THEN it can be posted without error
        await ips_async.post_job(file=test_image, service=ServiceType.blur, out_type=OutputType.images)

    async def test_upload_from_memory(self, ips_async, test_image):
        # GIVEN an IPS instance and a test image
        # WHEN the image comes from memory
        img = BytesIO(test_image.read())
        # THEN it can be posted without error
        await ips_async.post_job(file=img, service=ServiceType.blur, out_type=OutputType.images, file_name='in-memory.jpg')
