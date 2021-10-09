import os
from typing import Any, Dict

from sphinx.application import Sphinx
from sphinx.application import logger


def on_rtd() -> bool:
    return os.getenv("READTHEDOCS") == "True"


def on_pr(html_context: Dict[str, str]) -> bool:
    return (
        html_context["github_version"].startswith(html_context["commit"])
        or os.getenv("GITHUB_EVENT_NAME") == "pull_request"
    )


def inject_changed_files(html_context: Dict[str, str], app: Sphinx) -> None:
    import requests

    res = requests.get(
        f"https://api.github.com/repos/{html_context['github_user']}/{html_context['github_repo']}/pulls/{html_context['current_version']}/files"
    )
    if res.status_code != requests.codes.ok:
        return

    inject_rst = "".join(
        [
            ".. toctree::\n",
            "   :maxdepth: 1\n",
            "   :caption: PR CHANGED FILES\n",
            "\n",
            "   prchangedfiles",
        ]
    )

    changes_rst = "".join(
        [
            ".. toctree::\n",
            "   :maxdepth: 1\n",
            "   :caption: PR CHANGED FILES\n",
            "\n",
        ]
    )
    
    if app.config.delta_inject_location is None:
        inject_location = "index.rst"
    else:
        inject_location = app.config.delta_inject_location
    
    for file_context in res.json():
        status: str = file_context["status"]
        filename: str = file_context["filename"]

        if app.config.delta_doc_path is None:
            logger.error("Required option delta_doc_path is not set!")
        if status == "deleted":
            continue
        if not filename.startswith(app.config.delta_doc_path):
            continue
        if not filename.endswith(".rst"):
            continue
        rel_path = os.path.relpath(filename, app.config.delta_doc_path)
        if rel_path == inject_location:
            continue
        changes_rst += f"   {rel_path}\n"

    changes_rst += "\n\n.. todolist::\n"



    with open(os.join(os.dirname(inject_location), "prchangedfiles.rst"), "w") as f:
        f.write(changes_rst)
        
    with open(inject_location, "a") as f:
        f.write(inject_rst)


def config_inited(app: Sphinx, config: Dict[str, Any]):
    if on_rtd() and on_pr(config["html_context"]):
        inject_changed_files(config["html_context"], app)


def setup(app: Sphinx) -> Dict[str, Any]:
    app.connect("config-inited", config_inited)
    app.add_config_value("delta_doc_path", None, str)
    app.add_config_value("delta_inject_location", None, str)

    return {
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
