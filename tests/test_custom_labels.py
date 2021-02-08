import pytest

from io import BytesIO

from ips_client.data_models import ServiceType, OutputType, JobLabels
from ips_client.ips_instance import IPSInstance


@pytest.fixture(scope='module')
def ips(ips_url) -> IPSInstance:
    return IPSInstance(service=ServiceType.blur, out_type=OutputType.images, ips_url=ips_url)


@pytest.fixture(scope='module')  # Re-use the initial labels for every test
def test_labels(ips, test_image) -> JobLabels:
    test_image.seek(0)
    job = ips.start_job(file=test_image)
    labels = job.wait_until_finished().get_labels()
    assert len(labels.faces) == 1
    return labels


@pytest.mark.timeout(10)
class TestCustomLabels:
    """
    Test different formats to provide custom_labels: as JSON string, file, BytesIO, or JobLabels object.
    """

    def test_labels_of_result_equal_custom_labels_from_str(self, ips, test_image, test_labels):

        # GIVEN the labels of an anonymized image
        # WHEN the labels (as string) are used again as custom_labels
        custom_labels = test_labels.json()
        test_image.seek(0)
        new_labels = ips.start_job(test_image, custom_labels=custom_labels).wait_until_finished().get_labels()

        # THEN the labels of the result are the same as the custom labels
        assert new_labels == test_labels

    def test_labels_of_result_equal_custom_labels_from_object(self, ips, test_image, test_labels):

        # GIVEN the labels of an anonymized image
        # WHEN these labels (as JobLabels object) are used again as custom_labels
        test_image.seek(0)
        new_labels = ips.start_job(test_image, custom_labels=test_labels).wait_until_finished().get_labels()

        # THEN the labels of the result are the same as the custom labels
        assert new_labels == test_labels

    def test_labels_of_result_equal_custom_labels_from_file(self, ips, test_image, test_labels, tmp_path):

        # GIVEN the labels of an anonymized image (stored in a file)
        labels_path = tmp_path.joinpath('labels.json')
        with open(str(labels_path), 'w') as f:
            f.write(test_labels.json())

        # WHEN these label file is used again as custom_labels
        test_image.seek(0)
        with open(str(labels_path), 'rb') as f:
            new_labels = ips.start_job(test_image, custom_labels=f).wait_until_finished().get_labels()

        # THEN the labels of the result are the same as the custom labels
        assert new_labels == test_labels

    def test_labels_of_result_equal_custom_labels_from_mem_file(self, ips, test_image, test_labels):

        # GIVEN the labels of an anonymized image
        # WHEN these labels are used again as custom_labels
        custom_labels = BytesIO(test_labels.json().encode())
        test_image.seek(0)
        new_labels = ips.start_job(test_image, custom_labels=custom_labels).wait_until_finished().get_labels()

        # THEN the labels of the result are the same as the custom labels
        assert new_labels == test_labels
