from io import BytesIO
from matplotlib import pyplot as plt
from matplotlib.pyplot import imread

from ips_client.data_models import ServiceType, OutputType
from ips_client.ips_instance import IPSInstance


def main():

    # anonymize image
    ips = IPSInstance.create(service=ServiceType.blur, out_type=OutputType.images, ips_url='http://127.0.0.1:8787')
    with open('tests/resources/obama.jpg', 'rb') as f:
        job = ips.start_job(file=f)
    result = job.wait_until_finished().download_result()

    # show anonymized image
    img = imread(BytesIO(result.content), format='jpg')
    plt.imshow(img)
    plt.show()


if __name__ == '__main__':
    main()
