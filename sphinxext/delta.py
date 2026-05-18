import os
from functools import wraps
from typing import Any, Dict

from docutils import nodes
from sphinx import addnodes
from sphinx.application import Sphinx
from sphinx.application import logger
from sphinx.directives.other import TocTree


def NoWarnings(func):
    @wraps(func)
    def wrapped(self, *args, **kwargs):
        # defensively handle reporter.stream which changed in Sphinx 8
        doc = getattr(self.state, "document", None)
        reporter = getattr(doc, "reporter", None)
        prev_stream = None
        stream_mutated = False

        if reporter is not None and hasattr(reporter, "stream"):
            try:
                prev_stream = reporter.stream
                reporter.stream = None
                stream_mutated = True
            except Exception:
                stream_mutated = False

        try:
            ret = func(self, *args, **kwargs)
            # try to filter returned iterable of nodes; if not iterable, return as-is
            try:
                filtered = [n for n in ret if not isinstance(n, nodes.system_message)]
                return filtered
            except TypeError:
                return ret
        finally:
            if stream_mutated:
                try:
                    reporter.stream = prev_stream
                except Exception:
                    pass

    return wrapped


class NoWarningsToctree(TocTree):
    @NoWarnings
    def run(self):
        return super().run()

    @NoWarnings
    def parse_content(self, toctree: addnodes.toctree):
        return super().parse_content(toctree)


def on_rtd() -> bool:
    return os.getenv("READTHEDOCS") == "True"


def on_pr() -> bool:
    return (
        os.getenv("READTHEDOCS_VERSION_TYPE") == "external"
        or os.getenv("GITHUB_EVENT_NAME") == "pull_request"
    )


def fetch_and_process_page(
    api_url: str, page: int, per_page: int, all_files: list
) -> bool:
    """Fetch the next page of files from GitHub API and return whether to continue paginating."""
    import requests

    res = requests.get(api_url, params={"page": page, "per_page": per_page})

    if res.status_code != requests.codes.ok:
        logger.error("Github API request failed (status code: %s)", res.status_code)
        return False

    page_files = res.json()
    if not page_files:
        return False

    all_files.extend(page_files)

    # Continue only if we got a full page of results
    return len(page_files) == per_page


def inject_changed_files(html_context: Dict[str, str], app: Sphinx) -> None:
    api_url = f"https://api.github.com/repos/{html_context['github_user']}/{html_context['github_repo']}/pulls/{os.environ.get('READTHEDOCS_VERSION_NAME')}/files"

    all_files = []
    page = 1
    per_page = 100  # Max items per page for GitHub API
    max_pages = 30  # Safety limit based on maximum files from Github API (3000 files)

    # Paginate through all results
    while (
        fetch_and_process_page(api_url, page, per_page, all_files) and page < max_pages
    ):
        page += 1

    changes_rst = "".join(
        [
            "\n",
            ".. nowarningstoctree::\n",
            "   :maxdepth: 1\n",
            "   :caption: PR CHANGED FILES\n",
            "\n",
        ]
    )

    if app.config.delta_inject_location is None:
        inject_location = "index.rst"
    else:
        inject_location = app.config.delta_inject_location

    for file_context in all_files:
        status: str = file_context["status"]
        filename: str = file_context["filename"]

        rel_path = os.path.relpath(filename, app.config.delta_doc_path)

        if app.config.delta_doc_path is None:
            logger.error("Required option delta_doc_path is not set!")
        if status == "removed":
            continue
        if not filename.startswith(app.config.delta_doc_path):
            continue
        if not filename.endswith(".rst"):
            continue

        if rel_path == inject_location:
            continue
        changes_rst += f"   {rel_path}\n"

    changes_rst += "\n\n.. todolist::\n"

    inject_location = os.path.join(app.srcdir, inject_location)
    with open(inject_location, "a") as f:
        f.write(changes_rst)


def config_inited(app: Sphinx, config: Dict[str, Any]):
    if on_rtd() and on_pr():
        inject_changed_files(config["html_context"], app)


def setup(app: Sphinx) -> Dict[str, Any]:
    app.connect("config-inited", config_inited)
    app.add_config_value("delta_doc_path", None, str)
    app.add_config_value("delta_inject_location", None, str)
    app.add_directive("nowarningstoctree", NoWarningsToctree)

    return {
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
