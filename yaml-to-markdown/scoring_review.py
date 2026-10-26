from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

import yaml


PROJECT_DIR = Path(__file__).resolve().parent.parent
DEFINITIONS_DIR = PROJECT_DIR / "definitions"
DOCS_DIR = PROJECT_DIR / "docs"


@dataclass(frozen=True)
class Dependency:
    dependency: str
    dependent: str
    kind: str
    threshold: int | str | None = None


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as stream:
        value = yaml.safe_load(stream)
    if not isinstance(value, dict):
        raise ValueError(f"{path}: expected a YAML mapping")
    return value


def definition_paths() -> list[Path]:
    return sorted(DEFINITIONS_DIR.glob("*.yaml"))


def calculate_max(score: dict[str, Any]) -> int:
    if isinstance(score.get("scores"), dict):
        return sum(calculate_max(child) for child in score["scores"].values())
    return sum(
        requirement.get("value", 0)
        for requirement in score.get("requirements", [])
        if isinstance(requirement, dict)
    )


def flatten_scores(scores: dict[str, Any]) -> dict[str, dict[str, Any]]:
    flattened: dict[str, dict[str, Any]] = {}

    def visit(children: dict[str, Any], parent: str | None = None) -> None:
        for key, score in children.items():
            flattened[key] = {
                "key": key,
                "parent": parent,
                "score": score,
                "max": calculate_max(score),
            }
            if isinstance(score.get("scores"), dict):
                visit(score["scores"], key)

    visit(scores)
    return flattened


def score_conditions(score: dict[str, Any]) -> Iterable[tuple[str, dict[str, Any]]]:
    prerequisites = score.get("prerequisites", {})
    for condition in prerequisites.get("conditions", []) if isinstance(prerequisites, dict) else []:
        yield "prerequisite", condition
    for requirement in score.get("requirements", []) or []:
        if isinstance(requirement, dict):
            for condition in requirement.get("conditions", []) or []:
                yield "condition", condition


def dependencies(definition: dict[str, Any], include_structure: bool = False) -> set[Dependency]:
    flat = flatten_scores(definition.get("scores", {}))
    result: set[Dependency] = set()
    for key, item in flat.items():
        parent = item["parent"]
        if include_structure and parent:
            result.add(Dependency(key, parent, "contains"))
        for kind, condition in score_conditions(item["score"]):
            result.add(Dependency(condition.get("key", ""), key, kind, condition.get("value")))
    return result


def validate_definition(definition: dict[str, Any], source: str = "definition") -> list[str]:
    errors: list[str] = []
    scores = definition.get("scores")
    if not isinstance(scores, dict) or not scores:
        return [f"{source}: top-level 'scores' must be a non-empty mapping"]

    flat: dict[str, dict[str, Any]] = {}

    def visit(children: dict[str, Any], ancestors: tuple[str, ...] = ()) -> None:
        for key, score in children.items():
            location = ".".join((*ancestors, key))
            if key in flat:
                errors.append(f"{source}: duplicate score key '{key}' at {location}")
            if not isinstance(score, dict):
                errors.append(f"{source}: score '{location}' must be a mapping")
                continue
            flat[key] = {"score": score, "location": location, "max": calculate_max(score)}
            nested = score.get("scores")
            requirements = score.get("requirements")
            if bool(nested) == bool(requirements):
                errors.append(f"{source}: score '{key}' must have exactly one of 'scores' or 'requirements'")
            if nested is not None:
                if not isinstance(nested, dict) or not nested:
                    errors.append(f"{source}: parent score '{key}' must contain nested scores")
                else:
                    visit(nested, (*ancestors, key))
            if requirements is not None:
                if not isinstance(requirements, list) or not requirements:
                    errors.append(f"{source}: leaf score '{key}' must contain requirements")
                    continue
                for index, requirement in enumerate(requirements, 1):
                    prefix = f"{source}: score '{key}' requirement {index}"
                    if not isinstance(requirement, dict):
                        errors.append(f"{prefix} must be a mapping")
                        continue
                    if not isinstance(requirement.get("description"), str) or not requirement["description"].strip():
                        errors.append(f"{prefix} must have a description")
                    value = requirement.get("value")
                    if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
                        errors.append(f"{prefix} must have a positive integer value")
                    if not any(field in requirement for field in ("query", "resolvable", "conditions")):
                        errors.append(f"{prefix} has no query, resolvability check, or conditions")
                    resolvable = requirement.get("resolvable")
                    if resolvable is not None and resolvable != "self":
                        if not isinstance(resolvable, dict):
                            errors.append(f"{prefix} has an invalid resolvability check")
                        elif not isinstance(resolvable.get("query"), str) or not isinstance(resolvable.get("variable"), str):
                            errors.append(f"{prefix} resolvability check requires string 'query' and 'variable' fields")

    visit(scores)

    for key, item in flat.items():
        for kind, condition in score_conditions(item["score"]):
            prefix = f"{source}: score '{key}' {kind}"
            if not isinstance(condition, dict):
                errors.append(f"{prefix} must be a mapping")
                continue
            target = condition.get("key")
            if target not in flat:
                errors.append(f"{prefix} references missing score '{target}'")
                continue
            threshold = condition.get("value")
            if threshold != "max":
                if not isinstance(threshold, int) or isinstance(threshold, bool) or threshold < 0:
                    errors.append(f"{prefix} has invalid threshold {threshold!r}")
                elif threshold > flat[target]["max"]:
                    errors.append(
                        f"{prefix} threshold {threshold} exceeds '{target}' maximum {flat[target]['max']}"
                    )

    graph: dict[str, set[str]] = {key: set() for key in flat}
    for edge in dependencies(definition, include_structure=True):
        if edge.dependency in graph and edge.dependent in graph:
            graph[edge.dependent].add(edge.dependency)

    visiting: list[str] = []
    visited: set[str] = set()

    def find_cycle(node: str) -> None:
        if node in visiting:
            cycle = visiting[visiting.index(node):] + [node]
            message = f"{source}: circular dependency: {' -> '.join(cycle)}"
            if message not in errors:
                errors.append(message)
            return
        if node in visited:
            return
        visiting.append(node)
        for dependency in graph[node]:
            find_cycle(dependency)
        visiting.pop()
        visited.add(node)

    for key in graph:
        find_cycle(key)
    return errors


def condition_text(condition: dict[str, Any]) -> str:
    value = condition.get("value")
    return f"{condition.get('key', '?')} = maximum" if value == "max" else f"{condition.get('key', '?')} ≥ {value}"


def render_rules(definition: dict[str, Any], source_name: str) -> str:
    flat = flatten_scores(definition["scores"])
    lines = [
        f"# {definition.get('title', source_name.title())}",
        "",
        f"<!-- Generated from definitions/{source_name}; do not edit directly. -->",
        "",
        definition.get("description", "").strip(),
        "",
        f"Definition version: `{definition.get('version', 'unknown')}`",
        "",
        "## Score summary",
        "",
        "| Score | Description | Maximum | Depends on |",
        "|---|---|---:|---|",
    ]
    for key, item in flat.items():
        score = item["score"]
        depends_on = sorted({condition.get("key", "?") for _, condition in score_conditions(score)})
        lines.append(
            f"| {key.upper()} | {score.get('description', '')} | {item['max']} | {', '.join(k.upper() for k in depends_on) or '—'} |"
        )

    def render_children(children: dict[str, Any], level: int = 2) -> None:
        for key, score in children.items():
            lines.extend(["", f"{'#' * level} {key.upper()} — {score.get('title', key.upper())}", ""])
            lines.extend([score.get("description", ""), "", f"Maximum score: **{calculate_max(score)}**"])
            prerequisites = score.get("prerequisites", {}).get("conditions", [])
            if prerequisites:
                lines.extend(["", "Prerequisites:", ""])
                lines.extend(f"- {condition_text(condition)}" for condition in prerequisites)
            if score.get("scores"):
                render_children(score["scores"], min(level + 1, 6))
                continue
            lines.extend(["", "Requirements:", ""])
            for index, requirement in enumerate(score.get("requirements", []), 1):
                lines.append(f"{index}. **{requirement['description']}** — {requirement['value']} point(s)")
                for condition in requirement.get("conditions", []):
                    lines.append(f"   - Condition: {condition_text(condition)}")
                if requirement.get("resolvable") == "self":
                    lines.append("   - The resource IRI must resolve")
                elif isinstance(requirement.get("resolvable"), dict):
                    resolvable = requirement["resolvable"]
                    lines.append(f"   - Every `{resolvable.get('variable', '?')}` result must resolve")
                    lines.extend(
                        [
                            "",
                            "   ```sparql",
                            *[f"   {line.rstrip()}" for line in resolvable.get("query", "").rstrip().splitlines()],
                            "   ```",
                        ]
                    )
                if requirement.get("query"):
                    lines.extend(
                        [
                            "",
                            "   ```sparql",
                            *[f"   {line.rstrip()}" for line in requirement["query"].rstrip().splitlines()],
                            "   ```",
                        ]
                    )

    render_children(definition["scores"])
    return "\n".join(lines).rstrip() + "\n"


def mermaid_id(key: str) -> str:
    return "score_" + re.sub(r"[^A-Za-z0-9_]", "_", key)


def render_dependencies(definition: dict[str, Any], source_name: str) -> str:
    flat = flatten_scores(definition["scores"])
    edges = sorted(dependencies(definition), key=lambda edge: (edge.dependency, edge.dependent, edge.kind))
    lines = [
        f"# {definition.get('title', source_name.title())} dependencies",
        "",
        f"<!-- Generated from definitions/{source_name}; do not edit directly. -->",
        "",
        "Arrows point from the score being depended upon to the score whose evaluation it affects.",
        "",
        "```mermaid",
        "flowchart LR",
    ]
    involved = {edge.dependency for edge in edges} | {edge.dependent for edge in edges}
    for key in sorted(involved):
        if key in flat:
            label = f"{key.upper()} · max {flat[key]['max']}"
            lines.append(f'    {mermaid_id(key)}["{label}"]')
    for edge in edges:
        if edge.dependency in flat and edge.dependent in flat:
            threshold = "max" if edge.threshold == "max" else str(edge.threshold)
            label = f"{edge.kind}: {threshold}"
            lines.append(f'    {mermaid_id(edge.dependency)} -->|"{label}"| {mermaid_id(edge.dependent)}')
    if not edges:
        lines.append('    no_dependencies["No score dependencies"]')
    lines.extend(["```", ""])
    return "\n".join(lines)


def generated_documents() -> dict[Path, str]:
    documents: dict[Path, str] = {}
    index = [
        "# Scoring definition documentation",
        "",
        "These files are generated from the YAML scoring definitions. Regenerate them with `uv run --project yaml-to-markdown python yaml-to-markdown/main.py generate`.",
        "",
        "- [Scoring review workflow](scoring-review-workflow.md)",
    ]
    for path in definition_paths():
        definition = load_yaml(path)
        stem = path.stem
        documents[DOCS_DIR / f"{stem}-scoring.md"] = render_rules(definition, path.name)
        documents[DOCS_DIR / f"{stem}-dependencies.md"] = render_dependencies(definition, path.name)
        index.extend(
            [
                f"- [{definition.get('title', stem.upper())}]({stem}-scoring.md)",
                f"- [{definition.get('title', stem.upper())} dependencies]({stem}-dependencies.md)",
            ]
        )
    documents[DOCS_DIR / "README.md"] = "\n".join(index) + "\n"
    return documents


def requirement_signature(requirement: dict[str, Any]) -> str:
    return json.dumps(requirement, sort_keys=True, ensure_ascii=False)


def transitive_dependents(keys: set[str], edges: set[Dependency]) -> dict[str, set[str]]:
    direct: dict[str, set[str]] = defaultdict(set)
    for edge in edges:
        direct[edge.dependency].add(edge.dependent)
    result: dict[str, set[str]] = {}
    for key in keys:
        found: set[str] = set()
        pending = list(direct[key])
        while pending:
            dependent = pending.pop()
            if dependent not in found:
                found.add(dependent)
                pending.extend(direct[dependent])
        result[key] = found
    return result


def render_impact(current: dict[str, Any], base: dict[str, Any], name: str) -> str:
    current_flat = flatten_scores(current["scores"])
    base_flat = flatten_scores(base["scores"])
    current_edges = dependencies(current)
    base_edges = dependencies(base)
    added_scores = sorted(current_flat.keys() - base_flat.keys())
    removed_scores = sorted(base_flat.keys() - current_flat.keys())
    common = current_flat.keys() & base_flat.keys()
    max_changes = sorted(
        (key, base_flat[key]["max"], current_flat[key]["max"])
        for key in common
        if base_flat[key]["max"] != current_flat[key]["max"]
    )
    requirement_changes: list[tuple[str, list[str], list[str], list[str]]] = []
    changed_keys = set(added_scores) | set(removed_scores) | {key for key, _, _ in max_changes}
    for key in sorted(common):
        before = base_flat[key]["score"].get("requirements", [])
        after = current_flat[key]["score"].get("requirements", [])
        if [requirement_signature(item) for item in before] != [requirement_signature(item) for item in after]:
            before_by_description = {item.get("description", f"requirement {index}"): item for index, item in enumerate(before, 1)}
            after_by_description = {item.get("description", f"requirement {index}"): item for index, item in enumerate(after, 1)}
            added = sorted(after_by_description.keys() - before_by_description.keys())
            removed = sorted(before_by_description.keys() - after_by_description.keys())
            modified = sorted(
                description
                for description in before_by_description.keys() & after_by_description.keys()
                if requirement_signature(before_by_description[description])
                != requirement_signature(after_by_description[description])
            )
            requirement_changes.append((key, added, removed, modified))
            changed_keys.add(key)
    added_edges = current_edges - base_edges
    removed_edges = base_edges - current_edges
    changed_keys |= {edge.dependent for edge in added_edges | removed_edges}
    affected = transitive_dependents(changed_keys, current_edges | base_edges)

    lines = [f"## {name.upper()} scoring impact", ""]
    if not any((added_scores, removed_scores, max_changes, requirement_changes, added_edges, removed_edges)):
        return "\n".join(lines + ["No scoring-definition changes detected.", ""])
    if added_scores:
        lines.append(f"- Scores added: {', '.join(key.upper() for key in added_scores)}")
    if removed_scores:
        lines.append(f"- Scores removed: {', '.join(key.upper() for key in removed_scores)}")
    if requirement_changes:
        lines.extend(
            [
                "",
                "| Score | Requirements added | Removed | Modified |",
                "|---|---:|---:|---:|",
                *[
                    f"| {key.upper()} | {len(added)} | {len(removed)} | {len(modified)} |"
                    for key, added, removed, modified in requirement_changes
                ],
            ]
        )
        for key, added, removed, modified in requirement_changes:
            for label, descriptions in (("Added", added), ("Removed", removed), ("Modified", modified)):
                if descriptions:
                    lines.extend(["", f"- {key.upper()} {label.lower()}: " + "; ".join(descriptions)])
    if max_changes:
        lines.extend(["", "| Score | Previous maximum | Proposed maximum |", "|---|---:|---:|"])
        lines.extend(f"| {key.upper()} | {before} | {after} |" for key, before, after in max_changes)
    if added_edges or removed_edges:
        lines.extend(["", "Dependency changes:", ""])
        lines.extend(
            f"- Added: {edge.dependency.upper()} → {edge.dependent.upper()} ({edge.kind}, {edge.threshold})"
            for edge in sorted(added_edges, key=repr)
        )
        lines.extend(
            f"- Removed: {edge.dependency.upper()} → {edge.dependent.upper()} ({edge.kind}, {edge.threshold})"
            for edge in sorted(removed_edges, key=repr)
        )
    affected_lines = [
        f"- {key.upper()} → {', '.join(item.upper() for item in sorted(values))}"
        for key, values in sorted(affected.items())
        if values
    ]
    if affected_lines:
        lines.extend(["", "Transitively affected scores:", "", *affected_lines])
    lines.append("")
    return "\n".join(lines)


def load_from_git(ref: str, relative_path: Path) -> dict[str, Any]:
    result = subprocess.run(
        ["git", "show", f"{ref}:{relative_path.as_posix()}"],
        cwd=PROJECT_DIR,
        check=True,
        capture_output=True,
        text=True,
    )
    value = yaml.safe_load(result.stdout)
    if not isinstance(value, dict):
        raise ValueError(f"{ref}:{relative_path}: expected a YAML mapping")
    return value


def command_validate() -> int:
    errors: list[str] = []
    for path in definition_paths():
        errors.extend(validate_definition(load_yaml(path), str(path.relative_to(PROJECT_DIR))))
    if errors:
        print("Scoring definitions are invalid:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print(f"Validated {len(definition_paths())} scoring definitions")
    return 0


def command_generate(check: bool) -> int:
    documents = generated_documents()
    stale: list[Path] = []
    for path, content in documents.items():
        if check:
            if not path.exists() or path.read_text(encoding="utf-8") != content:
                stale.append(path)
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
    if stale:
        print("Generated scoring documentation is stale:", file=sys.stderr)
        for path in stale:
            print(f"- {path.relative_to(PROJECT_DIR)}", file=sys.stderr)
        return 1
    print(("Checked" if check else "Generated") + f" {len(documents)} documentation files")
    return 0


def command_impact(base_ref: str, output: Path | None) -> int:
    sections = ["# Scoring definition impact report", ""]
    for path in definition_paths():
        sections.append(render_impact(load_yaml(path), load_from_git(base_ref, path.relative_to(PROJECT_DIR)), path.stem))
    report = "\n".join(sections).rstrip() + "\n"
    if output:
        output.write_text(report, encoding="utf-8")
    print(report, end="")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Review and document FAIR/CARE scoring definitions")
    subparsers = parser.add_subparsers(dest="command")
    generate = subparsers.add_parser("generate", help="generate rule and dependency documentation")
    generate.add_argument("--check", action="store_true", help="fail when generated files are stale")
    subparsers.add_parser("validate", help="validate definition structure and dependencies")
    impact = subparsers.add_parser("impact", help="compare definitions with a Git revision")
    impact.add_argument("--base-ref", required=True, help="Git revision containing the base definitions")
    impact.add_argument("--output", type=Path, help="also write the Markdown report to this path")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    command = args.command or "generate"
    if command == "validate":
        return command_validate()
    if command == "impact":
        return command_impact(args.base_ref, args.output)
    return command_generate(getattr(args, "check", False))
