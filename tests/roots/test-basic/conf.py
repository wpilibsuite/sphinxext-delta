extensions = ["sphinx.ext.todo", "sphinxext.delta"]

master_doc = "index"
exclude_patterns = ["_build"]

# removes most of the HTML
html_theme = "basic"

delta_doc_path = "tests/roots/test-basic"
delta_inject_location = "index.rst"

html_context = {
    "display_github": True,  # Integrate GitHub
    "github_user": "wpilibsuite",  # Username
    "github_repo": "sphinxext-delta",  # Repo name
    "github_version": "main",  # Version, set to main so edit on github makes PRs to main
    "conf_py_path": "/source/",  # Path in the checkout to the docs root
}
