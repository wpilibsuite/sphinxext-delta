# sphinxext-delta

Sphinx extension to generate a page of changed articles on ReadTheDocs.

## Installation

```
python -m pip install sphinxext-delta
```

## Requirements

- Sphinx >= 5
- ReadTheDocs
- GitHub

No other environments are supported.

## Usage

Add `sphinxext.delta` to your extensions list in your `conf.py`

```
extensions = [
    "sphinxext.delta",
]
```

## Options

There is 1 required and 1 optional configuration:

- `delta_doc_path`
  - REQUIRED: Relative path to your articles. IE: `source/docs`
- `delta_inject_location`
  - OPTIONAL: Relative location for the toctree to be injected. Defaults to `index.rst`.
