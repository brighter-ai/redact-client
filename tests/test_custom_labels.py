from io import BytesIO

from ips_client.data_models import ServiceType, OutputType
from ips_client.ips_instance import IPSInstance


class TestCustomLabels:

    def test_labels_of_result_equal_custom_labels(self, ips_url, test_image):

        # GIVEN the labels of an anonymized image
        ips = IPSInstance(service=ServiceType.blur, out_type=OutputType.images, ips_url=ips_url)
        labels = ips.start_job(file=test_image).wait_until_finished().get_labels()
        assert len(labels.faces) == 1

        # WHEN these labels are used again as custom_labels
        custom_labels = BytesIO(labels.json().encode('utf8'))
        test_image.seek(0)
        labels_2 = ips.start_job(test_image, custom_labels=custom_labels).wait_until_finished().get_labels()

        # THEN the labels of the result are the same as the custom labels
        assert labels_2 == labels
