import pytest
from sphinx.application import Sphinx
from sphinx import version_info


@pytest.mark.sphinx("html", testroot="basic")
def test_simple_short(app: Sphinx):
    assert(True)
