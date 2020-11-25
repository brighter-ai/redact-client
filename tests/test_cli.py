import subprocess


class TestCLI:

    def test_cli_usage_message(self, ips_client_venv):

        # GIVEN a venv with 'ips_client' package
        # WHEN the package is executed
        run_output = subprocess.check_output(['python', '-m', 'ips_client'], encoding='utf8')

        # THEN it shows a usage message
        assert "Usage: ips_client" in run_output
