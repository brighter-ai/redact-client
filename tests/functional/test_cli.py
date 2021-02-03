import subprocess


class TestCLI:

    def test_entry_point_package(self, ips_client_venv):

        # GIVEN a venv with 'ips_client' package installed
        # WHEN the package is executed
        run_output = subprocess.check_output(['python', '-m', 'ips_client'], encoding='utf8')

        # THEN it shows a usage message
        assert "Usage: ips_client" in run_output

    def test_entry_point_for_file(self, ips_client_venv):

        # GIVEN a venv with 'ips_client' package installed
        # WHEN the 'ips_anon_file' script is executed
        run_output = subprocess.check_output(['ips_anon_file', '--help'], encoding='utf8')

        # THEN it shows a usage message
        assert 'Usage: ips_anon_file [OPTIONS] FILE_PATH' in run_output

    def test_entry_point_for_folder(self, ips_client_venv):

        # GIVEN a venv with 'ips_client' package installed
        # WHEN the 'ips_anon_folder' script is executed
        run_output = subprocess.check_output(['ips_anon_folder', '--help'], encoding='utf8')

        # THEN it shows a usage message
        assert 'Usage: ips_anon_folder [OPTIONS] IN_DIR' in run_output
