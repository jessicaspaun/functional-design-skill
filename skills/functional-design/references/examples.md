# Original language examples

These small teaching examples apply the book's concepts without reproducing its listings. They are not a production workflow engine or a requirement to adopt new dependencies. Check the project's language version and conventions before adapting them.

## Contract sketch: design before filling in bodies

For a document-generation feature, first sketch contracts in the host language. The following is pseudocode, not an executable API or a demand for these exact names:

```text
validate: RawRequest -> ValidatedRequest | ValidationIssues
decide: (ValidatedRequest, ContextSnapshot) -> GenerationPlan | Rejected
execute: GenerationPlan -> GeneratedDocument | ProviderFailure
persist: GeneratedDocument -> SavedDocument | StorageFailure
```

This sketch exposes decisions before implementation: what constitutes valid input, what context is required, which failures callers must handle, and where external effects occur. If persistence requires a successful generation, it consumes that success value rather than a status flag plus an optional payload. Choose variants with the fields appropriate to each outcome, so ordinary typed callers cannot casually combine contradictory states.

The concrete implementation may use synchronous returns, `async`/`await`, exceptions at an existing boundary, or a library result type. Keep those execution details accurate. A signature returning an outcome does not make its implementation pure. Validate external data at runtime, and do not introduce nominal wrappers around every string unless the distinction prevents a meaningful error.

## Python: an inert plan and a separate executor

Python 3.10+ syntax. The domain checks assume typed inputs from an already validated boundary. Untrusted JSON would need runtime type validation first.

```python
from dataclasses import dataclass
from collections.abc import Callable


@dataclass(frozen=True)
class GenerationRequest:
    prompt: str
    max_tokens: int


@dataclass(frozen=True)
class Plan:
    request: GenerationRequest


@dataclass(frozen=True)
class Invalid:
    issues: tuple[str, ...]


def plan_generation(prompt: str, max_tokens: int) -> Plan | Invalid:
    issues: list[str] = []
    if not prompt.strip():
        issues.append("prompt must contain text")
    if max_tokens <= 0:
        issues.append("max_tokens must be positive")
    if issues:
        return Invalid(tuple(issues))
    return Plan(GenerationRequest(prompt, max_tokens))


def execute(plan: Plan, generate: Callable[[GenerationRequest], str]) -> str:
    return generate(plan.request)
```

`plan_generation` has no model call, logging, or hidden configuration lookup. Its temporary mutable list is local; callers only receive immutable fields. It preserves the original prompt, using trimming solely to check for blank input. Independent invalid fields produce both issues. `execute` is effectful if its callback is effectful; dependency injection does not make it pure.

This example deliberately omits provider-specific failures, persistence, retries, and cancellation. Define those at the actual execution boundary using the project's contracts. It makes no claim that running the plan twice is safe or produces the same generated text.

## Python: replayable state transition

```python
@dataclass(frozen=True)
class Budget:
    remaining: int  # Domain invariant: non-negative.


@dataclass(frozen=True)
class Reserved:
    amount: int


def reserve(budget: Budget, amount: int) -> tuple[Budget, Reserved | Invalid]:
    if amount <= 0:
        return budget, Invalid(("amount must be positive",))
    if amount > budget.remaining:
        return budget, Invalid(("insufficient budget",))
    return Budget(budget.remaining - amount), Reserved(amount)
```

This is a pure decision about a supplied snapshot. It does not reserve funds or tokens in a shared service. The caller must use the returned state for the next decision. Persisting reservations concurrently needs an appropriate atomic operation, transaction, or version check.

Useful properties: rejected reservations leave the state unchanged; successful reservations decrease the balance by exactly the requested amount; replay with the same inputs gives the same result. Generate only budgets satisfying the invariant, and test boundary validation separately if it is in scope.

## Python: resource lifetime includes consumption

```python
from collections.abc import Iterable
from itertools import islice
from pathlib import Path


def first_nonempty(lines: Iterable[str], limit: int) -> tuple[str, ...]:
    if limit < 0:
        raise ValueError("limit must be non-negative")
    selected = (line.strip() for line in lines)
    return tuple(islice((line for line in selected if line), limit))


def read_preview(path: Path, limit: int) -> tuple[str, ...]:
    with path.open(encoding="utf-8") as source:
        return first_nonempty(source, limit)
```

Consumption happens inside `with`; successful early exit and exceptions both close the file. The example uses a normal exception for an invalid programmer-supplied argument to show that using functional ideas does not mandate replacing every exception contract.

`first_nonempty` can be tested with a tuple of strings, but consumes state if given a file or one-shot iterator; do not describe it as pure over every `Iterable`. The result retains at most `limit` strings, while scanning may inspect many blank lines. Memory also depends on line length and buffering, so this is not a constant-byte-memory guarantee.

## TypeScript: accumulate independent errors, then execute

The generic result type does not itself dictate failure policy. This validator explicitly collects issues in a stable order. It expects typed input; static types do not validate external JSON. `readonly` here is a compile-time restriction, not runtime freezing.

```typescript
type Result<T> =
  | { readonly ok: true; readonly value: T }
  | { readonly ok: false; readonly errors: readonly string[] };

type RequestPlan = {
  readonly prompt: string;
  readonly maxTokens: number;
};

function makePlan(prompt: string, maxTokens: number): Result<RequestPlan> {
  const errors: string[] = [];
  if (prompt.trim().length === 0) errors.push("prompt must contain text");
  if (!Number.isSafeInteger(maxTokens) || maxTokens <= 0) {
    errors.push("maxTokens must be a positive safe integer");
  }
  return errors.length > 0
    ? { ok: false, errors }
    : { ok: true, value: { prompt, maxTokens } };
}

async function executePlan(
  plan: RequestPlan,
  generate: (request: RequestPlan) => Promise<string>,
): Promise<string> {
  return generate(plan);
}
```

`makePlan` builds data and starts no task. Calling `executePlan` invokes `generate`; an `async` function is not an inert plan merely because it returns a promise. This executor preserves the callback's rejection behavior rather than swallowing it. An application can add a narrow provider-error adapter if its contract requires one.

If generation requires retrieval output, plan retrieval first, execute it, and then compute the generation request from the observed output. Do not precompute a dependent prompt with missing information or run dependent calls concurrently.

## Scala: transform a result versus choose the next computation

Uses Scala 2.13-compatible syntax and standard right-biased `Either`. Check the actual target version; older Scala observations in the book do not establish today's library behavior. This object is a standalone teaching example.

```scala
object FunctionalExample {
  sealed trait Problem
  case object BlankPrompt extends Problem
  case object NonPositiveLimit extends Problem

  final case class Request(prompt: String, maxTokens: Int)

  def validatePrompt(raw: String): Either[Problem, String] =
    if (raw.trim.isEmpty) Left(BlankPrompt) else Right(raw)

  def validateLimit(n: Int): Either[Problem, Int] =
    if (n <= 0) Left(NonPositiveLimit) else Right(n)

  def request(raw: String, limit: Int): Either[Problem, Request] =
    for {
      prompt <- validatePrompt(raw)
      tokens <- validateLimit(limit)
    } yield Request(prompt, tokens)

  def promptLength(raw: String): Either[Problem, Int] =
    validatePrompt(raw).map(_.length)
}
```

The comprehension binds successful values to build a request. It returns the first error and skips `validateLimit` if the prompt fails. Although these particular checks are independent, this implementation chooses fail-fast semantics. If the UI needs all field issues, use an accumulating validation implementation or the project's existing validation helper. A method called `map2` alone does not guarantee accumulation.

`promptLength` maps an ordinary transformation over a contextual result. Neither example needs a custom Monad interface or effect runtime. As with the other examples, non-null typed inputs are assumed; validate untrusted boundaries separately.

## Applying the ideas to an AI agent workflow

For a workflow that retrieves documents, constructs a prompt, calls a model, validates output, and saves a result:

1. Keep document selection rules, prompt assembly from supplied content/configuration, and response-validation rules as separately testable calculations when practical.
2. Treat retrieval, model invocation, persistence, clock reads, and trace writes as effects. Capture their observations explicitly if replay is needed.
3. Record meaningful states such as `AwaitingContext`, `ReadyToGenerate`, `Generated`, and `Rejected`, each carrying the relevant values. A new hierarchy is useful only when it prevents actual invalid combinations or clarifies transitions.
4. Model dependent steps in order. Use bounded concurrency only for safe independent operations, such as independent read requests within service limits.
5. Test deterministic policy invariants separately from model-quality evaluation. A fixed request is not proof of deterministic output; replay tests may use recorded responses or a controlled interpreter.

These are adaptations to agent systems, not claims that the book presents LLM orchestration. Apply the parts that resolve concrete problems in the code under review.
