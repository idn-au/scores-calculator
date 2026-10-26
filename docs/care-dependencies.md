# CARE Score dependencies

<!-- Generated from definitions/care.yaml; do not edit directly. -->

Arrows point from the score being depended upon to the score whose evaluation it affects.

```mermaid
flowchart LR
    score_a1["A1 · max 3"]
    score_a2["A2 · max 2"]
    score_a3["A3 · max 2"]
    score_c1["C1 · max 3"]
    score_c2["C2 · max 4"]
    score_c3["C3 · max 3"]
    score_e1["E1 · max 3"]
    score_e2["E2 · max 3"]
    score_e3["E3 · max 2"]
    score_r1["R1 · max 3"]
    score_r2["R2 · max 2"]
    score_r3["R3 · max 6"]
    score_a1 -->|"prerequisite: max"| score_a2
    score_a1 -->|"condition: max"| score_e1
    score_a2 -->|"prerequisite: max"| score_a3
    score_a3 -->|"condition: max"| score_e2
    score_c1 -->|"prerequisite: max"| score_c2
    score_c2 -->|"prerequisite: max"| score_c3
    score_c3 -->|"condition: max"| score_e1
    score_c3 -->|"condition: max"| score_r3
    score_e1 -->|"prerequisite: max"| score_e2
    score_e1 -->|"prerequisite: max"| score_e3
    score_r1 -->|"prerequisite: max"| score_r2
    score_r1 -->|"prerequisite: max"| score_r3
    score_r3 -->|"prerequisite: max"| score_e3
```
