# AGENTS.md

## Project Overview
This repository is for a master's thesis project on air-ground collaborative autonomous decision-making.

The simulation stack is:
- Unreal Engine 5.3
- AirSim
- Python

The system contains:
- one UAV
- one UGV

This project is not a generic robotics demo. It is a research-oriented thesis codebase. Every substantial code change should support a clear research objective, not just add engineering complexity.

---

## Core Research Direction
The thesis focuses on air-ground collaboration rather than duplicating a full single-robot autonomy stack for multiple robots.

The main design principle is:

**Reuse single-platform execution capability, and concentrate innovation at the collaboration layer.**

Do not simply clone one full high-level brain for the UAV and another for the UGV.

The intended high-level architecture is:
- lightweight platform executors for UAV and UGV
- one collaboration-level coordinator / shared-state layer above them
- later, a higher-level collaborative decision module

---

## Current Priority
Always prioritize **Research Topic 1** unless explicitly told otherwise.

### Research Topic 1
**Shared semantic-state / semantic-map consistency maintenance for air-ground collaboration**

The key problem is:
- UAV and UGV observe the environment from different viewpoints
- observations arrive at different times
- states can become inconsistent or stale
- naive periodic synchronization is not sufficient

The current implementation priority is:
1. shared state representation
2. observation normalization
3. conflict detection
4. state fusion
5. event-triggered update
6. logging and evaluation hooks

Do **not** proactively implement full collaborative task allocation or dynamic replanning yet unless explicitly requested.

---

## Expected Research Style
All implementations should be:
- modular
- thesis-friendly
- easy to explain in a methodology chapter
- easy to ablate in experiments
- easy to extend later

Prefer clear intermediate abstractions over tightly coupled code.

When designing modules, favor:
- dataclasses
- type hints
- docstrings
- small functions
- explicit assumptions
- TODO markers for unresolved research details

---

## Code Generation Rules
When writing code in this repository, follow these rules:

1. **Do not over-engineer**
   - Avoid unnecessary frameworks.
   - Avoid adding infrastructure that is not needed for the current research stage.

2. **Do not silently broaden scope**
   - Do not jump from Research Topic 1 into full Research Topic 2.
   - Do not introduce new subsystems unless they directly support the current task.

3. **Preserve low-level control assumptions**
   - Do not redesign low-level UAV flight control.
   - Do not redesign low-level UGV control.
   - Treat AirSim platform control as an existing capability unless explicitly told otherwise.

4. **Do not build a full SLAM system from scratch**
   - If mapping is needed, implement only the minimum shared semantic-state layer required by the current research goal.

5. **Use adapters for uncertain APIs**
   - If AirSim or UE integration details are uncertain, isolate them in adapter classes.
   - Clearly mark assumptions in comments.

6. **Keep outputs inspectable**
   - Prefer structured logs, JSON-serializable state objects, and simple debug outputs.
   - Make it easy to inspect intermediate shared-state updates.

7. **Default language**
   - Code, comments, docstrings, and commit messages should be in English unless explicitly requested otherwise.
   - Explanatory summaries to the user can be in Chinese.

---

## Preferred Implementation Pattern
For new work, prefer the following workflow:

1. Read the repository structure first.
2. Explain the planned change briefly.
3. Modify only files relevant to the current task.
4. Keep patches reviewable and logically grouped.
5. After coding, summarize:
   - what was changed
   - what assumptions were made
   - what remains as TODO
   - how this supports the thesis research point

---

## Shared-State Design Guidance
For Research Topic 1, prefer a 3-level shared state abstraction:

- **Region level**
  - region id
  - topology / adjacency
  - exploration or completion state
  - last update time

- **Entity level**
  - object id
  - semantic category
  - source platform
  - timestamp
  - confidence
  - optional coarse position
  - verification status
  - conflict flag

- **Task-state level**
  - owner
  - status
  - dependency
  - last update time

This should support later collaborative planning, but should not depend on that module being implemented now.

---

## Event-Triggered Update Guidance
Do not rely only on blind periodic synchronization.

Support event-triggered updates such as:
- new entity discovered
- confidence changed significantly
- semantic label changed
- region completion status changed
- state conflict detected
- stale-state timeout exceeded

Every triggered update should be traceable in logs.

---

## Conflict and Fusion Guidance
When different platforms provide inconsistent updates, prefer explicit conflict handling instead of silent overwrite.

Use interpretable fusion logic based on factors such as:
- freshness
- confidence
- source reliability
- consistency with previous state

Support outcomes such as:
- accept
- merge
- conflict
- mark for verification

The code should make these decisions easy to inspect and explain in a thesis.

---

## Evaluation Hooks
Whenever possible, keep lightweight hooks for future experiments, such as:
- entity consistency rate
- conflict count
- stale-state ratio
- update frequency
- estimated communication volume

Do not implement a large evaluation framework unless explicitly requested.

---

## What to Avoid
Avoid these patterns unless explicitly requested:
- end-to-end monolithic “brain”
- hard-coded task logic mixed with perception code
- hidden global mutable state
- overly clever abstractions that reduce readability
- large speculative rewrites
- implementing full collaboration planning before shared-state consistency is stable

---

## If Information Is Missing
If key details are missing:
- make the smallest reasonable assumption
- state the assumption clearly
- leave a TODO for later refinement

Do not fabricate precise sensor or simulator details that are not confirmed.

---

## Review Standard
Before finalizing a patch, check:
- Is this directly useful for the thesis?
- Is the scope controlled?
- Is the code easy to explain in the methodology chapter?
- Is it easy to extend into Research Topic 2 later?
- Does it avoid unnecessary duplication of single-robot logic?