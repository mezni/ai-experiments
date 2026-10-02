# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adopts [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## Version History

| Version | Feature Domain | Key Objectives |
| --- | --- | --- |
| 0.0.52 | Retry execution | `RetryExecutor` drives attempt → backoff → retry, then acts on the recovery decision; each attempt emits its own span |
| 0.0.51 | Recovery vocabulary | `RecoveryStrategy` matches `ErrorCategories` constants instead of raw string literals |
| 0.0.50 | Composition root fix | `create_application(container=...)` no longer crashes building a generator from an injected container |
| 0.0.49 | Recovery strategy | `RecoveryStrategy.recover(failure)` maps an error category to `FAIL` / `FALLBACK` / `ESCALATE` with a stated reason |
| 0.0.48 | Exponential backoff | `ExponentialBackoff.calculate_delay(attempt)` returns a capped exponential delay — pure math, no sleeping |
| 0.0.47 | Retry decision | `RetryPolicy.should_retry()` returns `RetryDecision` carrying `retry`, `next_attempt`, and a human-readable `reason` |
| 0.0.46 | Retry policy | `RetryPolicy` makes the retry decision deterministic — `should_retry(failure, attempt)` consults `Failure.retryable` and the attempt budget |
| 0.0.45 | Failure object | `Failure` bundles error type, category, message, and retryability into one value object; span finish APIs take `failure` instead of loose error arguments |
| 0.0.44 | Error classification | `ErrorCategory` separates "what kind of failure" from `error_type` ("which exception"); `TelemetryEvent` carries both |
| 0.0.43 | Span status vocabulary | `SpanStatus` value object replaces the raw `status` string at span boundaries; `SpanStatuses` catalogue mirrors `Operations` |
| 0.0.42 | Span attributes | `TelemetryEvent` carries an open `attributes` map; spans can record operation-specific detail without widening the event schema |
| 0.0.41 | Operation vocabulary | `Operation` value object replaces the `event_type`/`operation` string pair; `Operations` catalogue centralizes the observability vocabulary |
| 0.0.40 | Application-owned trace | `Application` creates the `TraceContext` per request and injects it through service → generator; recorder is a required application dependency |
| 0.0.39 | Parent span linkage | TelemetryEvent + Span carry parent_span_id; Span.start() accepts an optional parent for trace tree stitching |
| 0.0.38 | Span helper | `Span` dataclass wraps span start/finish into a TelemetryEvent; generator uses it instead of manual event construction |
| 0.0.37 | Trace + span IDs | RequestContext gains trace_id + create_span_id(), TelemetryEvent carries trace_id/span_id for per-operation tracing |
| 0.0.36 | Generic telemetry event | GenerationEvent → TelemetryEvent, event_type discriminator, reusable across generation/tool calls |
| 0.0.35 | Cost on events | Generator computes generation cost, cost fields on GenerationEvent, pricing wired via composition root |
| 0.0.34 | Cost calculation | CostCalculator, deterministic cost math, pricing config with placeholder values |
| 0.0.33 | Token usage tracking | LLMUsage model, include_raw structured output, real provider token counts on telemetry + events |
| 0.0.32 | Telemetry recorder | TelemetryRecorderInterface contract, in-memory recorder, generator records success events |
| 0.0.31 | Generation event | GenerationEvent observability model, immutable telemetry, event test coverage |
| 0.0.30 | Structured logging | RequestContextFilter, StructuredLogger helper, request_id/operation fields on every log line, filter-safe formatting |
| 0.0.29 | Request context | Immutable RequestContext created at the application boundary, request_id flows through the full pipeline |
| 0.0.28 | Prompt manager interface | PromptManagerInterface contract, generator depends on the abstraction, fake implements the interface |
| 0.0.27 | Full dependency injection | Generator requires injected LLM + prompt manager, fakes isolate tests from the filesystem and model calls |
| 0.0.26 | Configuration boundary / composition root | Config stays the only source of settings, dependencies injected into the LLM adapter, composition root assembles the graph |
| 0.0.25 | Structured LLM abstraction | Clean StructuredLLMInterface, structured output owned by the adapter, no conditional branches |
| 0.0.24 | LLM dependency injection | LLMInterface, injectable LLM, fully testable generator without real calls |
| 0.0.23 | CLI separation | Dedicated CLI class, app.py reduced to a launcher, replaceable interaction surface |
| 0.0.22 | Typed request/response models | Input validation schemas, typed API response for the application layer |
| 0.0.21 | File-based versioned prompts | Prompt templates on disk, config selects active version |
| 0.0.20 | Prompt management | Dedicated PromptManager, prompt versioning, versioned telemetry |
| 0.0.19 | Application layer | Composition root, app factory, no direct generator construction |
| 0.0.18 | Interfaces / dependency inversion | ABC, abstract method, service depends on interface |
| 0.0.17 | Service layer | Service abstraction, dependency injection, fake-generator tests |
| 0.0.16 | Generation result | Typed result wrapper, access to blueprint + telemetry |
| 0.0.15 | Telemetry | Latency measurement, telemetry model, honest token tracking |
| 0.0.14 | Logging | Structured log format, request_id tracing, log configuration |
| 0.0.13 | Application exceptions | Custom error, exception chaining, input vs generation errors |
| 0.0.12 | Settings / environment config | pydantic-settings, .env loading, Settings model, settings tests |
| 0.0.11 | Configuration validation | Typed LLMConfig, field constraints, config tests |
| 0.0.10 | Configuration | YAML config management, model settings, config-driven LLM client |
| 0.0.9 | Testing | pytest, unit tests, validation tests |
| 0.0.8 | Structured LLM output | LangChain structured output + Pydantic schema integration |
| 0.0.7 | LangChain OpenRouter client | ChatOpenAI, temperature, message tuples, LLM invoke |
| 0.0.6 | Prompt engineering | System vs user prompts, instructions, constraints, output requirements |
| 0.0.5 | OpenRouter LLM client | LLM APIs, API keys, models, direct client configuration |
| 0.0.4 | Schema field validation | Field descriptions, input stripping, empty value prevention |
| 0.0.3 | Pydantic Blueprint schema | Pydantic, type safety, validation, structured data |
| 0.0.2 | Initial project structure | Starter file skeleton: app, generator, schemas, prompts, env example |
| 0.0.1 | Project foundation | Python project structure, uv, virtual environments, .env, Git |

---

## [0.0.52] - 2026-09-30

### Retry Execution

**Feature Domain:** Recovery

**Key Objectives:**

* Actually run the three recovery policies instead of only unit-testing them in isolation
* Keep the loop testable without wall-clock time by injecting the sleep function
* Preserve one telemetry span per attempt so a retried request stays fully observable
* Keep the generator a single-attempt unit of work

### Added

* `retry_executor.py` — `RetryExecutor.execute(operation, fallback=None, request_id=None)` drives the loop and returns an immutable `RetryOutcome(result, attempts, recovery_action, failure)`
* `retry_executor.py` — policies injected (`RetryPolicy`, `ExponentialBackoff`, `RecoveryStrategy`) plus an injectable `sleep` seam; defaults give 3 attempts and 1s/2s delays
* `service.py` — `ProjectBlueprintService` takes an optional `RetryExecutor` and a per-call `fallback`; `ProjectBlueprintService(generator)` still works unchanged
* `tests/test_retry_executor.py` — 10 tests: first-attempt success, retry-then-succeed, exact exponential delay sequence, attempt exhaustion, non-retryable skip, unclassified-error propagation, fallback on timeout, no-fallback on escalation, missing-fallback re-raise, `RetryOutcome` immutability
* `tests/fakes.py` — `FlakyLLM` that fails N times then succeeds
* `tests/test_service.py` — integration test proving 3 attempts produce 3 distinct spans under one `trace_id`, and that exhaustion re-raises with the span stack unwound

### Changed

* `exceptions.py` — `ProjectGenerationError` accepts an optional `Failure`, so the loop can see the classification the generator already computed
* `generator.py` — attaches that `Failure` when raising

### Why

`RetryPolicy`, `ExponentialBackoff` and `RecoveryStrategy` were each correct in isolation and completely inert in production: nothing called them. A value object that is never consulted is documentation, not a feature.

The loop lives in a `RetryExecutor` collaborator rather than inside `ProjectBlueprintService` or `ProjectGenerator` for three reasons. The service stays a thin use-case boundary; the executor is testable against a plain callable with no LLM, no filesystem and no clock; and `ProjectGenerator` keeps exactly one span per call, so a retried request records a sibling span per attempt rather than a single span spanning all attempts. That last property is what makes retry cost and latency attributable — the recovery table is per attempt, and aggregating it later is a query, not a guess.

The `sleep` seam is the load-bearing design choice: injecting it means the test suite asserts the *exact* delay sequence `[0.5, 1.5, 4.5, 13.5]` while the whole suite still runs in seconds. Delays are still real `time.sleep` in production because that is the executor's default.

Unclassified errors — a `ProjectGenerationError` with no `Failure` attached — propagate immediately instead of consuming the attempt budget. Retrying an error we cannot classify is how you turn a fast, clear failure into a slow, mysterious one.

Scope note: the `FALLBACK` path is fully implemented and tested, but no production fallback provider is wired. Falling back to a different model requires a second LLM, a pricing entry for it, and a config key to select it; inventing that here would have meant fabricating infrastructure. Until it exists, a `FALLBACK` decision with no `fallback` callable re-raises and logs, which is the honest behaviour. Each attempt also inherits the generator's coarse classification — every exception is currently `ErrorCategories.LLM` with `retryable=True` — so a validation error surfacing inside the LLM call would be retried. Narrowing that classification is the natural follow-up.

Tests: 80 → 92 passing.

---

## [0.0.51] - 2026-09-30

### Recovery Vocabulary

**Feature Domain:** Recovery

**Key Objectives:**

* Stop comparing failure categories against raw string literals
* Make an unrecognised category fail closed rather than matching by accident

### Changed

* `recovery.py` — `RecoveryStrategy.recover` matches `ErrorCategories.TIMEOUT` / `ErrorCategories.LLM` instead of `failure.category.value == "timeout"` / `"llm"`

### Added

* `tests/test_recovery.py` — matching is by value, not identity (an independently constructed `ErrorCategory("timeout")` still routes to `FALLBACK`); an unknown category falls through to `FAIL`

### Why

0.0.44 introduced `ErrorCategory` precisely so decisions would stop being string matching, and 0.0.49 then wrote exactly the string matching it was meant to replace. Had `errors.py` renamed `"timeout"` to `"request_timeout"`, `RecoveryStrategy` would have silently degraded to `FAIL` for every timeout — no exception, no warning, just a policy quietly doing the wrong thing.

Because `ErrorCategory` is a frozen dataclass with generated `__eq__`, the comparison stays by value, so a `Failure` deserialized from a log or a future API payload still matches the catalogue constant rather than requiring object identity.

Tests: 78 → 80 passing.

---

## [0.0.50] - 2026-09-30

### Composition Root Fix

**Feature Domain:** Application

**Key Objectives:**

* Fix a crash on the container-injection path
* Pin the behaviour with a regression test that fails on the old code

### Fixed

* `application.py` — `create_application` referenced `pricing_config` and `llm_config` when building a generator, but both were only bound inside the `if container is None` branch. Calling `create_application(container=container)` with no generator raised `UnboundLocalError`. The model is now read from `container.llm_config.model`, and `load_pricing_config()` is called only on the path that actually needs pricing.

### Added

* `tests/test_application.py` — `create_application` builds a real `ProjectGenerator` from an injected container, with `model_pricing` correctly populated from config
* `tests/test_application.py` — an unpriced model still raises `ValueError` naming the model, on the container path as well as the default one

### Why

The existing tests only ever passed *both* a container and a generator, which skipped the broken branch entirely — the bug was invisible to the suite, not merely untested. A composition root that cannot build its own object graph from a container it was handed is a real defect, not a cosmetic one, because container injection is the project's designated seam for testing without touching `.env` or `config/*.yaml`.

The pricing-miss guard is now covered on the container path too; previously that validation lived only in the branch that constructed the container, so a container built elsewhere bypassed the check.

Tests: 76 → 78 passing.

---

## [0.0.49] - 2026-09-30

### Recovery Strategy

**Feature Domain:** Recovery

**Key Objectives:**

* Decide what to do about a failure — fail, fall back, or escalate — as a pure function of its error category
* Introduce `RecoveryAction` as an explicit enum so recovery intent is not scattered string literals
* Give every decision a stated reason, matching `RetryDecision`

### Added

* `recovery.py` — `RecoveryAction(str, Enum)` with `FAIL` / `FALLBACK` / `ESCALATE`
* `recovery.py` — frozen `RecoveryDecision(action, reason)` validating a non-empty reason, and frozen `RecoveryStrategy.recover(failure)` mapping `ErrorCategories.TIMEOUT` → `FALLBACK`, `ErrorCategories.LLM` → `ESCALATE`, everything else → `FAIL`
* `tests/test_recovery.py` — timeout→fallback, llm→escalate, validation→fail, `RecoveryDecision` reason validation, immutability

### Why

Retry answers "should we try again?" and is exhausted on its own; recovery answers "if not, what now?" A timeout that survives its retries should fall back to another model or a degraded response rather than failing the request outright, while a validation error will never succeed no matter how many attempts it gets — treating both identically is what makes naive retry loops look worse than useless.

`RecoveryAction` as an enum rather than `"fail"` / `"fallback"` / `"escalate"` strings means a typo is an `AttributeError` at the call site instead of a branch that silently never matches. `str, Enum` keeps it directly usable as the enum-marker telemetry often expects.

Scope note: nothing calls `recover()` yet, and the strategy ignores `Failure.retryable` entirely — it keys only on `category`, so a retryable and a non-retryable timeout take the same path. Wiring the three policies together (`RetryPolicy.decide` → `ExponentialBackoff.calculate_delay` → `RecoveryStrategy.recover`) into an actual retry loop is the remaining work, tracked as Roadmap Step 22.

Tests: 71 → 76 passing.

---

## [0.0.48] - 2026-09-30

### Exponential Backoff

**Feature Domain:** Recovery

**Key Objectives:**

* Give the retry loop a delay schedule, completing the pure-policy trio (`RetryPolicy` decides *whether*, `ExponentialBackoff` computes *how long*)
* Keep the calculation free of side effects so it is testable without waiting
* Validate the policy's parameter relationships at construction rather than producing a nonsensical schedule later

### Added

* `backoff.py` — frozen `ExponentialBackoff` dataclass (`initial_delay_seconds=1.0`, `multiplier=2.0`, `max_delay_seconds=30.0`) with `calculate_delay(attempt)` returning `min(initial × multiplier^(attempt-1), max_delay)`
* `backoff.py` — `__post_init__` rejects a negative initial delay, a multiplier below 1, a negative max delay, and a max delay smaller than the initial delay; `calculate_delay` rejects `attempt < 1`
* `tests/test_backoff.py` — 9 tests: first-attempt delay, exponential growth (1/2/4/8), capping at the ceiling, `attempt >= 1` validation, all four construction validations, immutability

### Why

Retrying immediately on a rate-limited or overloaded provider is how a transient failure becomes a self-inflicted outage; the delay schedule is what makes retrying safe rather than aggressive.

Two decisions are baked in that are easy to get wrong by hand: the cap is applied *after* the exponentiation, so a large `attempt` cannot produce an unbounded delay before being clamped, and `max_delay_seconds >= initial_delay_seconds` is enforced up front, because a policy whose ceiling sits below its first delay would silently return the ceiling for every attempt — including the first — instead of failing loudly.

`calculate_delay` returns a number and never sleeps. The policy stays a value object, so the whole schedule is assertable in milliseconds and the actual waiting remains the caller's decision when the retry loop is wired up (Roadmap Step 22).

Scope note: nothing calls `calculate_delay` yet, and there is no jitter. Jitter matters in production — synchronized retries from many workers can re-create the thundering herd the backoff was meant to prevent — so expect it before this is used against a live provider.

Tests: 62 → 71 passing.

---

## [0.0.47] - 2026-09-30

### Retry Decision

**Feature Domain:** Recovery

**Key Objectives:**

* Rename `RetryPolicy.should_retry()` → `RetryPolicy.decide()` to reflect that it returns a decision, not a bare boolean
* Return a `RetryDecision` value object carrying `retry`, `next_attempt`, and a human-readable `reason` instead of a bare `bool`
* Make the decision self-describing, so a caller can log or surface *why* no retry happened

### Added

* `retry.py` — frozen `RetryDecision` dataclass (`retry: bool`, `next_attempt: int | None`, `reason: str`) enforcing three invariants in `__post_init__`: `reason` is non-empty, `next_attempt` is required when `retry is True`, and `next_attempt` must be `None` when `retry is False`
* `retry.py` — `RetryPolicy.decide(failure, attempt)` returns a `RetryDecision` with reason `"Failure is not retryable."`, `"Maximum retry attempts reached."`, or `"Failure is retryable and attempts remain."`
* `tests/test_retry.py` — rewritten around `create_retryable_failure()` / `create_non_retryable_failure()` helpers; 10 tests covering the three decision branches, `attempt >= 1` validation, all three `RetryDecision` invariants, and immutability

### Changed

* `retry.py` — `RetryPolicy.should_retry(failure, attempt) -> bool` replaced by `decide(failure, attempt) -> RetryDecision`. This is a rename, not a new capability: the same two conditions (retryable + attempts remain) decide the outcome, and the exhausted-budget branch moved from `attempt < max_attempts` to `attempt >= max_attempts` — equivalent for valid input, and now the documented way the boundary is expressed.

### Why

A bare `False` cannot distinguish "the caller sent invalid input", "this failure is permanent", and "we ran out of attempts". All three end retries, but only the last two are worth retrying later after human action, and they mean different things in a log. `RetryDecision.reason` makes the branch explicit at zero cost, and `next_attempt` hands the retry loop its next counter value instead of making it re-derive `attempt + 1`.

The `RetryDecision` invariants turn that contract into something the type system enforces: a decision claiming `retry=True` with no `next_attempt`, or `retry=False` while claiming an attempt, cannot be constructed. That is the same "validate once, at construction" discipline as `Operation` and `SpanStatus`.

Scope note: `RetryPolicy` is still not wired into the generator — nothing calls `decide()`, and there is no backoff or delay modelling (`max_attempts` bounds count only). Ahead of the recovery workflow, Roadmap Step 22.

Tests: 58 → 62 passing.

---

## [0.0.46] - 2026-09-30

### Retry Policy

**Feature Domain:** Recovery

**Key Objectives:**

* Make the retry decision a deterministic function of the failure and the attempt number, rather than something implied at each call site
* Give `Failure.retryable` (added in 0.0.45, previously dropped at the telemetry boundary) an actual consumer
* Encode the attempt budget as validated policy data instead of a hardcoded loop bound

### Added

* `retry.py` — frozen `RetryPolicy(max_attempts: int = 3)` validating the budget in `__post_init__`, and `should_retry(failure, attempt)` returning `False` for non-retryable failures or an exhausted budget, `True` otherwise; rejects `attempt < 1`
* `tests/test_retry.py` — `test_max_attempts_must_be_at_least_one`, `test_non_retryable_failure_is_not_retried`, `test_retryable_failure_is_retried`, `test_no_retry_after_max_attempts`, `test_attempt_must_be_at_least_one`, `test_one_attempt_means_no_retry`

### Why

Two conditions gate a retry, and they belong together: the failure must be retryable *and* attempts must remain. Expressing both in one predicate means a call site cannot accidentally retry a validation error by forgetting the flag, and the `max_attempts=1` case behaves correctly without special-casing.

`should_retry` is pure and takes no clock, network, or state — the decision is testable in isolation, which is the same discipline as `CostCalculator`. `attempt` is 1-based and validated, so an off-by-one in a future retry loop surfaces immediately instead of silently never retrying.

Scope note: `RetryPolicy` is not wired into the generator yet — nothing calls `should_retry`, and the generator still raises on the first LLM failure. This is the policy in isolation, ahead of the recovery workflow (Roadmap Step 22). There is also no backoff or delay modelling yet; `max_attempts` bounds count only.

Tests: 52 → 58 passing.

---

## [0.0.45] - 2026-09-30

### Failure Object

**Feature Domain:** Observability vocabulary

**Key Objectives:**

* Bundle everything known about a failure — type, category, message, retryability — into a single validated value object instead of separate parameters
* Replace the two-parameter `error_type` / `error_category` span API with one `failure` argument, so adding failure metadata later does not widen every call site
* Keep the recorded telemetry unchanged while the domain layer grows richer

### Added

* `failure.py` — frozen `Failure` dataclass (`error_type`, `category: ErrorCategory`, `message`, `retryable: bool = False`) validating `error_type` and `message`; `retryable` defaults to `False`
* `tests/test_failure.py` — `test_failure_requires_error_type`, `test_failure_requires_message`, `test_failure_defaults_to_not_retryable`, `test_failure_can_be_retryable`, `test_failure_is_immutable`
* `tests/test_tracing.py` — `test_span_records_failure` asserts a `Failure` reaches the recorded event as `status="error"` / `error_type="ProviderError"` / `error_category="llm"`

### Changed

* `tracing.py` — `Span.finish(error_type, error_category, ...)` and `TraceContext.finish_span(...)` replaced by `failure: Failure | None = None`; `Span.finish()` unpacks it into the existing event fields (`failure.error_type`, `failure.category.value`)
* `generator.py` — the error path builds a `Failure(category=ErrorCategories.LLM, message="LLM generation failed.", retryable=True)` and passes it to `finish_span`
* `tests/test_tracing.py` — `test_span_records_error_event` and `test_span_records_error_category` now pass a `Failure` instead of loose arguments

### Why

`error_type` and `error_category` were two parameters travelling together that always had to agree, and the next fact to record — a human-readable message, then whether a retry is worth attempting — would have meant a third and fourth. One `Failure` makes the pairing structural: it cannot be constructed with a category but no type, and adding `retryable` required no change to `Span.finish`'s signature at all.

The conversion at the event boundary is unchanged, so recorded telemetry is identical to 0.0.44: the event still carries `error_type` and `error_category` as plain strings, and `message` / `retryable` are not first-class fields on `TelemetryEvent`. `retryable` is dropped at the boundary — 0.0.46 gives it a consumer.

Tests: 46 → 52 passing.

---

## [0.0.44] - 2026-09-30

### Error Classification

**Feature Domain:** Observability vocabulary

**Key Objectives:**

* Record *what kind* of failure occurred separately from *which exception* was raised
* Give failure handling a controlled vocabulary (`validation` / `configuration` / `llm` / `timeout` / `internal`) that metrics and alerts can group on
* Follow the same value-object + catalogue pattern as `Operation` and `SpanStatus`

### Added

* `errors.py` — frozen `ErrorCategory` dataclass wrapping a `value` string, rejecting empty/whitespace-only values, plus an `ErrorCategories` catalogue (`VALIDATION`, `CONFIGURATION`, `LLM`, `TIMEOUT`, `INTERNAL`)
* `telemetry.py` — `TelemetryEvent.error_category: str | None = None`, placed directly after `error_type`
* `tracing.py` — `Span.finish(error_category: ErrorCategory | None = None)` and `TraceContext.finish_span(...)` accept and forward it; `Span.finish()` converts with `error_category.value if error_category is not None else None`
* `generator.py` — the generation span's error path records `error_category=ErrorCategories.LLM`
* `tests/test_errors.py` — `test_error_category_requires_value`, `test_error_categories`, `test_error_category_is_immutable`
* `tests/test_tracing.py` — `test_span_records_error_category` asserts the recorded event carries `status == "error"`, `error_type == "ProviderError"`, `error_category == "llm"`

### Why

`error_type` alone is ambiguous. `ValueError` could mean invalid user input, a malformed config file, or an internal programming mistake — all indistinguishable downstream. Pairing `error_category` (a controlled vocabulary) with `error_type` (the concrete exception) answers both *what kind of failure* and *which exception*, which is the distinction a metrics query needs: validation failures, LLM failures, and system failures are different signals with different owners and different responses.

Note: the generator's empty-`project_idea` guard still raises `ValueError` without a recorded event — it fires before any span is opened. Classifying it as `ErrorCategories.VALIDATION` will need the validation boundary to open its own span first; deferred until validation moves into its own layer (Roadmap Step 9).

`errors.py` (vocabulary) and `exceptions.py` (`ProjectGenerationError` hierarchy) are deliberately separate concerns: one classifies, the other structures.

Tests: 42 → 46 passing.

---

## [0.0.43] - 2026-09-30

### Span Status Vocabulary

**Feature Domain:** Observability vocabulary

**Key Objectives:**

* Replace the raw `status` string at span boundaries with a validated `SpanStatus` value object, completing the set begun with `Operation` (0.0.41)
* Keep `TelemetryEvent.status` a plain `str` so the recorded/external representation is unchanged
* Give the status vocabulary the same catalogue treatment as `Operations`

### Added

* `span_status.py` — frozen `SpanStatus` dataclass wrapping a `value` string, rejecting empty/whitespace-only values; `SUCCESS` / `ERROR` constants and a `SpanStatuses` catalogue
* `tests/test_span_status.py` — `test_span_status_requires_value`, `test_success_status`, `test_error_status`, `test_span_status_is_immutable`

### Changed

* `tracing.py` — `Span.finish(status: SpanStatus)` and `TraceContext.finish_span(status: SpanStatus)` now take a `SpanStatus`; `Span.finish()` converts at the boundary with `status=status.value` when building the `TelemetryEvent`
* `generator.py` — success and error paths pass `SpanStatuses.SUCCESS` / `SpanStatuses.ERROR`
* `tests/test_tracing.py` — span/trace finish calls use `SpanStatuses.*`; assertions still expect the string `"success"` / `"error"` on the recorded event

### Why

`status` was the last unchecked string in the tracing layer — `"sucess"` would have been accepted silently and only surfaced when reading dashboards. Making it a value object means the two legal states are named, validated, and discoverable in one place, matching how `Operation` already works.

The domain/representation split is deliberate: `SpanStatus` exists for the tracing layer's type safety, while `TelemetryEvent.status` stays `str` because that is the value that gets stored, exported, or sent to an observability backend. `status.value` is the single conversion point, and `test_tracing.py` asserting the string form is what proves the boundary holds.

Tests: 38 → 42 passing.

---

## [0.0.42] - 2026-09-30

### Span Attributes

**Feature Domain:** Observability vocabulary

**Key Objectives:**

* Give spans a way to record operation-specific detail without adding a new field to `TelemetryEvent` for every new kind of information
* Keep the event schema stable while `Operations` grows new scopes (agent, tool, retrieval, database, evaluation)
* Prove that `attributes` is genuinely optional — most events carry none

### Added

* `telemetry.py` — `TelemetryEvent.attributes: dict[str, Any] | None = None`, appended last so every existing positional construction and default is unaffected
* `tracing.py` — `Span.finish(..., attributes=None)` and `TraceContext.finish_span(..., attributes=None)` both accept and forward the map to the recorded event
* `generator.py` — the LLM generation span records `attributes={"provider": "openrouter"}` on success
* `tests/test_tracing.py` — `test_span_records_attributes` (arbitrary mixed-type values survive the round trip) and `test_span_attributes_are_optional` (an event finished without attributes has `attributes is None`)

### Why

Every new observability fact would otherwise mean widening `TelemetryEvent`: `provider` today, `retrieval_score` tomorrow, `tool_name` the day after. A generic map lets a span say something the fixed schema does not anticipate, so new operations can be observed without an event-shape change per fact. The typed fields stay for the data that is genuinely universal across operations (`status`, `latency_seconds`, tokens, cost) — the schema is not being abandoned, just no longer required to enumerate everything.

Known limitation: `attributes` is a `dict` on a `frozen=True` dataclass, so `frozen` does not make the contents immutable — a caller can mutate the dict after the event is recorded. If attributes become data that is queried or asserted on, copy the map at record time to restore the guarantee. Left as-is for now since nothing reads it yet.

The provider is hardcoded in the generator; it should come from `LLMConfig` once the adapter exposes it.

Tests: 36 → 38 passing.

---

## [0.0.41] - 2026-09-30

### Operation Vocabulary

**Feature Domain:** Observability vocabulary

**Key Objectives:**

* Replace the loose `event_type` / `operation` string pair carried by `Span` with a single validated `Operation` value object
* Centralize the observability vocabulary as named constants, collected in an `Operations` catalogue so callers reference one import
* Keep the telemetry boundary unchanged — `TelemetryEvent` still receives plain strings

### Added

* `operations.py` — frozen `Operation` dataclass (`event_type`, `name`) that rejects empty/whitespace-only values in `__post_init__`
* `operations.py` — operation constants for application, service, and llm scopes plus forward-looking `agent`, `tool`, `retrieval`, `database`, and `evaluation` scopes
* `operations.py` — `Operations` catalogue class exposing all constants as attributes
* `tests/test_operations.py` — `test_operation_requires_event_type`, `test_operation_requires_name`, `test_operation_is_immutable`, `test_operation_catalogue_contains_llm_operation`, `test_operation_catalogue_contains_agent_operation`

### Changed

* `tracing.py` — `Span` carries one `operation: Operation` field in place of the separate `event_type`/`operation` strings; `Span.start()` and `TraceContext.start_span()` both take an `Operation`; `Span.finish()` unpacks `operation.event_type` / `operation.name` into the `TelemetryEvent`, so the telemetry layer is unaffected
* `generator.py` — imports `Operations` and opens its span with `Operations.LLM_PROJECT_BLUEPRINT_GENERATION`
* `tests/test_tracing.py` — span/trace construction passes `Operation` values

### Why

Two strings travelling together are a pair that can disagree, and neither is checked at construction. Making them one immutable object means `event_type` and `name` are validated once, at creation, and travel as a unit. Naming the constants turns the observability vocabulary into a single importable surface: as agents, tools, retrieval, and evaluation arrive, the set of operations is enumerable in one place rather than scattered across call sites as string literals.

Note: the generator's `event_type` for this operation is `"llm"` (previously `"generation"`). `test_telemetry.py` still constructs `"generation"` and `"tool_call"` events directly, so both vocabularies currently appear in the suite.

Tests: 34 → 36 passing.

---

## [0.0.40] - 2026-09-30

### Application-Owned Trace

**Feature Domain:** Request trace ownership

**Key Objectives:**

* The application owns the request-level trace: it creates `RequestContext` + `TraceContext` and passes it down, instead of each layer re-deriving context
* The generator no longer creates or reaches for request identity — it consumes the `TraceContext` it is given
* `TraceContext` (already present since 0.0.38) becomes the only way spans are opened and closed in the generation path

### Added

* `application.py` — `Application.__init__` takes a `telemetry_recorder: TelemetryRecorderInterface` alongside `blueprint_service`; `generate_blueprint()` builds `TraceContext(context=RequestContext.create(), recorder=self.telemetry_recorder)` and passes it to the service
* `tests/test_application.py` — `CapturingGenerator` (a `ProjectGeneratorInterface` fake that stores the received trace) plus `test_application_creates_trace_context`, asserting the generator received a trace whose `context.request_id` equals the returned telemetry `request_id` and that the trace carries the application's recorder

### Changed

* `interfaces.py` — `ProjectGeneratorInterface.generate(project_idea, trace: TraceContext)` replaces the `context: RequestContext` parameter; `TraceContext` is imported under `TYPE_CHECKING` because `tracing.py` already imports `interfaces` (a runtime import would be circular)
* `service.py` — `generate_blueprint(project_idea, trace: TraceContext)` receives and forwards the trace unchanged
* `generator.py` — opens its span with `trace.start_span("generation", "project_blueprint_generation")` and closes it with `trace.finish_span(span, ...)` on both the success and error paths, replacing the direct `Span.start(context=..., recorder=...)` call; `request_id` is read once from `trace.context`; `latency_seconds` is captured into a local before `finish_span` (it is a live `perf_counter()` property and `finish_span` pops the span)
* `application.py` — `create_application()` hoists `telemetry_recorder = container.create_telemetry_recorder()` above the `if generator is None` branch so the recorder exists on every path (previously it was only created when building a default generator, which would leave `Application` without one when a generator was injected); the recorder is also passed to `Application`
* `tests/fakes.py` — `FakeProjectGenerator.generate()` takes a `TraceContext` and reads `request_id` from `trace.context`
* `tests/test_service.py`, `tests/test_generator.py` — construct a `TraceContext` (with `InMemoryTelemetryRecorder`) instead of passing a bare `RequestContext` to `generate()`

### Why

`TraceContext` already existed but was unused: the generator still started spans by passing `context` and `recorder` separately, so the trace hierarchy had no single owner. Moving trace creation to the application boundary means request identity is decided exactly once, per request, and every layer below receives it rather than reconstructing it. It also completes the migration started in 0.0.38 — `Span.start()` is now an internal detail of `TraceContext`, and call sites open and close spans through the helper, which is the shape later tool calls and agent steps will reuse.

Tests: 30 → 31 passing.

---

## [0.0.39] - 2026-09-23

### Parent Span Linkage

**Feature Domain:** Parent span linkage

**Key Objectives:**

* `TelemetryEvent` carries `parent_span_id` so child operations can be stitched into a trace tree
* `Span.start()` accepts an optional `parent_span_id` so nested spans are expressible declaratively
* A parent/child test proves the tree relationships (parent chain, shared trace)

### Added

* `tests/test_tracing.py` — `test_span_records_parent_span`: root span has `parent_span_id is None`, child links to the parent's `span_id`, and both share the same `trace_id`

### Changed

* `telemetry.py` — `TelemetryEvent` now requires `parent_span_id` (`str | None`) after `span_id`
* `tracing.py` — `Span` gains a `parent_span_id` field; `Span.start(..., parent_span_id=None)` records it; `finish()` passes it through to the `TelemetryEvent`
* `tests/test_telemetry.py`, `tests/test_telemetry_recorder.py` — event constructions pass `parent_span_id=None`

### Why

Trace trees need more than shared `request_id`/`trace_id`: knowing which span is the parent lets a collector reconstruct the call graph (agent → generation, orchestrator → tool call). With `parent_span_id` on both `Span` and `TelemetryEvent`, nesting is handled by the helper rather than hand-wired per call site.

---

### Span Helper

**Feature Domain:** Span helper

**Key Objectives:**

* `Span` dataclass owns one execution unit: `start()` opens a span, `finish()` closes it into a `TelemetryEvent`
* The generator records success and error events through the span instead of constructing `TelemetryEvent` manually
* Manual timing (`time.perf_counter()`) moves out of the generator into the span

### Added

* `tracing.py` — `Span` with `start(context, recorder, event_type, operation)` (captures `span_id` from `context.create_span_id()` and a start timestamp) and `finish(status, model, prompt_version, tokens, costs, error_type)` that builds and records a `TelemetryEvent`; a `latency_seconds` property exposes elapsed time
* `tests/test_tracing.py` — `test_span_records_success_event` (request/trace/span correlation, operation, model, non-negative latency) and `test_span_records_error_event` (error status + `error_type`)

### Changed

* `generator.py` — starts a `Span` before the LLM call; on success finishes the span with status/model/prompt version/tokens/costs; on failure finishes with `status="error"` and `error_type=type(exc).__name__`; the manual `TelemetryEvent` construction and `start_time`/`latency` timing are removed (`latency` read from `span.latency_seconds` for `GenerationTelemetry`)

### Why

The generator now expresses timing and event emission declaratively, while the span encapsulates the span-id assignment and record-on-finish mechanics. Every future operation (tool call, agent step) can reuse the same helper, keeping the recorder contract and `TelemetryEvent` shape uniform across the pipeline.

---

### Trace and Span IDs

**Feature Domain:** Trace + span IDs

**Key Objectives:**

* `RequestContext` gains a `trace_id` alongside `request_id`, distinguishing one request from a broader trace
* `TelemetryEvent` now carries `trace_id` and `span_id`, giving each individual operation within a trace its own identifier
* `RequestContext.create_span_id()` generates unique span IDs per execution unit

### Added

* `context.py` — `RequestContext` now has a `trace_id` field (generated in `create()`), plus a `create_span_id()` helper that returns a fresh `uuid4`
* `tests/test_context.py` — `test_request_context_generates_ids` asserts both `request_id` and `trace_id`; `test_span_ids_are_unique` asserts span IDs are non-empty and distinct

### Changed

* `telemetry.py` — `TelemetryEvent` now requires `trace_id` and `span_id` (in addition to `request_id`)
* `generator.py` — the recorded `TelemetryEvent` now passes `trace_id=context.trace_id` and `span_id=context.create_span_id()`
* `tests/test_telemetry.py` — generation and tool-call event tests now set and assert `trace_id` / `span_id`
* `tests/test_telemetry_recorder.py` — updated event construction with `trace_id` / `span_id`

### Why

One `request_id` is enough to correlate a single call, but not to track a multi-operation trace. With `trace_id` shared across the pipeline and `span_id` unique per operation (generation, tool call, agent step), every `TelemetryEvent` can later be stitched into a parent/child trace — the precondition for full observability as the system grows toward pipelines and agents.

---

### Generic Telemetry Event

**Feature Domain:** Generic telemetry event

**Key Objectives:**

* Replace the generation-specific `GenerationEvent` with a reusable `TelemetryEvent`
* `event_type` discriminates what happened (generation, tool call, ...) so the same recorder serves the whole pipeline
* Generation-specific fields (`model`, `prompt_version`, tokens, costs) become optional and stay populated only when relevant

### Changed

* `telemetry.py` — `GenerationEvent` removed; `TelemetryEvent` added with `request_id`, `event_type`, `operation`, `status`, `latency_seconds` as required fields and optional `model` / `prompt_version` / token / cost / `error_type` fields
* `interfaces.py` — `TelemetryRecorderInterface.record()` now takes a `TelemetryEvent`
* `telemetry_recorder.py` — `InMemoryTelemetryRecorder` stores `TelemetryEvent`s
* `generator.py` — records a `TelemetryEvent` with `event_type="generation"` and `operation="project_blueprint_generation"`
* `tests/test_telemetry.py` — rewritten: asserts full generation observability data (including `event_type` and `total_cost`) and a generic `tool_call` event where `model` and `input_tokens` default to `None`
* `tests/test_telemetry_recorder.py` — updated to record a `TelemetryEvent`

### Why

Observability should not leak generation-specific vocabulary into the recorder contract. A single generic event type lets agents, tools, and the LLM generation path emit uniform records through one recorder, with `event_type` distinguishing them — the precondition for tracing the whole pipeline under one `request_id`.

---

## [0.0.35] - 2026-09-21

### Cost on Events

**Feature Domain:** Cost on events

**Key Objectives:**

* The generator now computes generation cost and attaches it to the recorded event and telemetry
* Pricing is injected from configuration via the composition root — no pricing logic inside the generator
* Running without pricing for the configured model fails loudly instead of silently

### Added

* `GenerationEvent` cost fields — `input_cost`, `output_cost`, `total_cost` (optional, `None` when token usage is missing)

### Changed

* `generator.py` — `ProjectGenerator` now requires injected `cost_calculator: CostCalculator` and `model_pricing: ModelPricing`; after the LLM call it computes cost only when both input and output token counts are present, and records the cost values on the `GenerationEvent`
* `container.py` — adds `create_cost_calculator()`; the generator factory now receives the calculator and pricing
* `application.py` — composition root loads `load_pricing_config()`, validates the configured `llm_config.model` has pricing (raising `ValueError` otherwise), converts the `ModelPricingConfig` into a `ModelPricing`, and injects both
* `config/pricing.yaml` — adds the active model `nvidia/nemotron-3-ultra-550b-a55b:free` (zero-cost placeholder)
* `tests/test_generator.py` — asserts `input_cost == 0.0001`, `output_cost == 0.0001`, `total_cost == 0.0002` on the recorded event
* `tests/test_config.py` — `test_load_pricing_config` and `test_pricing_contains_configured_model` (guards against removing the model's pricing entry)

### Why

Cost is a per-model, config-driven fact, not code: the generator stays a pure consumer of `CostCalculator` + `ModelPricing`. Because cost depends on token usage, it stays `None` when the provider reports no usage. The missing-model guard prevents the application from silently running unmeasured.

---

## [0.0.34] - 2026-09-21

### Cost Calculation

**Feature Domain:** Cost calculation

**Key Objectives:**

* `CostCalculator` computes generation cost from token usage and model pricing
* Pricing lives in configuration, not hard-coded in Python — zero placeholders avoid embedding potentially outdated commercial rates
* Deterministic, tested math

### Added

* `cost.py` — frozen `ModelPricing` (input/output cost per million tokens), frozen `GenerationCost` (input, output, total), and `CostCalculator.calculate(pricing, input_tokens, output_tokens)`
* `config/pricing.yaml` — placeholder pricing (`0.0`) for `openai/gpt-4o-mini`; to be populated with verified rates later
* `config.py` — `ModelPricingConfig` (non-negative rate fields), `PricingConfig` (model → pricing mapping), `PRICING_CONFIG_PATH`, and `load_pricing_config()` with the same missing/empty guards as `load_llm_config()`
* `tests/test_cost.py` — asserts per-million math yields correct input/output/total costs, and that zero tokens cost zero

### Why

Token usage is now measured; cost is the next step. Calculation is pure deterministic math (the "AI for reasoning, code for guarantees" rule), so it belongs in a plain class. Pricing is deliberately kept out of the generator and out of code — no hard-coded per-model price branches — and sourced from configuration where it can later be verified and updated centrally.

---

## [0.0.33] - 2026-09-21

### Token Usage Tracking

**Feature Domain:** Token usage tracking

**Key Objectives:**

* `LLMUsage` model surfaces real provider-reported token counts through the LLM abstraction
* The `StructuredLLMInterface.generate()` contract now returns `(blueprint, usage)` instead of only the blueprint
* Generator telemetry and events carry `input_tokens`, `output_tokens`, and `total_tokens` — never invented numbers

### Added

* `interfaces.py` — frozen `LLMUsage` dataclass with optional `input_tokens` / `output_tokens` / `total_tokens`

### Changed

* `interfaces.py` — `StructuredLLMInterface.generate()` now returns `tuple[ProjectBlueprint, LLMUsage]`
* `structured_llm.py` — `with_structured_output(ProjectBlueprint, include_raw=True)` so both the parsed blueprint and the raw response metadata are available; `generate()` reads `usage_metadata` from the raw response and returns a `LLMUsage` (empty when metadata is absent)
* `generator.py` — unpacks `blueprint, usage = self.llm.generate(messages)`; the `GenerationTelemetry` and success `GenerationEvent` now include the real token counts from usage
* `tests/fakes.py` — `FakeLLM.generate()` returns a blueprint plus `LLMUsage(input=100, output=50, total=150)`
* `tests/test_generator.py` — asserts `result.telemetry.input_tokens == 100`, `output_tokens == 50`, `total_tokens == 150`, and the same on the recorded event

### Why

The blueprint alone discards provider-reported usage, so cost and token tracking stayed empty forever. Now the LLM abstraction is honest about usage: counts flow through telemetry and events when the provider reports them, and stay `None` otherwise — no invented figures (consistent with the honest-token-tracking principle).

---

## [0.0.32] - 2026-09-21

### Telemetry Recorder

**Feature Domain:** Telemetry recorder

**Key Objectives:**

* `TelemetryRecorderInterface` contract so event emission is injectable
* `InMemoryTelemetryRecorder` — a deterministic recorder for now, replaced by external sinks later
* The generator records a success `GenerationEvent` after the LLM call

### Added

* `interfaces.py` — `TelemetryRecorderInterface` with `record(event: GenerationEvent) -> None`
* `telemetry_recorder.py` — `InMemoryTelemetryRecorder` storing events in a list
* `tests/test_telemetry_recorder.py` — verifies the recorder stores the event and returns it as-is

### Changed

* `generator.py` — `ProjectGenerator.__init__` now requires an injected `telemetry_recorder: TelemetryRecorderInterface`; after the LLM call succeeds it records a `GenerationEvent` (`operation="project_blueprint_generation"`, `status="success"`, latency/model/prompt version)
* `container.py` — adds `create_telemetry_recorder()` and passes the recorder into `create_generator()`
* `application.py` — the composition root creates the recorder before assembling the generator
* `tests/test_generator.py` — instantiates `InMemoryTelemetryRecorder`, asserts exactly one event recorded with the matching `request_id`, `operation`, `status`, `model`, and `prompt_version`

### Why

Observability events are now emitted through an injectable contract rather than being fire-and-forget inside the generator. The in-memory recorder keeps tests deterministic and isolates event emission, and it can be swapped for a queue, file, or tracing backend without touching the generator.

---

## [0.0.31] - 2026-09-21

### Generation Event

**Feature Domain:** Generation event

**Key Objectives:**

* `GenerationEvent` observability model — a single record of a generation attempt (success or failure) that can be emitted for tracing
* Frozen telemetry dataclasses so records cannot be mutated after creation
* Test coverage for both the success and failure event shapes

### Added

* `telemetry.py` — `GenerationEvent` with `request_id`, `operation`, `model`, `prompt_version`, `status`, `latency_seconds`, optional token fields, and optional `error_type` for failure representation
* `tests/test_telemetry.py` — `test_generation_event_contains_observability_data` asserts all success fields; `test_generation_event_can_represent_failure` asserts the failure shape with `error_type`

### Changed

* `telemetry.py` — `GenerationTelemetry` is now frozen (`@dataclass(frozen=True)`) to keep telemetry immutable

### Why

Observability needs a single, structured record of each generation attempt — including failures — rather than only a success-only summary. A frozen `GenerationEvent` carrying `status` and optional `error_type` prepares the pipeline for event emission and tracing while telemetry stays honest (tokens remain optional).

---

## [0.0.30] - 2026-09-20

### Structured Logging

**Feature Domain:** Structured logging

**Key Objectives:**

* `request_id` and `operation` fields on every log line
* `StructuredLogger` helper so callers don't build `extra={...}` by hand
* `RequestContextFilter` keeps ordinary logs from crashing the formatter

### Added

* `logger.py` — `StructuredLogger` wrapping a `logging.Logger` with `info`/`error`/`exception`, each accepting `request_id` and `operation` keyword fields
* `logging_config.py` — `RequestContextFilter` defaults missing `request_id`/`operation` to `"-"`; `configure_logging()` installs a filtered `StreamHandler` on the root logger (clearing existing handlers)

### Changed

* `generator.py` — logger replaced with `self.logger = StructuredLogger(logging.getLogger(__name__))`; start, LLM-call, completion, and failure logs now emit fields `request_id=context.request_id` and an `operation` label (`generate_blueprint` / `llm_generation`)
* `cli.py` — `main()` calls `configure_logging()` before running

### Why

Log lines now carry structured context (`request_id`, `operation`) without callers hand-rolling `extra` dicts, and the filter guarantees any log that omits the fields still renders instead of raising. Structured output is safe for production aggregation and tracing.

---

## [0.0.29] - 2026-09-20

### Request Context

**Feature Domain:** Request context

**Key Objectives:**

* Frozen `RequestContext` — the request ID cannot change during processing
* Context created at the application boundary (start of the use case)
* `request_id` flows through service, generator, and telemetry

### Added

* `context.py` — frozen `RequestContext` dataclass with `create()` factory generating a `uuid4` request ID
* `tests/test_context.py` — verifies a 36-character request ID is created and immutability raises `AttributeError`

### Changed

* `application.py` — `generate_blueprint` creates `RequestContext` and passes it to the service
* `service.py` — `generate_blueprint(project_idea, context)` forwards the context to the generator
* `interfaces.py` — `ProjectGeneratorInterface.generate` now accepts `context: RequestContext`
* `generator.py` — no longer crafts its own request ID (`uuid` import removed); logging and telemetry read `context.request_id`
* `tests/fakes.py` — `FakeProjectGenerator` implements the new signature and echoes `context.request_id`
* `tests/test_generator.py`, `tests/test_application.py`, `tests/test_service.py` — updated for the new signature and assertions

### Why

Request identity is now owned by the application boundary and immutable for the life of the request, so every downstream layer traces logs and telemetry under the exact same `request_id` without anyone re-deriving it.

---

## [0.0.28] - 2026-09-20

### Prompt Manager Interface

**Feature Domain:** Prompt manager interface

**Key Objectives:**

* Introduce a `PromptManagerInterface` contract
* Generator depends on the abstraction, not the concrete `PromptManager`
* Fakes explicitly implement the interface

### Added

* `interfaces.py` — `PromptManagerInterface` with `get_system_prompt()`, `build_user_prompt(project_idea)`, `get_version()`

### Changed

* `prompt_manager.py` — `PromptManager` now implements `PromptManagerInterface`
* `generator.py` — `ProjectGenerator` accepts `prompt_manager: PromptManagerInterface`; no import or dependency on the concrete `PromptManager`
* `application.py` — the composition root creates the concrete `PromptManager()` and injects it into the generator
* `tests/fakes.py` — `FakePromptManager` explicitly implements `PromptManagerInterface`

### Why

The generator is now coupled only to a prompt contract, so the concrete manager is an implementation detail owned by the composition root. Real and fake prompt managers are interchangeable, keeping every layer testable without touching the filesystem.

---

## [0.0.27] - 2026-09-20

### Full Dependency Injection

**Feature Domain:** Full dependency injection

**Key Objectives:**

* Generator requires both `llm` and `prompt_manager` at construction time
* No optional/defaulted dependencies — composition root supplies everything
* Unit tests isolated from both the filesystem and model calls via fakes

### Changed

* `generator.py` — `ProjectGenerator.__init__` now takes `llm: StructuredLLMInterface` and `prompt_manager: PromptManager` (both required); the optional `prompt_manager` default and internal `PromptManager()` construction are removed
* `application.py` — the composition root now passes `prompt_manager=PromptManager()` when assembling the generator
* `tests/fakes.py` — adds `FakePromptManager` (`get_system_prompt`, `build_user_prompt`, `get_version`)
* `tests/test_generator.py` — `test_generator_uses_injected_dependencies` injects `FakeLLM` + `FakePromptManager` and asserts telemetry `model == "fake-model"` and `prompt_version == "test-v1"`

### Why

The generator no longer constructs anything itself or touches the filesystem: prompts come from an injected `PromptManager` fake, and generation comes from an injected LLM fake. Tests exercise the full flow in isolation, and production wiring lives solely in the composition root.

---

## [0.0.26] - 2026-09-20

### Configuration Boundary and Composition Root

**Feature Domain:** Configuration boundary / composition root

**Key Objectives:**

* Keep `config.py` as the single configuration boundary (settings + YAML)
* Inject dependencies into the LLM adapter instead of self-loading them
* Make the composition root (`create_application`) the only place that assembles the graph

### Changed

* `structured_llm.py` — `LangChainStructuredLLM.__init__` now receives `config: LLMConfig` and `settings: Settings` instead of loading them itself
* `application.py` — `create_application` loads settings + LLM config, builds `LangChainStructuredLLM(config=..., settings=...)`, and wires the generator; it remains the composition root
* `generator.py` — `ProjectGenerator` requires an injected `StructuredLLMInterface`; the default `LangChainStructuredLLM()` fallback is removed since the adapter no longer has a no-arg constructor

### Why

Dependencies flow inward instead of being fetched at point of use: `config.py` remains the configuration boundary, adapters receive ready-to-use dependencies, and the only place connecting pieces together is `create_application`. Swapping providers or wiring order is now a single composition-root change, and every layer stays testable with fakes.

---

## [0.0.25] - 2026-09-19

### Structured LLM Abstraction

**Feature Domain:** Structured LLM abstraction

**Key Objectives:**

* Replace the temporary `llm is None` branch with a clean, structured-output contract
* Own the LangChain wiring inside a dedicated adapter
* Keep the generator portable across providers/fakes through the interface

### Added

* `structured_llm.py` — `LangChainStructuredLLM` builds `ChatOpenAI` + `with_structured_output(ProjectBlueprint)` and exposes `model_name`

### Changed

* `interfaces.py` — `StructuredLLMInterface` with `generate(messages) -> ProjectBlueprint` and a `model_name` property
* `generator.py` — injects a `StructuredLLMInterface` directly, no conditional construction branch; telemetry reads `self.llm.model_name`
* `tests/fakes.py` — `FakeLLM` implements the `model_name` property + `generate`
* `tests/test_generator.py` — asserts telemetry `model == "fake-model"` and `prompt_version == "v1"`

### Why

Structured output is a property of the adapter, not the generator. The temporary branching is gone, the contract is uniform, and swapping OpenRouter for another provider or a fake is a single constructor choice.

---

## [0.0.24] - 2026-09-19

### LLM Dependency Injection

**Feature Domain:** LLM dependency injection

**Key Objectives:**

* Introduce an `LLMInterface` contract for model invocation
* Let `ProjectGenerator` accept an injected LLM (real or fake)
* Make the generator fully testable without OpenRouter calls

### Added

* `interfaces.py` — `LLMInterface` ABC with `invoke()`
* `tests/fakes.py` — `FakeLLM` returning a validated `ProjectBlueprint` (never contacts OpenRouter)
* `tests/test_generator.py` — verifies `ProjectGenerator` uses an injected LLM and records `prompt_version`

### Changed

* `generator.py` — constructor takes `llm` and `prompt_manager`; builds `ChatOpenAI` + `with_structured_output` only when no LLM is injected

### Why

The generator no longer hard-depends on OpenRouter: tests exercise the full generate flow with a fake, and model/provider switching is now a constructor choice — the payoff of the interface established earlier.

---

## [0.0.23] - 2026-09-19

### CLI Separation

**Feature Domain:** CLI separation

**Key Objectives:**

* Move all presentation/CLI concerns into a dedicated `CLI`
* Reduce `app.py` to a thin launcher
* Make the interaction surface replaceable (CLI, API, UI) without touching the application flow

### Added

* `cli.py` — `CLI` (builds the request, calls the application, formats/prints the response) plus a `main()` that reads `sys.argv`

### Changed

* `app.py` — reduced to `from cli import main; main()`

### Why

The business/application flow no longer depends on how the user interacts with the system — a key lesson: swap `CLI` for FastAPI, Streamlit, or a queue consumer without changing the service or generator.

---

## [0.0.22] - 2026-09-19

### Typed Request/Response Models

**Feature Domain:** Typed request/response models

**Key Objectives:**

* Validate input at the application boundary via `GenerateBlueprintRequest`
* Return a typed `GenerateBlueprintResponse` from the application layer
* Prepare the application interface for API/Streamlit/Web use

### Added

* `schemas.py` — `GenerateBlueprintRequest` (validated, whitespace-stripped project idea), `GenerateBlueprintResponse`, `GenerationTelemetryResponse`

### Changed

* `application.py` — `generate_blueprint(request)` accepts a request model and maps service telemetry into `GenerationTelemetryResponse`
* `app.py` — builds a `GenerateBlueprintRequest` and prints from the typed response fields
* `tests/test_schemas.py` — request validation, whitespace stripping, empty-input rejection, response construction
* `tests/test_application.py` — passes a `GenerateBlueprintRequest` to the application

### Why

The application layer now speaks typed request/response contracts rather than raw strings, so the same use case can be served by a CLI, API, or UI without changing core logic.

---

## [0.0.21] - 2026-09-19

### File-Based Versioned Prompts

**Feature Domain:** File-based versioned prompts

**Key Objectives:**

* Prompt templates stored as files under `prompts/<name>/<version>/`
* `config/prompts.yaml` selects the active prompt version and base path
* Configuration (not code) determines which prompt version is used

### Added

* `prompts/project_blueprint/v1/system.txt` — system prompt template
* `prompts/project_blueprint/v1/user.txt` — user prompt template with `{project_idea}` placeholder

### Changed

* `prompt_manager.py` rewritten to resolve `base_path/version/{system,user}.txt` from `config/prompts.yaml`, with `get_version()`
* `config/prompts.yaml` now includes `path: "prompts/project_blueprint"` alongside `version`
* `generator.py` obtains `prompt_version` from `self.prompt_manager.get_version()`
* `tests/test_prompt_manager.py` adds a version assertion (`get_version() == "v1"`)

### Removed

* `prompts.py` — replaced by the file-based prompt store
* Unused `PromptsConfig` + `load_prompts_config()` from `config.py`

### Why

Prompts are now versioned assets on disk; changing `config/prompts.yaml` swaps the active version without code changes, preparing for prompt regression testing and rollback.

---

## [0.0.20] - 2026-09-19

### Prompt Management

**Feature Domain:** Prompt management

**Key Objectives:**

* Dedicated `PromptManager` abstraction for prompt building
* Versioned prompts via `config/prompts.yaml`
* `prompt_version` recorded in telemetry

### Added

* `prompt_manager.py` — `PromptManager` wrapping `SYSTEM_PROMPT` and `build_user_prompt`
* `config/prompts.yaml` — `project_blueprint.version: "v1"`
* `tests/test_prompt_manager.py` — verifies system prompt content and user prompt embedding

### Changed

* `generator.py` injects `PromptManager` (optional) and builds messages through it; reads `prompt_version` from `config/prompts.yaml`
* `config.py` adds `PromptsConfig` + `load_prompts_config()`
* `telemetry.py` — `GenerationTelemetry` gains a `prompt_version` field
* `tests/test_service.py` and `tests/test_application.py` fakes include `prompt_version`

### Why

Prompts are now managed as a versioned asset (config-driven) rather than imports scattered through the generator, preparing for prompt evolution and regression tracking.

---

## [0.0.19] - 2026-09-18

### Application Layer

**Feature Domain:** Application layer

**Key Objectives:**

* Composition root (`Application` + `create_application`)
* Optional generator injection
* App no longer constructs the generator directly

### Added

* `application.py` — `Application` wrapping a `ProjectBlueprintService`, plus `create_application(generator=None)` that builds the default generator or accepts an injected one
* `tests/test_application.py` — verifies `create_application` with a fake generator (no LLM call)

### Changed

* `app.py` uses `create_application()` and no longer imports/constructs `ProjectGenerator`

---

## [0.0.18] - 2026-09-18

### Interfaces / Dependency Inversion

**Feature Domain:** Interfaces / dependency inversion

**Key Objectives:**

* `abc.ABC` + `@abstractmethod`
* Service depends on an abstraction, not a concrete implementation

### Added

* `interfaces.py` — `ProjectGeneratorInterface` with abstract `generate(project_idea)`

### Changed

* `generator.py` — `ProjectGenerator` implements `ProjectGeneratorInterface`
* `service.py` — `ProjectBlueprintService` accepts `ProjectGeneratorInterface`
* `tests/test_service.py` — `FakeProjectGenerator` implements the interface

---

## [0.0.17] - 2026-09-18

### Service Layer

**Feature Domain:** Service layer

**Key Objectives:**

* Service abstraction over the generator
* Dependency injection
* Testability without calling OpenRouter

### Added

* `service.py` — `ProjectBlueprintService` wraps a generator and exposes `generate_blueprint(project_idea)`
* `tests/test_service.py` — uses a `FakeProjectGenerator` (no LLM call) to verify the service returns the blueprint + telemetry

### Changed

* `app.py` instantiates `ProjectBlueprintService(generator)` and calls `service.generate_blueprint(...)`

---

## [0.0.16] - 2026-09-18

### Generation Result

**Feature Domain:** Generation result

**Key Objectives:**

* Typed result wrapper around blueprint + telemetry
* CLI surfaces request ID and latency

### Changed

* `telemetry.py` adds `GenerationResult` (`blueprint` + `telemetry`)
* `generator.py` `generate()` now returns `GenerationResult` instead of a bare `ProjectBlueprint`
* `app.py` uses `result.blueprint` and prints `Request ID` and `Latency` from `result.telemetry`

---

## [0.0.15] - 2026-09-18

### Telemetry

**Feature Domain:** Telemetry

**Key Objectives:**

* Latency measurement with `time.perf_counter()`
* `GenerationTelemetry` dataclass
* Honest token tracking — never invent token counts

### Added

* `telemetry.py` — `GenerationTelemetry` with `request_id`, `model`, `latency_seconds`, and optional `input_tokens`/`output_tokens`/`total_tokens` (default `None`)

### Changed

* `generator.py` times the LLM call, logs LLM response metadata (temporary inspection), and logs generation telemetry (model + latency) on success

---

## [0.0.14] - 2026-09-18

### Logging

**Feature Domain:** Logging

**Key Objectives:**

* Structured log format (timestamp, level, logger, message)
* `request_id` tracing across generation stages
* Centralized logging configuration

### Added

* `logging_config.py` — `configure_logging()` sets INFO level with a structured format

### Changed

* `generator.py` logs start, LLM call, completion, warning (empty input), and exception (with traceback) — each tagged with a per-request `request_id` (uuid)
* `app.py` calls `configure_logging()` before running

---

## [0.0.13] - 2026-09-18

### Application Exceptions

**Feature Domain:** Application exceptions

**Key Objectives:**

* Custom application exception
* Exception chaining (`raise ... from exc`)
* Input vs generation error separation

### Added

* `exceptions.py` — `ProjectGenerationError`

### Changed

* `generator.py` wraps any `structured_llm.invoke` failure in `ProjectGenerationError` (preserving the original via `from exc`)
* `app.py` catches `ValueError` (input error) and `ProjectGenerationError` (generation error) separately, exiting with a clear message for each

---

## [0.0.12] - 2026-09-18

### Settings / Environment Configuration

**Feature Domain:** Settings / environment configuration

**Key Objectives:**

* `pydantic-settings` `BaseSettings`
* `.env` loading via `SettingsConfigDict`
* API key as typed setting

### Added

* `config.py` adds `Settings` (`openrouter_api_key` min length 1) and `load_settings()` — reads `.env` with `extra="ignore"`
* `tests/test_settings.py` with a test that reads `OPENROUTER_API_KEY` from the environment via `monkeypatch`

### Changed

* `generator.py` replaces `load_dotenv`/`os.getenv` with `Settings` — API key now comes from `settings.openrouter_api_key`
* `pyproject.toml` adds `pydantic-settings` as a dependency

---

## [0.0.11] - 2026-09-18

### Configuration Validation

**Feature Domain:** Configuration validation

**Key Objectives:**

* Typed `LLMConfig` model
* Field constraints (`temperature` 0.0–2.0, `max_tokens` > 0)
* Config validation tests

### Changed

* `config.py` `load_llm_config()` now returns a typed `LLMConfig` via `model_validate` instead of a raw dict
* `generator.py` uses attribute access (`config.model`, `config.temperature`, ...)

### Added

* `tests/test_config.py` with 3 tests — accepts valid config, rejects invalid temperature, rejects invalid max_tokens

---

## [0.0.10] - 2026-09-18

### Configuration

**Feature Domain:** Configuration

**Key Objectives:**

* YAML config management
* Model settings (model, temperature, max_tokens, base_url)
* Config-driven LLM client

### Added

* `config/llm.yaml` — YAML config with `provider`, `base_url`, `model`, `temperature`, `max_tokens`
* `config.py` — `load_llm_config()` reads the YAML config and raises `FileNotFoundError` / `ValueError` for missing or empty config

### Changed

* `pyproject.toml` adds `pyyaml` as a dependency
* `generator.py` builds `ChatOpenAI` from the YAML config values

---

## [0.0.9] - 2026-09-18

### Phase 8 — Testing

**Feature Domain:** Testing

**Key Objectives:**

* pytest
* Unit tests
* Validation tests

### Added

* `tests/test_schemas.py` with 3 tests — accepts valid blueprint data, rejects empty `project_name`, rejects empty `business_outcome`

### Changed

* `pyproject.toml` adds `pytest` as a dev dependency
* `pyproject.toml` adds `[tool.pytest.ini_options]` (`pythonpath = ["."]`, `testpaths = ["tests"]`) so `pytest` resolves the project root imports

---

## [0.0.8] - 2026-09-18

### Phase 5 — Structured LLM Output

**Feature Domain:** Structured LLM output

**Key Objectives:**

* LangChain structured output
* Pydantic integration
* Output parsing
* Validation failures

### Added

* `generator.py` builds a `structured_llm` via `self.llm.with_structured_output(ProjectBlueprint)`

### Changed

* `generator.py` `generate()` now invokes the structured LLM and returns a typed `ProjectBlueprint` (instead of raw text)
* `app.py` prints the typed result via `blueprint.project_name` and `blueprint.business_outcome`
* `schemas.py` tightens field descriptions: concise meaningful name, and business outcome focused on measurable value rather than technical implementation

---

## [0.0.7] - 2026-09-18

### LangChain OpenRouter Client

**Feature Domain:** LangChain OpenRouter client

**Key Objectives:**

* LangChain `ChatOpenAI`
* Model and temperature configuration
* System/human message tuples
* `llm.invoke`

### Changed

* `generator.py` replaces the `openai` SDK client with LangChain `ChatOpenAI` (model `nvidia/nemotron-3-ultra-550b-a55b:free`, `temperature=0.2`, OpenRouter `base_url`)
* `generator.py` sends `("system", ...)` / `("human", ...)` message tuples and returns `response.content` from `llm.invoke`
* `generator.py` reads the API key from `OPENROUTER_API_KEY` (falling back to `OPENAI_API_KEY`), raises `ValueError` if missing, and passes it as `SecretStr`

---

## [0.0.6] - 2026-09-18

### Phase 4 — Prompt Engineering

**Feature Domain:** Prompt engineering

**Key Objectives:**

* System vs user prompts
* Instructions
* Constraints
* Output requirements

### Added

* `prompts.py` adds `SYSTEM_PROMPT` — an AI architecture assistant that asks for a project name and business outcome while forbidding technical architecture design
* `prompts.py` adds `build_user_prompt(project_idea)` — wraps the project idea into a user prompt

### Changed

* `generator.py` now sends `SYSTEM_PROMPT` (system) and `build_user_prompt(project_idea)` (user) to the OpenRouter LLM

---

## [0.0.5] - 2026-09-18

### Phase 3 — OpenRouter LLM Client

**Feature Domain:** OpenRouter LLM client

**Key Objectives:**

* LLM APIs
* API keys
* Models
* Direct client configuration

### Added

* `generator.py` adds `ProjectGenerator` — an OpenRouter LLM client (via the `openai` SDK) that raises `ValueError` when `OPENROUTER_API_KEY` is not configured

### Changed

* `app.py` uses `ProjectGenerator` to generate a response for "Build an AI system that classifies corporate documents."

---

## [0.0.4] - 2026-09-18

### Schema Field Validation

**Feature Domain:** Schema field validation

**Key Objectives:**

* `Field` descriptions
* `field_validator`
* Input stripping
* Empty value prevention

### Changed

* `schemas.py` adds `Field` descriptions to `project_name` and `business_outcome`
* `schemas.py` adds a `field_validator` that strips whitespace and raises `ValueError` ("Value cannot be empty.") for empty values on both fields
* `app.py` verifies valid data still validates and dumps correctly

---

## [0.0.3] - 2026-09-18

### Phase 2 — Pydantic Blueprint Schema

**Feature Domain:** Pydantic Blueprint schema

**Key Objectives:**

* `BaseModel`
* Type hints and fields
* Validation
* Structured data

### Changed

* `schemas.py` now defines `ProjectBlueprint` with `project_name` and `business_outcome` fields (replaces the starter `ProjectIdea`/`Blueprint` placeholders)
* `app.py` tests the schema without an LLM — builds a `ProjectBlueprint`, prints it, and prints `model_dump()`

---

## [0.0.2] - 2026-09-18

### Initial Project Structure

**Feature Domain:** Initial project structure

**Key Objectives:**

* Deploy the starter file skeleton for the blueprint generator
* Define environment variable names for configuration

### Added

* `.env.example` with the documented variable names
* `app.py` minimal entry point (`main()` prints the generator name)
* `generator.py` placeholder `generate_blueprint(idea)`
* `schemas.py` starter Pydantic models (`ProjectIdea`, `Blueprint`)
* `prompts.py` initial system prompt

---

## [0.0.1] - 2026-09-18

### Phase 1 — Project Foundation

**Feature Domain:** Project foundation

**Key Objectives:**

* Python project structure
* `uv` project management
* Virtual environments
* `.env` configuration
* Git version control
* Dependencies

### Added

* `pyproject.toml` with project metadata and core dependencies (langchain, langchain-openrouter, pydantic, python-dotenv)
* `uv.lock` lockfile
* `.env` template for `OPENROUTER_API_KEY` and `OPENROUTER_MODEL` configuration
* `.gitignore` for virtual environments, environment files, and Python caches
* `README.md` project documentation
* `docs/ROADMAP.md` learning roadmap
* `docs/SESSION_HANDOFF.md` session handoff document
* `CHANGELOG.md` changelog with version history
* Initial Git repository## [0.0.40] - 2026-09-25

### Trace Context

**Feature Domain:** Trace context

**Key Objectives:**

* Automatic parent span detection from the active span stack
* LIFO enforcement for span finish order
* Hierarchical trace tree building without explicit `parent_span_id`

### Added

* `tracing.py` — `TraceContext` class with `start_span(event_type, operation)` and `finish_span(span, ...)` methods; `current_span_id` property
* `tests/test_tracing.py` — `test_trace_context_creates_parent_child_relationships`, `test_trace_context_finishes_spans_in_lifo_order`, `test_trace_context_records_nested_events`

### Why

Spans can now be started without manually passing `parent_span_id` — `TraceContext` automatically assigns the currently active span as the parent. This enables natural hierarchical trace trees (agent → generation → tool → database) and enforces LIFO finish order to prevent invalid traces.
