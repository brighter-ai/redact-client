import pytest

from pathlib import Path


@pytest.fixture
def ips_client_venv(venv):
    """Prepare a virtual environment with 'ips_client' package installed."""
    root_path = Path(__file__).parent.parent.parent
    venv.install(pkg_name=str(root_path), upgrade=True)
    return venv
