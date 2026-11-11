# Book review and source map

Reviewed: November 11, 2026.

## Source and review scope

Paul Chiusano and Rúnar Bjarnason, *Functional Programming in Scala*, Manning, ISBN 9781617290657. The reviewed source is the original 15-chapter edition, with 322 PDF pages and printed chapter content on pages 3-293. Its copyright page states 2015. Do not confuse it with a later edition or treat its library observations as current Scala API documentation.

- [Publisher: Functional Programming in Scala](https://www.manning.com/books/functional-programming-in-scala)
- [Authors' companion repository](https://github.com/fpinscala/fpinscala), identified in the book; select material matching the edition when consulting it.

Review method: extracted the complete PDF for navigation, reviewed the contents and explanatory passages across all 15 chapters, with focused reading on purity, data sharing, error handling, state, algebraic design, laws, effect interpretation, and resource safety. Visually checked the contents and resource-safety discussion. This is a concept-focused review, not a claim that every page, exercise solution, proof, or implementation was independently verified.

This skill contains original instructions and examples derived from the concepts. It does not bundle the PDF, the extracted text, the book's program listings, or an exercise answer collection. Runtime and operational advice is identified below as practical adaptation.

## Assessment

The book's strongest contribution is a method for designing software: begin with concrete programs, make hidden behavior explicit, describe operations with types, and test the relationships those operations should preserve. Separating description from interpretation appears repeatedly, from returning a requested action to modeling state, parallel computation, I/O, and streams.

It is especially useful for understanding why small transformations and explicit outcomes compose well, why an abstraction needs laws as well as method signatures, and why pure descriptions still depend on a correct interpreter. The bounded-pool deadlock and streaming cleanup discussions prevent a simplistic reading in which a functional interface automatically solves execution problems.

The sequence is demanding. Building libraries from first principles teaches design reasoning, but an application engineer usually benefits from applying a few ideas within existing tools before constructing an entire abstraction hierarchy. Chapters 1, 3, 4, 6, and the effect-boundary ideas in 13 are particularly direct starting points. Chapters 7-12 provide deeper library-design reasoning; 5, 14, and 15 sharpen performance and resource reasoning.

The main limitation for direct code reuse is that many implementations are deliberate teaching stages. Some are later revised because they deadlock, overflow the stack, or lack required semantics. Scala syntax and library details also reflect the edition's era. This skill therefore extracts design criteria and tells the agent to check the actual project's APIs and runtime guarantees.

## Chapter map

Numbers below are printed pages. For the numbered chapter pages in this PDF, add 21 to obtain the one-based PDF page (for example, printed 283 is PDF page 304).

| Chapter | Printed pages | Concept carried into the skill | Practical decision |
| --- | --- | --- | --- |
| 1. What is functional programming? | 3-13 | Purity, referential transparency, returning requested actions as values | Separate domain decisions from externally visible execution |
| 2. Getting started | 14-28 | Higher-order and polymorphic functions; types constrain implementations | Reuse concrete patterns; adapt recursion to the host runtime |
| 3. Functional data structures | 29-47 | ADTs, pattern matching, persistence, structural sharing, folds | Model meaningful alternatives; distinguish sharing from copying |
| 4. Handling errors without exceptions | 48-63 | Option, Either, composition, failure as a value | Distinguish absence, explained failure, and dependent propagation |
| 5. Strictness and laziness | 64-77 | Non-strictness, memoization, demand, unfold | Define evaluation and retention semantics before using lazy pipelines |
| 6. Purely functional state | 78-91 | RNG and general state transitions | Make state explicit and thread the returned state consistently |
| 7. Purely functional parallelism | 95-123 | Descriptions, interpreters, API laws, bounded-pool deadlock | Check execution semantics; avoid blocking nested work on the same pool |
| 8. Property-based testing | 124-145 | Generators, properties, minimization, sized generation | Specify invariants and generate revealing inputs; keep counterexamples |
| 9. Parser combinators | 146-171 | Algebra-first design, dependent parsing, errors and backtracking | Define semantics and failure context before choosing representation |
| 10. Monoids | 175-186 | Associative merging, identity, folds, composed summaries | Establish merge laws before changing grouping or chunking |
| 11. Monads | 187-204 | Functor, bind, lift, composition laws | Use dependent sequencing when the next action needs a previous result |
| 12. Applicative and traversable functors | 205-226 | Independent combination, accumulating validation, traversal, composition limits | Use only the capabilities needed; distinguish independence from parallel execution |
| 13. External effects and I/O | 229-253 | Effect factoring, IO, trampolining, Free, interpreters | Keep descriptions inert; verify stack safety in the actual runtime |
| 14. Local effects and mutable state | 254-267 | Scoped mutation, ST, contextual purity | Permit efficient internal mutation when it cannot leak through aliases |
| 15. Stream processing and incremental I/O | 268-293 | Composable processing, effectful streams, resource safety | Scope resources around consumption, including early termination and failure |

## What is adaptation rather than a book claim

Python dataclasses and generators, TypeScript discriminated unions and promises, AI tool-call plans, LLM nondeterminism, retry/idempotency concerns, persisted-state concurrency control, and modern cancellation practices are applications of the concepts to other contexts. They are not presented as examples or guarantees supplied by the book.

The skill's guidance to prefer established libraries over building pedagogical runtimes is an application-engineering judgment. Likewise, preserving existing public contracts and choosing a small refactor are scope decisions for agent work, not requirements attributed to the authors.

## Podcast context added November 11, 2026

In Ryan Peterman's December 15, 2025 interview, Boris Cherny recommends the book around [15:52](https://www.youtube.com/watch?v=AmdLVWMdjOk&t=952s). He emphasizes its influence on his reasoning and type signatures, including work in Python and TypeScript. The host's [published transcript](https://www.developing.dev/p/boris-cherny-creator-of-claude-code) covers this passage through about 17:00; this check used the transcript rather than independently reviewing the audio.

Our practical interpretation is to make domain-contract design an explicit step before implementation, with a small contract sketch in the examples. This is an adaptation of his emphasis, not a claim that he prescribes this skill or a particular workflow for coding agents.

## Example invocations

- `Use $functional-design to review this Python agent workflow for hidden state and side effects. Suggest focused changes.`
- `Use $functional-design to refactor this TypeScript validator so independent field errors are returned together.`
- `Use $functional-design to explain map, applicative combination, and flatMap using this Scala code.`
- `Use $functional-design to check whether this streaming pipeline closes resources when its consumer stops early.`
- `Use $functional-design to decide whether this proposed abstraction makes the code easier to maintain.`
- `Use $functional-design to design the data types and function signatures for this feature before implementing it.`

## Creation-time validation

The skill structure/frontmatter validator passed, UI metadata was parsed and checked, and all local reference links resolved. Executed all three Python code blocks and checked independent error accumulation, inert planning versus execution, 1,000 reproducible state-transition cases, bounded preview consumption, and file closure on exhaustion, early exit, and exceptions. TypeScript and Scala examples received static review; their compilers were not available and those examples were not compiler-checked.

A separate agent used the skill on three read-only scenarios: a lazy reader outliving its file, a straightforward TypeScript loop refactor, and a design review involving batch averages and eager promises. It identified the concrete defects and preserved the simple loop without unnecessary abstraction. These focused checks do not prove behavior on every future task.
