import pytest
from sphinx.application import Sphinx


@pytest.mark.sphinx("html", testroot="basic")
def test_simple_short(app: Sphinx):
    app.build()

    content = read_text(app)

    html = '<h1>test<a class="headerlink" href="#test"'
    changed = "PR CHANGED FILES"

    assert html in content
    assert changed in content


def read_text(app: Sphinx):
    return (app.outdir / "index.html").read_text()
