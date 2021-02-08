from io import BytesIO
from pathlib import Path

from ips_client.data_models import ServiceType, OutputType
from ips_client.ips_instance import IPSInstance


class TestCustomLabels:
    """
    Test different formats to provide custom_labels: as JSON string, file, BytesIO, or JobLabels object.
    """

    def test_labels_of_result_equal_custom_labels_from_str(self, ips_url, test_image):

        # GIVEN the labels of an anonymized image
        ips = IPSInstance(service=ServiceType.blur, out_type=OutputType.images, ips_url=ips_url)
        labels = ips.start_job(file=test_image).wait_until_finished().get_labels()
        assert len(labels.faces) == 1

        # WHEN these labels are used again as custom_labels
        custom_labels = labels.json()
        test_image.seek(0)
        new_labels = ips.start_job(test_image, custom_labels=custom_labels).wait_until_finished().get_labels()

        # THEN the labels of the result are the same as the custom labels
        assert new_labels == labels

    def test_labels_of_result_equal_custom_labels_from_object(self, ips_url, test_image):

        # GIVEN the labels of an anonymized image
        ips = IPSInstance(service=ServiceType.blur, out_type=OutputType.images, ips_url=ips_url)
        labels = ips.start_job(file=test_image).wait_until_finished().get_labels()
        assert len(labels.faces) == 1

        # WHEN these labels are used again as custom_labels
        test_image.seek(0)
        new_labels = ips.start_job(test_image, custom_labels=labels).wait_until_finished().get_labels()

        # THEN the labels of the result are the same as the custom labels
        assert new_labels == labels

    def test_labels_of_result_equal_custom_labels_from_file(self, ips_url, test_image):

        # GIVEN the labels of an anonymized image
        ips = IPSInstance(service=ServiceType.blur, out_type=OutputType.images, ips_url=ips_url)
        labels = ips.start_job(file=test_image).wait_until_finished().get_labels()
        assert len(labels.faces) == 1

        # WHEN these labels are used again as custom_labels
        test_image.seek(0)
        with open(str(Path(__file__).parent.joinpath('obama.json')), 'rb') as f:
            new_labels = ips.start_job(test_image, custom_labels=f).wait_until_finished().get_labels()

        # THEN the labels of the result are the same as the custom labels
        assert new_labels == labels

    def test_labels_of_result_equal_custom_labels_from_mem_file(self, ips_url, test_image):

        # GIVEN the labels of an anonymized image
        ips = IPSInstance(service=ServiceType.blur, out_type=OutputType.images, ips_url=ips_url)
        labels = ips.start_job(file=test_image).wait_until_finished().get_labels()
        assert len(labels.faces) == 1

        # WHEN these labels are used again as custom_labels
        custom_labels = BytesIO(labels.json().encode())
        test_image.seek(0)
        new_labels = ips.start_job(test_image, custom_labels=custom_labels).wait_until_finished().get_labels()

        # THEN the labels of the result are the same as the custom labels
        assert new_labels == labels
