import os
from functools import wraps
from typing import Any, Dict

from docutils import nodes
from sphinx import addnodes
from sphinx.application import Sphinx
from sphinx.application import logger
from sphinx.directives.other import TocTree

class PrintTraceback:
    def __call__(self, func):
        def wrapper_func(*args, **kwargs):
            with self:
                return func(*args, **kwargs)
        return wrapper_func
    def __enter__(self): pass
    def __exit__(self, exc_type, exc_val, tb):
        if exc_type == None: return True
        try: from rich import print
        except: pass
        import traceback
        print(f"\n{traceback.format_exc()}\n{exc_type.__name__}: {str(exc_val)}")

def NoWarnings(func):
    @wraps(func)
    def wrapped(self, *args, **kwargs):
        stream = self.state.document.reporter.stream
        self.state.document.reporter.stream = None
        ret = func(self, *args, **kwargs)
        self.state.document.reporter.stream = stream
        ret = list(filter(lambda node: not isinstance(node, nodes.system_message), ret))
        # print(ret)
        return ret
    return wrapped
    

class NoWarningsToctree(TocTree):
    @NoWarnings
    def run(self):
        return super().run()
    
    @NoWarnings
    def parse_content(self, toctree: addnodes.toctree):
        return super().parse_content(toctree)

    # def run(*args, **kwargs): return []
    # def parse_content(*args, **kwargs): return []


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

    print(res)

    if res.status_code != requests.codes.ok:
        return

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
        # app.srcdir
    else:
        inject_location = app.config.delta_inject_location
        
    for file_context in res.json():
        status: str = file_context["status"]
        filename: str = file_context["filename"]

        print(status, filename)

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
        print("adding")
        changes_rst += f"   {rel_path}\n"

    changes_rst += "\n\n.. todolist::\n"


    print(changes_rst)
    inject_location = os.path.join(app.srcdir, inject_location)
    with open(inject_location, "a") as f:
        print(inject_location)
        f.write(changes_rst)

CONFIG = {}
CONFIG["html_context"] = {}
CONFIG["html_context"]["github_version"] = "commit..."
CONFIG["html_context"]['github_user'] = "wpilibsuite"
CONFIG["html_context"]['github_repo'] = "frc-docs"
CONFIG["html_context"]['current_version'] = "1453"

@PrintTraceback()
def config_inited(app: Sphinx, config: Dict[str, Any]):
    if on_rtd() and on_pr(config["html_context"]):
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
