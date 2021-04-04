# sphinxext-delta

Sphinx extension to generate a page of changed articles on ReadTheDocs.

## Installation

```
python -m pip install sphinxext-delta
```

## Requirements

- Sphinx >= 2
- ReadTheDocs
- GitHub

No other environments are supported.

## Usage

Add `sphinxext.delta` to your extensions list in your `conf.py`

```
extensions = [
    sphinxext.delta,
]
```

## Options

There are 2 required and 1 optional configurations:

- `delta_doc_path`
  - REQUIRED: Relative path to your articles. IE: `source/docs`
- `delta_inject_location`
  - OPTIONAL: Relative location for the toctree to be injected. Defaults to `master_doc`.
