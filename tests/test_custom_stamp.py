def test_custom_lp_stamps_from_file(any_img_ips, some_image, some_custom_lp_stamp):

    # GIVEN an IPS instance
    # WHEN a job is started with custom license plate stamp
    job = any_img_ips.start_job(file=some_image, licence_plate_custom_stamp=some_custom_lp_stamp)

    # THEN it can be processed and downloaded without error
    job.wait_until_finished().download_result()
