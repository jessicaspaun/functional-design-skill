# Concepts and design decisions

Read the relevant sections when the task goes beyond a small pure-function extraction. Chapter references point to the supplied edition; see [book-review.md](book-review.md) for page ranges and source details. The decision rules below are practical synthesis, not quotations or a reproduction of the book's implementations.

## Contents

- Purity and immutable data (chapters 1-3, 14)
- Absence, failure, and validation (chapters 4, 12)
- Explicit state (chapter 6)
- Designing an algebra and parsers (chapters 7-9)
- Monoids, functors, applicatives, monads, traversal (chapters 10-12)
- Effects and interpreters (chapter 13)
- Lazy and resource-safe streaming (chapters 5, 15)
- Properties worth testing (chapter 8 and laws throughout)

## Purity and immutable data

A pure calculation depends on its explicit values and has no relevant observable side effects. Referential transparency allows replacing an expression with its result while preserving the observations that matter in the program. Define those observations before optimizing or refactoring: domain output alone may omit externally visible logs, I/O, identity, timing requirements, or mutation.

Separate calculating a requested action from performing it. Returning a domain command can permit inspection, batching, deterministic tests, or a different interpreter. It is useful only if this separation removes a real coupling; it need not become a command framework.

Algebraic data types model a choice between variants, each containing the fields appropriate to that case. Examples: `Pending | Completed(value) | Failed(reason)`, rather than `done`, `failed`, and nullable payload fields that can contradict one another. Use exhaustive handling where the language supports it. Do not assume types prevent invalid values arriving through JSON, casts, deserialization, or external libraries.

Persistent structures preserve previous versions and can reuse unchanged structure. Ordinary immutable-looking array copies are not automatically persistent data structures with cheap updates. Repeated append/copy in a loop can be quadratic. Prefer a local builder followed by a stable result if that preserves the contract more efficiently.

Local mutation is compatible with a pure observable interface when no external alias can observe it. A fresh list mutated during construction and returned as a tuple is a simple Python example. Mutating a nested input object after copying only its outer dictionary is not equivalent.

## Absence, failure, and validation

| Need | Suitable shape | Important choice |
| --- | --- | --- |
| Legitimately absent value | Option/Maybe, nullable return where idiomatic | Absence does not explain a failure |
| Success or an expected domain error | Either/Result, discriminated union | Preserve the reason and distinguish errors from empty success |
| Independent field checks with all errors shown | Validated value or collection of issues | Define deterministic error order; each check must be independently meaningful |
| Later step needs an earlier success | Bind/flatMap or ordinary branching | Do not run dependent work after failure |
| Existing library raises expected exceptions | Narrow boundary adapter | Translate documented exceptions; retain useful context |

Applicative combination does not inherently accumulate errors. The chosen instance must define accumulation, usually using an associative combination for errors. An Either-style instance may still fail fast. Likewise, an independent structure does not inherently execute in parallel.

Do not replace all exceptions everywhere. A framework may require exceptions at its boundary, and an application can reasonably expose exceptions while using explicit domain results internally. Be precise about which failures the new result type handles.

## Explicit state

Model a transition as `step(state, event) -> (new_state, output)`. It makes dependencies visible and permits replay without a live database. State may describe a workflow, parser position, retry policy, UI, or pseudorandom generator.

Using the same initial RNG state reproduces the same generated value. Producing the next value requires the next state, not another call with the original state. A mutable seeded RNG is reproducible as a sequence, but it is still stateful; invoking it repeatedly changes its internal state.

For persisted workflows, pair the pure transition with a storage mechanism appropriate to concurrent writers, such as a transaction or version check already used by the system. Snapshot purity cannot enforce atomic commits. Replaying recorded events must not accidentally resend previously executed external actions.

## Designing an algebra and parsers

Start from a few real client examples. Write the operations needed to express them, specify their intended relationships, and then choose a representation. Distinguish primitives from operations derivable by composition. Revise a proposed law when its preconditions were too broad, or fix the implementation when it violates the intended contract.

The book's bounded-thread-pool deadlock is an important example: nesting a task that blocks while waiting for another task on the same saturated pool defeats compositional reasoning. A pure description does not ensure that every interpreter is safe. Use a maintained runtime's nonblocking composition in production; do not build a replacement actor or scheduler for an application refactor.

Parser design illustrates more than text processing. Combinators need semantics for consumed input, alternatives, failure context, and commitment/backtracking. For actual parser tasks:

- Repeated parsers need a progress condition: repeating a parser that succeeds without consuming input can loop forever.
- Distinguish construction-time recursion from parse-time recursion; defer recursive parser construction when necessary.
- Preserve position and relevant context in failures; do not silently discard the most informative branch error.
- Bound or deliberately control backtracking. A fallback after partially consuming a branch is a semantic choice, not just a performance tweak.
- Decide whether the caller requires complete input consumption; accepting a prefix can hide malformed trailing data.

For ordinary JSON or a known format, use the existing standard/library parser. Building combinators is appropriate when learning or solving a real grammar problem that existing tools do not serve.

## Abstraction by actual capability

The signatures here are explanatory pseudocode; they do not require a particular library or implementation.

| Structure | Capability | Useful situation | Do not infer |
| --- | --- | --- | --- |
| Monoid | `combine(A, A) -> A` with identity | Merge summaries and fold partitions | Reordering is safe, or numerical regrouping is exact |
| Functor | `map(F[A], A -> B) -> F[B]` | Transform a contained result without changing the context's intended structure | Any method named `map` satisfies the laws |
| Applicative | Lift values and combine independent contextual computations | Validate independent fields or describe a fixed computation structure | Errors accumulate or tasks run concurrently automatically |
| Monad | `bind(F[A], A -> F[B]) -> F[B]` plus lift | Choose the next computation using a prior result | Every nested pair of monads composes into a lawful monad automatically |
| Traverse | `traverse(T[A], A -> F[B]) -> F[T[B]]` | Process each element with context while retaining the outer structure | Traversing is parallel, bounded, or resource-safe by itself |

`sequence` exchanges `T[F[A]]` for `F[T[A]]`; `traverse` first maps into the context, then performs that exchange. Choose failure and ordering semantics explicitly.

For aggregation, use a summary that can be merged associatively. A mean needs `(sum, count)`, with identity `(0, 0)`; finalization divides sum by count and handles zero count. An unweighted mean of partition means is incorrect for unequal partition sizes. IEEE floating-point addition is not exactly associative. Preserve a specified reduction order or define and validate a numerical error policy when that matters.

Recognizing a monoid does not require introducing a `Monoid` class. A clearly named merge function and tested laws can be sufficient. Similarly, ordinary branching or `await` can express dependent sequencing without a new generic Monad interface.

## Effects and interpreters

Separate the description of work from running it. A domain-specific plan can have a real interpreter and an in-memory test interpreter. For interactive workflows, descriptions may include continuations or be built in stages after each observation; one static list cannot represent every dependency.

Construction must be inert if the abstraction promises deferral. In particular, JavaScript promises are often eager; a Python coroutine object, a scheduled task, and an already-running request also have different lifetimes. Use the existing runtime's documented mechanisms and check when execution starts.

An `IO` wrapper does not by itself guarantee stack safety, exception capture, cancellation, or resource release. The book develops representations and interpreters to address such problems. Reuse those ideas as design criteria; use the project's established runtime rather than transplanting the pedagogical runtime.

Effects-as-data do not make external actions safe to repeat. Retry limits, idempotency, and whether an action can be retried belong to the execution contract. For AI workflows, a timeout may leave an ambiguous remote result; deterministic planning does not imply deterministic generation or exactly-once execution.

## Lazy and resource-safe streaming

Laziness controls when work is demanded. Memoization controls whether already-computed values are retained and reused. A generator is usually consumable once; a memoized lazy sequence has different replay and retention behavior.

Analyze the whole pipeline. A bounded transform followed by `list(...)`, an unbounded queue, a global sort, or a growing group-by may still require unbounded memory. Retaining the head of a memoized stream can retain its evaluated tail. Avoid promising constant memory merely because code uses a stream API.

Treat acquisition, consumption, and release as one scoped lifecycle. Acquiring a file inside a function and returning a lazy reader after leaving that scope may produce reads from a closed handle. Acquiring inside an abandoned generator can instead leak it unless the consumer explicitly closes it. Use the language/runtime's context management or resource abstraction so ownership is unambiguous.

Test cleanup under normal exhaustion, transform failure, early termination, and cancellation where applicable. In concurrent pipelines, also account for producer shutdown and blocked writers when consumers stop. Use runtime guarantees for cancellation-safe finalizers instead of approximating them with an unprotected callback.

## Properties worth testing

Choose laws that constrain observable behavior, and state their domain. Useful examples:

- **Monoid:** `combine(combine(a,b),c) == combine(a,combine(b,c))`; identity on both sides. No commutativity assumption unless actually needed.
- **Functor:** mapping identity preserves the context; two successive pure maps agree with mapping their composition.
- **Monad:** binding a lifted value agrees with direct application, binding to lift preserves the computation, and regrouping binds preserves semantics. Compare observations under controlled interpreters for effects.
- **Validation:** independent invalid fields all appear in the result; valid cases return a validated value. Generate combinations of multiple simultaneous failures.
- **State:** replay from the same initial state and events produces the same final state and outputs; the old state remains unchanged.
- **Parsing:** valid render/parse round trips where the format promises them; malformed suffixes, empty input, incomplete input, and useful failure positions.
- **Streaming:** result equivalence with a small strict reference implementation; early exit does not over-read; resources close on all supported exit paths.
- **Aggregation:** merging summaries from different valid partitions agrees with the specified whole-input result. Include empty and unequal partitions.

Keep example tests for specific regressions. A sorting property such as idempotence alone is too weak: returning an empty list is also idempotent. Check ordering and preservation of elements/counts. Likewise, a round-trip can miss a shared bug in encoder and decoder; use independent examples or an oracle when warranted.

Use appropriate generators and shrinking from the project's testing framework. Record seeds/counterexamples for reproducibility. Sampling a property is evidence, not a proof for every value or every scheduler interleaving.
