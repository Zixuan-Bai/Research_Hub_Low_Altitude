# Low-Altitude Research Intelligence Hub: Codex Setup Plan

## 0. Purpose

This document defines a repository design and workflow for building a Codex-assisted research-intelligence hub for low-altitude communication and autonomous aerial systems.

The current stage is **not** implementation or large-scale experimentation. The goal is to first build a general repository for:

- large-scale literature search;
- local PDF ingestion and reading;
- paper note generation;
- topic synthesis;
- research-gap identification;
- route-card generation;
- route feasibility ranking;
- deciding whether a specific direction deserves a separate implementation repository.

Only after a research route becomes sufficiently clear should a separate implementation repository be created.

---

## 1. Two-Level Repository System

The overall system should use two levels of repositories.

```text
Level 0: low-altitude-research-hub
Used for direction scouting, literature management, topic synthesis, route-card generation, feasibility evaluation, and repository creation decisions.

Level 1: topic-specific implementation repositories
Used for modeling, simulation, algorithm implementation, experiments, evidence generation, and manuscript drafting for a specific approved route.
```

The Level 0 repository is the first priority. The Level 1 repositories should only be created after a route card passes the feasibility review.

Possible future Level 1 repositories include:

```text
low-altitude-broadcast-capacity/
dtmb-uav-broadcast-control/
uav-formation-safety-boundary/
dynamic-directional-networking/
remote-id-density-analysis/
```

---

## 2. Initial Research Scope

The broad target is low-altitude communication and autonomous aerial systems.

The initial candidate directions are:

1. **UAV broadcast capacity analysis / Remote ID-like broadcast systems**
   - high-density UAV broadcast;
   - Remote ID-like direct broadcast;
   - broadcast frequency versus packet reception probability;
   - hidden terminals and channel congestion;
   - safe density boundary.

2. **DTMB-based or terrestrial-broadcast-based large-scale UAV management**
   - one-to-many broadcast control;
   - command dissemination;
   - coverage and latency;
   - relationship to UTM/U-space systems;
   - comparison with cellular broadcast/multicast.

3. **Autonomous UAV formation safety and stability boundaries**
   - communication cycle, delay, packet loss, and formation stability;
   - uncertainty propagation;
   - finite-window convergence;
   - critical noise or safety boundary;
   - risk-driven broadcast/update control.

4. **Dynamic directional networking**
   - directional transmission;
   - dynamic aerial topology;
   - clustering and cluster-head coordination;
   - beam selection;
   - topology prediction;
   - interference suppression and spatial reuse.

The research hub should not assume that any of these is already the final direction. It should compare them systematically.

---

## 3. Recommended Repository Name

```text
low-altitude-research-hub/
```

---

## 4. Repository Layout

Create the following structure:

```text
low-altitude-research-hub/
├── AGENTS.md
├── README.md
├── pyproject.toml
├── .gitignore
│
├── literature/
│   ├── inbox/
│   │   ├── papers/                 # Local PDFs. Usually not committed to Git.
│   │   └── metadata_manual.yaml
│   ├── database/
│   │   ├── papers.csv              # Master metadata table.
│   │   ├── papers.bib              # BibTeX database.
│   │   └── paper_index.jsonl       # Search or embedding index metadata.
│   ├── notes/
│   │   ├── paper_notes/            # One note per paper.
│   │   ├── survey_notes/           # Topic-level notes.
│   │   └── reading_logs/
│   └── queries/
│       ├── remote_id.yaml
│       ├── dtmb_broadcast.yaml
│       ├── formation_safety.yaml
│       └── directional_networking.yaml
│
├── topics/
│   ├── remote_id_broadcast_capacity/
│   │   ├── topic_brief.md
│   │   ├── evidence_map.md
│   │   ├── open_questions.md
│   │   ├── route_cards/
│   │   └── repo_proposal.md
│   ├── dtmb_uav_control/
│   ├── formation_safety_boundary/
│   └── dynamic_directional_networking/
│
├── route_cards/
│   ├── template.md
│   ├── candidate_001_remote_id_capacity.md
│   ├── candidate_002_dtmb_control.md
│   └── candidate_003_safety_boundary.md
│
├── scripts/
│   ├── search_literature.py
│   ├── import_local_pdfs.py
│   ├── extract_pdf_metadata.py
│   ├── build_literature_index.py
│   ├── generate_paper_note.py
│   ├── cluster_topics.py
│   ├── generate_route_card.py
│   ├── rank_routes.py
│   └── create_topic_repo.py
│
├── prompts/
│   ├── literature_search.md
│   ├── paper_reading.md
│   ├── topic_synthesis.md
│   ├── route_generation.md
│   └── route_review.md
│
├── rubrics/
│   ├── paper_relevance_rubric.md
│   ├── topic_potential_rubric.md
│   ├── route_feasibility_rubric.md
│   └── paperability_rubric.md
│
└── outputs/
    ├── weekly_reports/
    ├── topic_rankings/
    ├── route_rankings/
    └── repo_creation_logs/
```

---

## 5. Repository Boundary

This repository should contain:

- metadata;
- BibTeX entries;
- paper notes;
- topic briefs;
- evidence maps;
- route cards;
- feasibility rubrics;
- workflow documentation;
- scripts for literature management and route ranking.

This repository should **not** contain:

- large raw PDFs;
- copyrighted full-text paper dumps;
- datasets;
- model checkpoints;
- large simulation logs;
- long experimental outputs.

Recommended `.gitignore` entries:

```gitignore
literature/inbox/papers/
literature/processed/full_text/
data/
datasets/
logs/
outputs/tmp/
*.pdf
*.log
__pycache__/
.venv/
.env
.DS_Store
```

---

## 6. AGENTS.md Draft

Create `AGENTS.md` with the following content:

```md
# AGENTS.md

## Project Type

This is a research-intelligence repository, not an implementation repository.

The goal is to collect literature, synthesize research directions, generate route cards, evaluate route feasibility, and decide whether a topic deserves a separate implementation repository.

## Broad Research Target

The broad target is low-altitude communication and autonomous aerial systems.

Initial candidate directions include:

1. UAV broadcast capacity analysis, including Remote ID-like systems;
2. DTMB-based or terrestrial-broadcast-based large-scale UAV management;
3. autonomous UAV formation safety and stability boundaries;
4. dynamic directional networking for low-altitude aerial networks.

## Non-negotiable Literature Rules

1. Do not fabricate references.
2. Do not invent DOI, venue, author, year, or numerical results.
3. If a paper has not been read, mark it as `metadata only`.
4. If only the abstract has been read, mark it as `abstract only`.
5. If the full PDF has been parsed, mark it as `full-text parsed`.
6. Distinguish between:
   - what the paper explicitly states;
   - what is inferred from multiple papers;
   - what is my proposed extension.
7. Do not claim a research gap unless at least three relevant papers have been compared.
8. Do not generate a route card without listing the supporting literature.
9. Do not recommend creating a new implementation repository unless the route passes the feasibility rubric.
10. Do not write final paper claims in this repository unless they are explicitly marked as preliminary.

## Output Rules

Every topic synthesis must include:

1. evidence base;
2. known methods;
3. common assumptions;
4. limitations of existing work;
5. possible research gaps;
6. candidate route cards;
7. feasibility and risk assessment.

## Reading Status Labels

Use the following labels consistently:

- `metadata only`: only title/authors/year/venue/abstract or search metadata are available.
- `abstract only`: abstract has been read, but full text has not been parsed.
- `full-text parsed`: full paper text has been processed.
- `human reviewed`: a human has checked the note.
- `uncertain metadata`: bibliographic fields may be wrong.

## Repository Boundary

This repository should not contain large raw PDFs, datasets, checkpoints, or long simulation outputs.

It should contain metadata, notes, route cards, scripts, rubrics, and research decision records.

## Codex Behavior

Before editing files, inspect the relevant templates and rubrics.

For any generated synthesis, explicitly mark unsupported or speculative parts.

Do not overstate novelty.

Do not recommend building an implementation repository unless the corresponding route has:

1. a clear research question;
2. at least 10 relevant candidate papers;
3. identifiable gaps;
4. a minimal model;
5. possible baselines;
6. expected evidence;
7. manageable implementation risk.
```

---

## 7. Paper Note Template

Create:

```text
literature/notes/paper_notes/template.md
```

Content:

```md
# Paper Note

## Metadata

- Title:
- Authors:
- Year:
- Venue:
- DOI:
- URL:
- Topic:
- Reading status: metadata only / abstract only / full-text parsed / human reviewed
- Relevance: high / medium / low

## Problem

What problem does the paper study?

## Method

What model, algorithm, system, or analysis does it propose?

## Key Assumptions

What assumptions are made?

## Evidence

What experiments, proofs, measurements, simulations, or case studies are provided?

## Limitations

What does it not solve?

## Useful For My Research

- Motivation:
- Baseline:
- Model:
- Parameter:
- Figure/table inspiration:
- Related work:

## Possible Follow-up Route

What research route could be derived from this paper?

## Reliability Notes

Which parts are directly supported by the paper, and which parts are inferred?
```

---

## 8. Topic Brief Template

Create:

```text
topics/template_topic_brief.md
```

Content:

```md
# Topic Brief

## Topic Name

## Scope

What does this topic include and exclude?

## Why It Matters for Low-Altitude Communication

Explain the relevance to low-altitude UAV communication, control, or safety.

## Literature Base

List the main papers and what each contributes.

## Existing Research Clusters

Group the literature into clusters.

Examples:
- regulation and architecture;
- communication capacity;
- interference and congestion;
- safety and reliability;
- control and management;
- simulation and measurement.

## Common Models and Assumptions

Summarize common channel models, traffic models, mobility models, network models, and control assumptions.

## Known Limitations

What is missing or weak in the existing literature?

## Possible Research Gaps

Mark each gap as:

- supported by literature;
- inferred from comparison;
- speculative.

## Candidate Route Cards

List 3–5 possible route cards.

## Feasibility Assessment

Assess modeling feasibility, simulation feasibility, baseline availability, data requirement, and expected time.

## Decision

- continue surveying;
- generate route cards;
- create implementation repository;
- pause or reject.
```

---

## 9. Evidence Map Template

Create:

```text
topics/template_evidence_map.md
```

Content:

```md
# Evidence Map

## Topic

## Evidence Table

| Claim / Observation | Supporting Papers | Evidence Type | Strength | Notes |
|---|---|---|---|---|
|  |  | theory / simulation / measurement / standard / survey | high / medium / low |  |

## Literature Clusters

### Cluster 1

- Papers:
- Main idea:
- Limitations:

### Cluster 2

- Papers:
- Main idea:
- Limitations:

## Gap Candidates

| Gap | Supporting Evidence | Risk | Possible Route |
|---|---|---|---|
|  |  |  |  |

## Unsupported or Speculative Ideas

List ideas that are interesting but not yet supported by enough literature.
```

---

## 10. Route Card Template

Create:

```text
route_cards/template.md
```

Content:

```md
# Route Card

## Route ID

## Candidate Title

## Parent Topic

## One-sentence Claim

## Core Research Question

## Why This Problem Matters

## Literature Basis

List supporting papers and what each supports.

## Gap

What is missing in the current literature?

## Proposed Angle

Describe the possible technical route.

## Minimal Model

What is the smallest mathematical or simulation model needed?

## Possible Method

Choose applicable methods:

- analytical model;
- simulation model;
- optimization;
- reinforcement learning;
- control theory;
- graph model;
- formal verification;
- network calculus;
- stochastic geometry;
- queueing;
- game theory;
- measurement study.

## Expected Evidence

What figures, tables, proofs, or simulations would make this route convincing?

## Baselines

What should be compared?

## Feasibility

- required data:
- required simulator:
- required compute:
- required domain knowledge:
- expected time:

## Risk

- novelty risk:
- modeling risk:
- experiment risk:
- writing risk:

## Paperability Score

0–5

## Decision

- keep;
- watch;
- reject;
- create implementation repository.

## Repository Proposal Needed?

yes / no
```

---

## 11. Route Feasibility Rubric

Create:

```text
rubrics/route_feasibility_rubric.md
```

Content:

```md
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

5: expected figures/tables/proofs are clear.
3: evidence may be possible but not yet crisp.
1: unclear what would count as convincing evidence.

## 7. Fit with Low-Altitude Communication

5: directly addresses a low-altitude communication problem.
3: related but needs better framing.
1: only loosely related.

## 8. Fit with Prior Work

5: strongly fits prior work on uncertainty, safety boundaries, broadcast cycles, UAV networks, or formal safety.
3: partial fit.
1: weak fit.

## Decision Rule

Recommend creating an implementation repository only if:

- total score is high;
- no critical dimension scores below 3;
- the route has a clear research question;
- at least 10 relevant candidate papers exist;
- baselines and expected evidence are identifiable.
```

---

## 12. Literature Query YAML Examples

Create:

```text
literature/queries/remote_id.yaml
```

```yaml
topic: remote_id_broadcast_capacity

seed_keywords:
  - UAV Remote ID
  - drone remote identification
  - broadcast remote ID
  - direct remote identification
  - ASTM F3411
  - drone density
  - broadcast capacity
  - wireless broadcast congestion
  - C-V2X sidelink UAV
  - ADS-B UAV scalability

databases:
  - IEEE Xplore
  - ACM Digital Library
  - arXiv
  - Google Scholar
  - Web of Science

must_extract:
  - problem setting
  - communication mode
  - broadcast frequency
  - density assumption
  - channel model
  - interference model
  - scalability limitation
  - safety implication
  - open problem

exclude:
  - pure regulation without technical model
  - consumer drone product reports
  - papers without capacity or scalability analysis
```

Create:

```text
literature/queries/dtmb_broadcast.yaml
```

```yaml
topic: dtmb_uav_control

seed_keywords:
  - DTMB
  - digital terrestrial multimedia broadcasting
  - UAV command and control
  - broadcast control channel
  - low altitude air traffic management
  - terrestrial broadcast network UAV
  - one-to-many UAV control
  - emergency broadcast UAV
  - cellular broadcast UAV control
  - multicast UAV control

must_extract:
  - broadcast architecture
  - downlink control capacity
  - latency
  - coverage
  - reliability
  - uplink feedback mechanism
  - safety fallback
  - relation to UTM or U-space
```

Create:

```text
literature/queries/formation_safety.yaml
```

```yaml
topic: formation_safety_boundary

seed_keywords:
  - UAV formation stability
  - multi-UAV formation control communication delay
  - packet loss formation control UAV
  - consensus under communication delay
  - swarm stability boundary
  - critical noise multi-agent system
  - Vicsek model noise transition
  - risk-driven broadcast UAV
  - state synchronization error propagation
  - communication-aware formation control

must_extract:
  - stability condition
  - communication model
  - delay model
  - packet loss model
  - uncertainty representation
  - safety boundary
  - proof method
  - simulation setting
  - control policy
```

Create:

```text
literature/queries/directional_networking.yaml
```

```yaml
topic: dynamic_directional_networking

seed_keywords:
  - UAV directional networking
  - FANET directional antenna
  - UAV beamforming network
  - dynamic topology UAV network
  - aerial ad hoc network directional transmission
  - UAV clustering directional communication
  - beam selection UAV swarm
  - topology prediction UAV network
  - low altitude network spatial reuse
  - directional MAC UAV

must_extract:
  - network model
  - antenna or beam model
  - topology dynamics
  - clustering method
  - routing or scheduling method
  - interference model
  - performance metrics
  - scalability
  - limitation
```

---

## 13. First Codex Task: Build the Hub Skeleton

Give Codex this task first:

```text
Read AGENTS.md.

Create the initial structure for a research-intelligence hub on low-altitude communication.

Requirements:
1. Create directories for literature metadata, topic briefs, route cards, rubrics, prompts, and outputs.
2. Create templates for paper notes, topic briefs, evidence maps, open questions, and route cards.
3. Create YAML query files for four initial topics:
   - UAV broadcast capacity and Remote ID-like systems;
   - DTMB-based large-scale UAV control;
   - autonomous formation safety and stability boundaries;
   - dynamic directional networking.
4. Create a script skeleton for importing local PDF metadata.
5. Create a script skeleton for ranking route cards.
6. Do not invent literature.
7. Do not generate final research conclusions yet.
```

---

## 14. Second Codex Task: Write Workflow Documentation

```text
Generate the first version of the research workflow documentation.

Create docs/workflow.md explaining:
1. how to add a new paper;
2. how to mark reading status;
3. how to create a paper note;
4. how to synthesize a topic;
5. how to generate a route card;
6. how to decide whether to create a separate implementation repository.

Do not make unsupported claims about any research direction.
```

---

## 15. Third Codex Task: Create the Route Feasibility Rubric

```text
Create the route feasibility rubric.

The rubric should score:
1. novelty potential;
2. literature support;
3. modeling clarity;
4. simulation feasibility;
5. baseline availability;
6. expected evidence clarity;
7. fit with low-altitude communication;
8. fit with my prior work on uncertainty, safety boundaries, broadcast cycles, and UAV networks.

Do not evaluate any route yet.
```

---

## 16. Fourth Codex Task: Import Local PDFs

After placing local PDFs under:

```text
literature/inbox/papers/
```

give Codex this task:

```text
Scan literature/inbox/papers/.

For each PDF:
1. extract title if possible;
2. extract authors and year if possible;
3. create or update a metadata entry under literature/database/papers.csv;
4. create a note stub under literature/notes/paper_notes/;
5. mark reading_status as metadata only unless the full text is parsed;
6. flag uncertain fields.

Do not infer missing metadata aggressively.
Do not fabricate DOI, venue, or year.
```

---

## 17. Fifth Codex Task: Public Literature Search

For one topic, for example Remote ID:

```text
Use literature/queries/remote_id.yaml.

Search for relevant papers on UAV Remote ID, broadcast remote identification, drone density, and broadcast capacity.

For each candidate paper, record:
1. title;
2. authors;
3. year;
4. venue;
5. DOI or URL if available;
6. why it is relevant;
7. whether it is about regulation, architecture, communication model, capacity, interference, or safety;
8. reading status.

Do not summarize full papers unless the full text is available.
Create or update literature/database/remote_id_candidates.csv.
```

---

## 18. Sixth Codex Task: Topic Synthesis

After enough candidate papers exist:

```text
Read the candidate papers and paper notes under the Remote ID topic.

Create topics/remote_id_broadcast_capacity/topic_brief.md and evidence_map.md.

The brief must include:
1. what the existing literature mainly studies;
2. what models are commonly used;
3. what assumptions are common;
4. what is missing or weak;
5. possible low-altitude communication research gaps;
6. 3–5 candidate route cards.

Mark every claim as:
- supported by literature;
- inferred from multiple papers;
- speculative proposal.

Do not overstate novelty.
Do not recommend creating an implementation repository yet.
```

---

## 19. Seventh Codex Task: Generate Route Cards

```text
Based on topics/remote_id_broadcast_capacity/topic_brief.md and evidence_map.md, generate 5 route cards.

Each route card must include:
1. core research question;
2. literature basis;
3. gap;
4. minimal model;
5. possible method;
6. expected evidence;
7. baseline;
8. feasibility;
9. risk;
10. decision recommendation.

Do not recommend creating an implementation repository unless feasibility is at least medium.
```

---

## 20. Eighth Codex Task: Repository Proposal

Only after a route is approved:

```text
Read route_cards/<approved_route_card>.md.

Create a repository proposal for this route.

The proposal must include:
1. proposed repository name;
2. research objective;
3. minimal model;
4. implementation modules;
5. experiment plan;
6. baselines;
7. metrics;
8. expected figures/tables;
9. compute requirements;
10. paper outline;
11. risks and fallback plan.

Do not create the repository yet.
```

---

## 21. When to Create a Topic-Specific Implementation Repository

Create a separate implementation repository only if the route satisfies all of the following:

```text
1. clear research question;
2. at least 10 relevant candidate papers;
3. identifiable gap supported by literature comparison;
4. minimal mathematical or simulation model;
5. available or constructible baselines;
6. clear expected evidence, such as figures, tables, proofs, or simulations;
7. manageable implementation risk;
8. plausible path to a paper within 3–6 months.
```

---

## 22. Expected Short-Term Goal

The short-term goal is not to write a paper.

The first goal is:

```text
Use 2–3 weeks to generate 10–20 candidate route cards.
Rank them.
Select 1–2 routes for deeper investigation.
Only then create implementation repositories.
```

This avoids creating many empty or weakly motivated repositories before the research direction becomes clear.

---

## 23. Recommended Human Review Points

Human review is required at the following points:

1. after literature candidates are collected;
2. after paper notes are generated;
3. before a topic brief is treated as reliable;
4. before a research gap is accepted;
5. before route cards are ranked;
6. before an implementation repository is created;
7. before any manuscript claim is drafted.

Codex can assist with structure, search, reading, synthesis, and code. It should not be trusted to determine scientific novelty without human review.
