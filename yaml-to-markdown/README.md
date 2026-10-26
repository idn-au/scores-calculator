# Scoring definition review tools

This utility keeps the YAML files in [`/definitions`](/definitions) as the scoring source of truth while making changes easier to review. It provides:

- generated rule documentation and Mermaid dependency diagrams under [`/docs`](/docs)
- structural and dependency validation
- base-versus-branch impact reports showing changed requirements, maxima, dependencies, and transitively affected scores

The validator and impact report analyse rule structure; they do not attempt to infer relationships between arbitrary SPARQL queries. In particular, they cannot prove that a calculated maximum is attainable when requirements overlap or exclude one another. Representative RDF scenario tests are the intended next layer for demonstrating actual before-and-after scoring outcomes.

## Install & Run
To install the project (requires uv), run:

```bash
uv sync
```

Generate documentation:

```bash
uv run --project yaml-to-markdown python yaml-to-markdown/main.py generate
```

Validate the definitions:

```bash
uv run --project yaml-to-markdown python yaml-to-markdown/main.py validate
```

Check that committed documentation is current:

```bash
uv run --project yaml-to-markdown python yaml-to-markdown/main.py generate --check
```

Compare the working definitions with another Git revision:

```bash
uv run --project yaml-to-markdown python yaml-to-markdown/main.py impact --base-ref origin/main
```

Run the tests:

```bash
uv run --project yaml-to-markdown python -m unittest discover -s yaml-to-markdown/tests
```
