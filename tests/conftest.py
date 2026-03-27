import pytest
import requests
import sphinx
from sphinx.application import Sphinx

# try to import the old testing path helper; keep it available for older Sphinx
try:
    from sphinx.testing.path import path  # type: ignore
except Exception:
    path = None

from pathlib import Path


pytest_plugins = "sphinx.testing.fixtures"


@pytest.fixture(autouse=True)
def set_rtd_env(monkeypatch):
    monkeypatch.setenv("READTHEDOCS_VERSION_NAME", "17")
    monkeypatch.setenv("READTHEDOCS", "True")
    monkeypatch.setenv("GITHUB_EVENT_NAME", "pull_request")

    # monkeypatch the GitHub API request used by the extension
    def fake_get(url, *args, **kwargs):
        class FakeResponse:
            status_code = requests.codes.ok
            text = (
                '[{"status":"modified","filename":"tests/roots/test-basic/test.rst"}]'
            )

            def json(self_inner):
                return [
                    {
                        "status": "modified",
                        "filename": "tests/roots/test-basic/test.rst",
                    },
                    {
                        "status": "added",
                        "filename": "tests/roots/test-basic/new_page.rst",
                    },
                ]

        return FakeResponse()

    monkeypatch.setattr(requests, "get", fake_get)


@pytest.fixture(scope="session")
def rootdir():
    # use sphinx.testing.path if availible (removed in Sphinx 9, else use pathlib, which fails with older Sphinx versions)
    if path is not None:
        return path(__file__).parent.abspath() / "roots"
    if Path is not None:
        return Path(__file__).parent.resolve() / "roots"
    # last resort
    return Path(__file__).parent.resolve() / "roots"


@pytest.fixture()
def content(app):
    app.build()
    yield app


def pytest_configure(config):
    config.addinivalue_line("markers", "sphinx")
