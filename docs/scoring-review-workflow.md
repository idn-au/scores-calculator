# Scoring review workflow

The files in `definitions/` remain the source of truth for FAIR and CARE scoring. The review tooling adds validation and generated views around those files; it does not introduce another authoring format.

## Existing tooling assessment

Before this workflow was added:

- `yaml-to-markdown/main.py` read the YAML definitions and generated nested HTML tables in `test.html`. It did not expose prerequisites, validate references, or provide a stable committed output.
- the root `README.md` contained a static rule rendering, but regeneration was not checked in CI.
- `ScoreCalculator.traverseScores` in `js/src/score.ts` calculated maxima and built the runtime dependency DAG.
- pull-request CI type-checked and built the packages, but did not validate or compare scoring definitions.

The review utility extends the existing Python generator. Its maximum and dependency calculations intentionally mirror the JavaScript calculator’s additive requirements, nested-score aggregation, prerequisites, and requirement conditions.

## Editor workflow

1. Edit `definitions/care.yaml` or `definitions/fair.yaml`.
2. Run the validator to find missing references, impossible numeric thresholds, structural errors, and circular dependencies.
3. Regenerate the rule documentation and dependency diagrams.
4. Generate an impact report against the intended base branch.
5. Review changed requirements and maxima, then follow each listed transitive dependant.
6. Add or update representative RDF scenario tests when the SPARQL behaviour changes.

Commands are documented in [`yaml-to-markdown/README.md`](../yaml-to-markdown/README.md).

## Pull-request output

CI validates the definitions, runs the review-tool tests, checks that generated documents are current, and writes a scoring-impact report to the GitHub Actions job summary. The report identifies:

- requirements added, removed, or modified
- score maximum changes, including aggregate parent scores
- dependency edges added or removed
- scores affected transitively by the changed rules

## Dependency diagrams

The generated Mermaid diagrams show semantic dependencies created by prerequisites and requirement conditions. An arrow points from the score being depended upon to the score whose evaluation it affects. Parent-child containment is shown in the rule documentation rather than the diagram so the dependency view remains readable.

## Limits of static analysis

Static validation cannot determine whether arbitrary SPARQL queries overlap, contradict one another, or make a calculated maximum unattainable. It also cannot predict score changes for real resources without representative RDF. Scenario-based before-and-after scoring is therefore complementary to this workflow and should be added for material query changes.
