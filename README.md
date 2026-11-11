# Functional Design Skill

A reusable skill for AI coding agents that applies ideas from *Functional Programming in Scala* to everyday software design, code review, and teaching in Python, TypeScript, and Scala.

Design inputs, outputs, valid states, and failure cases before implementing the logic. Then choose the smallest change that improves correctness or clarity within the project's existing language and conventions.

## What it helps with

- Designing domain types and function signatures.
- Separating pure decisions from I/O and other effects.
- Modeling expected errors and explicit state transitions.
- Choosing between independent validation and dependent sequencing.
- Understanding composition, monoids, functors, applicatives, monads, and traversal.
- Checking lazy pipelines, resource lifetimes, concurrency, and aggregation laws.
- Writing useful properties and regression tests.

The skill favors focused improvements and established libraries. It permits clear loops and efficient local mutation when they preserve the intended behavior.

## Install in Codex

In Codex, ask the built-in skill installer:

```text
Use $skill-installer to install the skill at
https://github.com/jessicaspaun/functional-design-skill/tree/main/skills/functional-design
```

Alternatively, clone this repository and copy the skill folder:

```bash
git clone https://github.com/jessicaspaun/functional-design-skill.git
mkdir -p ~/.codex/skills
cp -R functional-design-skill/skills/functional-design ~/.codex/skills/functional-design
```

The manual command assumes that destination does not already exist. For an existing installation, compare the folders and update the intended files rather than nesting another copy inside it. The installed skill is available on the next turn after Codex refreshes its skill catalog.

For another agent that supports `SKILL.md`, use its documented skill installation location and preserve the `references/` folder. The core instructions do not require a particular model or an FP library; `agents/openai.yaml` supplies Codex UI metadata.

## Use it

```text
Use $functional-design to design the data types and function signatures
for this feature before implementing it.
```

```text
Use $functional-design to review this Python agent workflow for hidden
state, effects, and resource-lifetime bugs. Report findings without editing.
```

```text
Use $functional-design to refactor this TypeScript validator so independent
field errors are returned together, preserving the public API.
```

```text
Use $functional-design to explain map, applicative combination, and flatMap
using a small example from this codebase.
```

## Read the material

- [Skill instructions](skills/functional-design/SKILL.md)
- [Concepts and design decisions](skills/functional-design/references/concepts.md)
- [Original language examples](skills/functional-design/references/examples.md)
- [Book review, chapter map, and podcast context](skills/functional-design/references/book-review.md)

## Sources and attribution

The conceptual source is Paul Chiusano and Rúnar Bjarnason's [*Functional Programming in Scala*](https://www.manning.com/books/functional-programming-in-scala), using its original 15-chapter edition. The book review distinguishes those concepts from this repository's practical adaptations and original examples.

The type-design emphasis also draws on Boris Cherny's discussion around [15:52-17:00 of his interview with Ryan Peterman](https://www.youtube.com/watch?v=AmdLVWMdjOk&t=952s). The [host's transcript](https://www.developing.dev/p/boris-cherny-creator-of-claude-code) was used to check that passage.

This is an independent project by [Jessica Desotell](https://github.com/jessicaspaun), developed with AI assistance. It is not affiliated with or endorsed by the book's authors, Manning, Boris Cherny, or the podcast. The repository contains original skill guidance and examples; it does not redistribute the book, its listings, or an exercise answer collection.

## Validation

Run the dependency-free checks with Python 3.10 or later:

```bash
python3 -m unittest discover -s tests -v
```

The checks execute the Python examples and verify validation behavior, planning versus execution, reproducible state transitions, preview consumption, cleanup on several exit paths, and local documentation links. GitHub Actions runs the same checks.

TypeScript and Scala examples are teaching examples that have received static review; this repository's checks do not compile them. Property and example tests provide evidence for the cases tested, not a proof of correctness for all programs or agent behavior.
