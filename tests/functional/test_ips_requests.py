from io import BytesIO

from ips_client.data_models import ServiceType, OutputType


class TestIPSRequests:

    def test_upload_from_disk(self, ips_requests, some_image):
        # GIVEN an IPS instance and a test image
        # WHEN the image comes from disk
        # THEN it can be posted without error
        ips_requests.post_job(file=some_image, service=ServiceType.blur, out_type=OutputType.images)

    def test_upload_from_memory(self, ips_requests, some_image):
        # GIVEN an IPS instance and a test image
        # WHEN the image comes from memory
        img = BytesIO(some_image.read())
        img.name = 'in-mem.jpg'  # pretend to be a FileIO
        # THEN it can be posted without error by providing a name manually
        ips_requests.post_job(file=img, service=ServiceType.blur, out_type=OutputType.images)
