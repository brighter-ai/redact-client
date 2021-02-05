from io import BytesIO

from ips_client.data_models import ServiceType, OutputType


class TestIPSRequests:

    def test_upload_from_disk(self, ips_requests, test_image):
        # GIVEN an IPS instance and a test image
        # WHEN the image comes from disk
        # THEN it can be posted without error
        ips_requests.post_job(file=test_image, service=ServiceType.blur, out_type=OutputType.images)

    def test_upload_from_memory(self, ips_requests, test_image):
        # GIVEN an IPS instance and a test image
        # WHEN the image comes from memory
        img = BytesIO(test_image.read())
        # THEN it can be posted without error
        ips_requests.post_job(file=img, service=ServiceType.blur, out_type=OutputType.images, file_name='in-memory.jpg')
