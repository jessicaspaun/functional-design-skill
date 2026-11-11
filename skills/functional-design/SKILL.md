---
name: functional-design
description: Apply concepts from Functional Programming in Scala to design, refactor, review, or explain code, including Python and TypeScript. Use for functional decomposition, explicit state and errors, composable operations, effect boundaries, and law-based testing; avoid activating for unrelated routine edits.
---

# Functional Design

Use the ideas in Paul Chiusano and Rúnar Bjarnason's *Functional Programming in Scala* to make behavior easier to understand, compose, and verify. Adapt the concepts to the repository's language and conventions. The book is a conceptual source, not a requirement to use Scala or introduce an FP framework.

## Choose the task

- **Implement or refactor:** inspect the relevant code, public contract, dependencies, and tests; make a focused change within the user's scope.
- **Review:** report concrete correctness or maintenance problems with locations and consequences. Distinguish defects from optional design suggestions. Do not rewrite code unless requested.
- **Teach:** explain one concept through a small example in the user's language, connect it to their problem, and offer an exercise when useful. Do not require category theory first.

Read only the supporting material needed:

- [Concepts and design decisions](references/concepts.md): state, errors, algebraic design, parallelism, parsing, abstraction laws, effects, and streaming.
- [Language examples](references/examples.md): original Python, TypeScript, and Scala examples, plus agent-workflow adaptations.
- [Book review and chapter map](references/book-review.md): source provenance, chapter/page references, strengths, limitations, and the distinction between book concepts and practical adaptations.

## Start with observable behavior

Identify what must remain true: returned values, expected failures, ordering, externally visible mutations, effect timing and count, resource lifetime, and relevant performance bounds. A refactor that returns the same value but changes these observations can still break the contract.

Trace hidden inputs such as clocks, randomness, environment, shared state, network responses, and mutable aliases. Passing an effectful callback as an argument makes a dependency explicit; it does not itself make the caller pure.

Choose the smallest useful improvement. Extract a pure transformation, introduce a named result variant, or make a state transition explicit before considering a generic abstraction. Keep a straightforward implementation if the alternative adds machinery without a concrete benefit. Preserve public signatures unless changing them is part of the task; use boundary adapters when needed.

## Functional design choices

### Design the domain contract before the implementation

For new or substantially revised behavior, sketch the input and output types, valid states, expected failures, and dependencies before filling in the function body. Ask what a caller can learn from the signature and which invalid combinations it still permits. Distinguish raw input from validated domain values when that prevents a real misuse, and make required information explicit rather than hiding it in globals or permissive containers.

Use those contracts to guide decomposition: validation produces a validated value or issues; a decision consumes the validated value; execution produces an observed outcome. Read [the contract sketch](references/examples.md#contract-sketch-design-before-filling-in-bodies) for an example. Favor the project's ordinary types and runtime validators. Signatures constrain possible implementations but do not prove business correctness or runtime validity. For an existing API, preserve its contract unless changing it is authorized; improve internal types without forcing a public migration.

### Separate decisions from effects

Compute domain results, validated requests, or descriptions of work in ordinary functions. Execute network calls, persistence, logging, and other effects at a clear boundary. If later decisions require external observations, execute that step and feed the observation into the next decision; do not pretend the whole workflow can always be planned in advance.

An effect description is inert data or a deferred computation with a defined interpreter. Creating an eager promise or submitting a task may already start work. Wrapping an already executed operation does not defer it. Never label LLM calls or ordinary network reads pure because the request is repeatable.

### Model data, failure, and state deliberately

- Use immutable domain values where shared mutation causes ambiguity. Check nested containers and aliases: `readonly` and frozen wrappers may be shallow. Persistent structures can share unchanged parts; copying a Python list or spreading a JavaScript array still copies elements.
- Use distinct variants for meaningful alternatives rather than several flags that permit contradictory combinations. Validate untrusted data at runtime; static annotations are not validation.
- Represent expected absence separately from errors needing an explanation. Choose explicit success/error values where they improve composition, while preserving the repository's public exception contract. Catch known boundary failures narrowly; do not convert programming bugs, cancellation, or every exception into a successful empty result.
- Choose fail-fast composition for dependent steps. Choose error accumulation for independent checks when callers need all failures. Applicative structure permits independence; its actual implementation determines error handling and execution strategy.
- Represent a stateful decision as `(state, input) -> (new_state, result)` when replay, testing, or avoiding shared mutation helps. Consistently thread the returned state. Keep persistence and concurrency control at the boundary: a pure transition alone does not prevent lost updates.

### Compose with clear semantics

Use `map` for transforming a value within a context, `flatMap`/bind for selecting a subsequent contextual computation from a previous result, and folds for aggregation. Use a loop, comprehension, or standard helper when it expresses the same intent more clearly. Do not replace loops with recursion in languages without suitable stack guarantees.

Define reusable operations and their laws when designing a real library. Infer abstractions from concrete use cases. Prefer the weakest capability needed: mapping before independent combination, independent combination before dependent sequencing. Do not add custom monads, parsers, IO runtimes, or higher-kinded encodings merely to imitate the book's teaching exercises.

For chunked aggregation, establish associativity and an identity before changing grouping. Reordering also needs commutativity or preserved order. Floating-point arithmetic may invalidate exact regrouping equivalence. For means, merge totals and counts rather than averaging chunk averages.

### Keep execution semantics explicit

For concurrency, distinguish independent computations from computations that are safe to run concurrently. Account for bounded capacity, failure propagation, cancellation, ordering, and cleanup. Never block a worker waiting on work that needs the same exhausted pool.

For lazy or streaming pipelines, specify demand, replay/memoization, and resource ownership. Laziness alone guarantees neither bounded memory nor cleanup. Keep file/connection lifetime around consumption; release resources on exhaustion, failure, early exit, and cancellation using the runtime's structured facilities. Include retained state, buffers, and the terminal consumer in memory analysis.

Local mutation can be a good implementation choice when callers cannot observe intermediate state, inputs are not mutated through aliases, and mutable internals do not escape. Judge the observable interface and actual cost.

## Verify the relevant invariants

For a substantive refactor or reusable abstraction, combine concrete regression cases with applicable properties. Examples include preservation of input data, state replay, round-trip laws on their stated domain, identity/associativity for custom combinators, deterministic aggregation across partitions, and cleanup on early termination.

Generate edge cases and valid structured inputs, rather than filtering most inputs away. Retain reproducible counterexamples, preferably minimized by the existing test framework. Equality for effects means equivalent observations under a specified interpreter, not object identity or executing a live effect twice. Property tests provide evidence over sampled inputs, not a proof.

Use existing test tools and dependency versions. Do not add a testing library for a trivial change, or create a test suite solely because this skill is active. Check large-input stack and memory behavior when the change makes those relevant. Verify modern library APIs against the installed version or official documentation instead of copying older book syntax blindly.

## Report the result

Lead with what changed or what the review found, then explain the functional idea in plain language and its practical benefit. State tests actually run and material limits. In reviews, make optional abstractions visibly optional. In teaching, distinguish conceptual examples from production-ready implementations. If no functional redesign is justified, say so and keep the solution simple.
