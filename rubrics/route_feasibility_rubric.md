# Route Feasibility Rubric

Each route is scored from 0 to 5 on each dimension.

## 1. Novelty Potential

5: clear gap compared with recent literature.

3: potentially novel but requires stronger positioning.

1: likely incremental or already well studied.

## 2. Literature Support

5: enough literature to support motivation, baseline, and modeling.

3: some literature exists, but evidence is incomplete.

1: literature base is too thin.

## 3. Modeling Clarity

5: minimal model is clear and defensible.

3: model is plausible but still vague.

1: model is unclear or hard to justify.

## 4. Simulation Feasibility

5: simulation can be built with available tools and reasonable effort.

3: simulation is possible but needs significant engineering.

1: simulation requires unavailable data, tools, or infrastructure.

## 5. Baseline Availability

5: clear baselines exist.

3: baselines can be constructed but need interpretation.

1: no obvious baseline.

## 6. Expected Evidence Clarity

5: expected figures, tables, proofs, or simulations are clear.

3: evidence may be possible but not yet crisp.

1: unclear what would count as convincing evidence.

## 7. Fit with Low-Altitude Communication

5: directly addresses a low-altitude communication problem.

3: related but needs better framing.

1: only loosely related.

## 8. Fit with Prior Work

5: strongly fits prior work on uncertainty, safety boundaries, broadcast cycles, UAV networks, graph models, reinforcement learning, or planning.

3: partial fit.

1: weak fit.

## 9. Source Quality

5: core motivation and assumptions are supported by high-quality academic or practical sources.

3: some high-quality support exists, but important assumptions still rely on medium-confidence sources.

1: route mostly relies on low-tier papers, single-paper claims, or unsupported academic fashion.

## 10. Practical Grounding

5: route is tied to standards, policy, deployed systems, planned systems, or concrete industrial constraints.

3: practical connection is plausible but needs more evidence.

1: deployment path is unclear or mostly speculative.

## Decision Rule

Recommend creating a Level 1 implementation repository only if:

- no critical dimension scores below 3;
- the route has a clear research question;
- at least 10 relevant candidate papers exist;
- high-quality and practical sources support the core assumptions;
- baselines and expected evidence are identifiable;
- human review approves the route.
