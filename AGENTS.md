# AGENTS.md

## Project Type

This is a Level 0 research-intelligence repository, not an implementation repository.

The goal is to collect literature, synthesize research directions, generate route cards, evaluate route feasibility, and decide whether a topic deserves a separate Level 1 implementation repository.

## Broad Research Target

The broad target is low-altitude communication and autonomous aerial systems.

Initial candidate directions include:

1. UAV broadcast capacity and Remote ID-like systems;
2. DTMB-based or terrestrial-broadcast-based UAV management;
3. autonomous UAV formation safety and stability boundaries;
4. dynamic directional networking for low-altitude aerial networks.

These are candidates only. Do not treat any direction as approved or novel until the evidence and rubric support it.

## Non-negotiable Literature Rules

1. Do not fabricate references.
2. Do not invent DOI, venue, author, year, dataset, standard number, or numerical result.
3. If a paper has not been read, mark it as `metadata only`.
4. If only the abstract has been read, mark it as `abstract only`.
5. If the full PDF has been parsed, mark it as `full-text parsed`.
6. Distinguish between:
   - `paper-supported`: what a paper explicitly states;
   - `inferred`: what is inferred from multiple papers;
   - `proposal`: the user's or Codex's proposed extension.
7. Do not claim a research gap unless at least three relevant papers have been compared.
8. Do not generate a route card without listing supporting literature or explicitly marking missing support.
9. Do not recommend creating a Level 1 repository unless the route passes the feasibility rubric and human review.
10. Do not write final paper claims in this repository unless they are explicitly marked as preliminary.

## Source Quality and Practicality Rules

1. Prefer high-quality sources when forming research directions:
   - top journals and conferences;
   - IEEE Transactions / ACM Transactions;
   - Nature / Science family journals;
   - recognized standards, white papers, and technical reports;
   - deployed or clearly planned industrial systems;
   - policy, regulatory, or government documents when they define real constraints.
2. Treat low-tier or weakly reviewed papers as low-confidence evidence unless independently supported.
3. Do not let a single paper's framing dominate topic synthesis.
4. Do not infer real-world deployability from academic popularity.
5. Before generating route cards, check practical context: existing systems, industrial roadmaps, standards, regulation, policy news, public deployments, and realistic performance parameters.
6. Mark purely academic concepts with unclear deployment path as `deployment uncertain`.
7. Be especially cautious with areas that may be mostly academic speculation, such as semantic communication or RIS, unless there is concrete system evidence.

## Reading Status Labels

Use these labels consistently:

- `metadata only`: only bibliographic metadata or search metadata are available.
- `abstract only`: abstract has been read, but full text has not been parsed.
- `full-text parsed`: full paper text has been processed.
- `human reviewed`: a human has checked the note.
- `uncertain metadata`: bibliographic fields may be wrong.

## Output Rules

Every topic synthesis must include:

1. evidence base;
2. known methods;
3. common assumptions;
4. limitations of existing work;
5. source quality assessment;
6. practical context from industry, policy, standards, or real systems;
7. possible research gaps;
8. candidate route cards;
9. feasibility and risk assessment.

Every generated artifact must mark unsupported or speculative parts.

## Repository Boundary

This repository should not contain large raw PDFs, datasets, checkpoints, full-text paper dumps, long experiment logs, or Level 1 implementation code.

It should contain metadata, notes, route cards, prompts, rubrics, workflow documentation, and lightweight scripts.

## Codex Behavior

Before editing files, inspect the relevant templates and rubrics.

Prefer small, verifiable changes over large rewrites.

Do not overstate novelty. Do not recommend building an implementation repository unless the corresponding route has:

1. a clear research question;
2. at least 10 relevant candidate papers;
3. identifiable gaps supported by literature comparison;
4. a minimal model;
5. possible baselines;
6. expected evidence;
7. manageable implementation risk;
8. explicit human approval.
