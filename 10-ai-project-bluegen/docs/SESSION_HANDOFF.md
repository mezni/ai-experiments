# Session Handoff

Date: 2026-09-30

## Project State

An agentic AI learning project that transforms a simple AI project idea into a structured, implementation-ready architecture blueprint. Built progressively with Python, Pydantic, LangChain, and OpenRouter.

Current stage: **Level 1 — Structured LLM** functional end-to-end, behind a clean layered architecture with fully injected dependencies, a container-based composition root, application-owned request tracing, a typed observability vocabulary, deterministic cost calculation, and a wired retry/backoff/recovery loop. The `FALLBACK` recovery action has no production fallback provider yet.

```text
app.py (launcher)
   → CLI (cli.py — replaceable presentation layer)
      → Application (application.py — creates RequestContext + TraceContext at the use-case boundary)
         → ProjectBlueprintService (service.py — owns a RetryExecutor, forwards the trace)
            → RetryExecutor (retry_executor.py — the loop; owns no business logic)
               → ProjectGeneratorInterface (interfaces.py, ABC — generate(project_idea, trace))
                  → ProjectGenerator (generator.py — ONE attempt = ONE span)
                     ├── PromptManagerInterface (interfaces.py, ABC)
                     │   ├── PromptManager (prompt_manager.py) → prompts/<name>/<version>/*.txt
                     │   └── FakePromptManager / FlakyLLM (tests/fakes.py)
                     ├── StructuredLLMInterface (interfaces.py, ABC)
                     │   ├── LangChainStructuredLLM (structured_llm.py) → ChatOpenAI → OpenRouter
                     │   └── FakeLLM (tests/fakes.py)
                     ├── TelemetryRecorderInterface (interfaces.py, ABC)
                     │   └── InMemoryTelemetryRecorder (telemetry_recorder.py)
                     ├── CostCalculator (cost.py — deterministic math)
                     └── ModelPricing (from config/pricing.yaml via composition root)
   object graph assembled by DependencyContainer (container.py) via create_application (application.py)
   observability: TelemetryEvent (telemetry.py) — event_type, usage (tokens), cost (optional), attributes
   tracing: TraceContext (tracing.py) — owns the span stack; start_span/finish_span emit a
            TelemetryEvent with trace_id, span_id, parent_span_id; Span is an internal detail
   typed vocabulary (frozen value objects, one catalogue each):
      Operation + Operations          (operations.py)  — event_type + name
      SpanStatus + SpanStatuses        (span_status.py) — success / error
      ErrorCategory + ErrorCategories  (errors.py)      — validation/configuration/llm/timeout/internal
      Failure                          (failure.py)     — error_type + category + message + retryable
   recovery policies (pure, injected into RetryExecutor, all covered by tests):
      RetryPolicy.decide(failure, attempt) → RetryDecision  (retry.py)
      ExponentialBackoff.calculate_delay(attempt) → float    (backoff.py)
      RecoveryStrategy.recover(failure) → RecoveryDecision  (recovery.py)
```

Key properties:

* The application flow depends only on typed contracts (`GenerateBlueprintRequest`/`GenerateBlueprintResponse`).
* `config.py` is the single configuration boundary — `Settings` (from `.env`), `LLMConfig` (`config/llm.yaml`), and `PricingConfig` (`config/pricing.yaml`).
* `DependencyContainer` knows how to construct infrastructure only; it never executes use cases. The composition root (`create_application`) accepts an injected generator and/or container for tests, and works on both paths.
* `RequestContext` is frozen and created at the application boundary; its `request_id` threads through service → generator → telemetry → logs → events.
* **The application owns the request trace.** It creates `RequestContext` *and* `TraceContext` once per request and passes it down through service → generator. No layer below re-derives context, and the generator never creates request identity.
* `TraceContext` (tracing.py) owns the span stack: `start_span(operation: Operation)` opens a span and auto-links it to the enclosing one via `parent_span_id`; `finish_span(span, status: SpanStatus, ...)` records exactly one `TelemetryEvent` and pops it. Spans must be finished in LIFO order. `Span` itself is an internal detail of `TraceContext` — call sites no longer call `Span.start(...)` directly.
* **The generator is a single-attempt unit of work.** The retry loop lives in `RetryExecutor`, one layer above it, so each attempt re-enters the generator and emits its own span. A retried request therefore records sibling spans (distinct `span_id`, one `trace_id`), which is what makes retry cost and latency attributable.
* **The sleep function is injected.** `RetryExecutor(sleep=...)` defaults to `time.sleep` in production, and tests pass a no-op, so the exact delay sequence is assertable while the suite still runs in seconds.
* Every log line carries `request_id` and `operation` fields via `StructuredLogger` + `RequestContextFilter`; ordinary logs that omit the fields still render.
* Observability is a single generic `TelemetryEvent` (`event_type` discriminates generation / tool call / agent operations); `request_id` correlates all events for one request.
* Trace hierarchy is explicit: `trace_id` groups the request pipeline, `span_id` identifies each unit of work, and `parent_span_id` links child spans to their parent so a collector can reconstruct the call graph (agent → generation, orchestrator → tool call).
* `interfaces.py` imports `TraceContext` under `TYPE_CHECKING` only — `tracing.py` already imports `interfaces`, so a runtime import would be circular.
* **The observability vocabulary is typed.** `Operation` (event_type + name), `SpanStatus` (success/error), `ErrorCategory` (validation/configuration/llm/timeout/internal), `Failure` (error_type + category + message + retryable), `RetryDecision`, `RecoveryAction` — each a frozen, validated value object with a `*s`/`*es` catalogue class. All are collected in `Operations`, `SpanStatuses`, `ErrorCategories`.
* **The domain/representation boundary is explicit:** tracing APIs take the typed objects (`SpanStatus`, `Failure`, `ErrorCategory`), and `Span.finish()` is the single conversion point where they become the plain strings on `TelemetryEvent`. Telemetry stays a flat, storable record.
* Token usage is honest: `LangChainStructuredLLM` reads provider-reported `usage_metadata` (via `include_raw`) into `LLMUsage`; counts stay `None` when the provider reports nothing.
* Cost is deterministic math (`CostCalculator`) driven by injected `ModelPricing` from `config/pricing.yaml` — no per-model pricing branches in code, no stale prices embedded.
* The generator records one `TelemetryEvent` per attempt (status, latency, tokens, cost, failure classification, `attributes={"provider": "openrouter"}`) through the injectable `TelemetryRecorderInterface`.
* Structured output is owned by the `LangChainStructuredLLM` adapter, not spread through the generator.
* Prompts are versioned files on disk; `config/prompts.yaml` selects the active version; the version is recorded in telemetry.

## Completed

| Release | Feature Domain | What was built |
| --- | --- | --- |
| 0.0.52 | Retry execution | `RetryExecutor` drives attempt → backoff → retry, then acts on the recovery decision; each attempt emits its own span; injected `sleep` |
| 0.0.51 | Recovery vocabulary | `RecoveryStrategy` matches `ErrorCategories` constants; unknown categories fail closed to `FAIL` |
| 0.0.50 | Composition root fix | `create_application(container=...)` no longer crashes building a generator from an injected container; pricing-miss guard covered on both paths |
| 0.0.49 | Recovery strategy | `RecoveryStrategy.recover(failure)` maps error category → `FAIL`/`FALLBACK`/`ESCALATE`; `RecoveryAction` enum; decisions carry a reason |
| 0.0.48 | Exponential backoff | `ExponentialBackoff.calculate_delay(attempt)` — capped exponential delay, validated at construction, never sleeps |
| 0.0.47 | Retry decision | `RetryPolicy.should_retry()` → `decide()` returning `RetryDecision` (`retry`, `next_attempt`, `reason`) with enforced invariants |
| 0.0.46 | Retry policy | `RetryPolicy(max_attempts=3)` — deterministic retry decision from `Failure.retryable` + attempt budget |
| 0.0.45 | Failure object | `Failure` bundles error_type + category + message + retryable; `Span.finish(failure=...)` replaces loose error args |
| 0.0.44 | Error classification | `ErrorCategory` separates failure *kind* from exception *type*; `TelemetryEvent.error_category` added |
| 0.0.43 | Span status vocabulary | `SpanStatus` (success/error) + `SpanStatuses`; tracing APIs take it, telemetry keeps `str` |
| 0.0.42 | Span attributes | `TelemetryEvent.attributes` — open map for operation-specific detail without widening the schema |
| 0.0.41 | Operation vocabulary | `Operation` (event_type + name) + `Operations` catalogue; `Span` carries one instead of two strings |
| 0.0.40 | Application-owned trace | `Application` creates `TraceContext` per request and injects it through service → generator; `generate(project_idea, trace)` contract |
| 0.0.39 | Parent span linkage | `TelemetryEvent` + `Span` carry `parent_span_id`; `Span.start()` accepts an optional parent |
| 0.0.38 | Span helper | `Span` dataclass (`start`/`finish`) emits a `TelemetryEvent`; manual timing + event construction removed |
| 0.0.37 | Trace + span IDs | `RequestContext` gains `trace_id` + `create_span_id()`; `TelemetryEvent` carries `trace_id`/`span_id` |
| 0.0.36 | Generic telemetry event | `GenerationEvent` → `TelemetryEvent` (adds `event_type`, optional model/tokens/cost fields) |
| 0.0.35 | Cost on events | Generator computes cost and records it on the event; composition root validates model pricing exists |
| 0.0.34 | Cost calculation | Deterministic `CostCalculator` + typed pricing config (`config/pricing.yaml`, placeholder zeros) |
| 0.0.33 | Token usage tracking | `LLMUsage`; LLM abstraction returns `(blueprint, usage)`; provider token counts on telemetry + events |
| 0.0.32 | Telemetry recorder | `TelemetryRecorderInterface` + `InMemoryTelemetryRecorder`; generator records success events |
| 0.0.31 | Generation event | Frozen `GenerationEvent` (status, latency, optional tokens, `error_type`); success/failure tests |
| 0.0.30 | Structured logging | `StructuredLogger` + `RequestContextFilter`; `request_id`/`operation` on every log line |
| 0.0.29 | Request context | Frozen `RequestContext` created at the application boundary; `request_id` flows through the pipeline |
| 0.0.28 | Prompt manager interface | `PromptManagerInterface`; generator depends on abstraction; `FakePromptManager` implements it |
| 0.0.27 | Full dependency injection | Generator requires injected LLM + prompt manager; tests need no filesystem |
| 0.0.26 | Configuration boundary / composition root | LLM adapter receives `config` + `settings` via constructor; generator requires injected LLM |
| 0.0.25 | Structured LLM abstraction | `StructuredLLMInterface`, `LangChainStructuredLLM` adapter, no conditional branches |
| 0.0.24 | LLM dependency injection | `LLMInterface`, injectable LLM, fully testable generator without real calls |
| 0.0.23 | CLI separation | Dedicated `CLI`, `app.py` reduced to a launcher, replaceable interaction surface |
| 0.0.22 | Typed request/response models | Input validation schemas, typed API response for the application layer |
| 0.0.21 | File-based versioned prompts | `prompts/project_blueprint/v1/`, config selects active version |
| 0.0.20 | Prompt management | Dedicated `PromptManager`, prompt versioning, versioned telemetry |
| 0.0.19 | Application layer | `Application` + `create_application(generator=None)` composition root |
| 0.0.18 | Interfaces / dependency inversion | ABC, abstract method, service depends on interface |
| 0.0.17 | Service layer | `ProjectBlueprintService`, dependency injection, fake-generator test |
| 0.0.16 | Generation result | `GenerationResult` (blueprint + telemetry) |
| 0.0.15 | Telemetry | `telemetry.py` `GenerationTelemetry` (latency, honest optional token fields) |
| 0.0.14 | Logging | Structured log format, `request_id` tracing, log configuration |
| 0.0.13 | Application exceptions | `exceptions.py` (`ProjectGenerationError`), chained wrapping, input vs generation errors |
| 0.0.12 | Settings / environment config | `pydantic-settings` `Settings`, `.env` loading, `Settings` model, settings tests |
| 0.0.11 | Configuration validation | Typed `LLMConfig`, field constraints, config tests |
| 0.0.10 | Configuration | YAML config management, model settings, config-driven LLM client |
| 0.0.9 | Testing | pytest, unit tests, validation tests |
| 0.0.8 | Structured LLM output | LangChain structured output + Pydantic schema integration |
| 0.0.7 | LangChain OpenRouter client | `ChatOpenAI`, temperature, message tuples, LLM invoke |
| 0.0.6 | Prompt engineering | System vs user prompts, instructions, constraints, output requirements |
| 0.0.5 | OpenRouter LLM client | LLM APIs, API keys, models, direct client configuration |
| 0.0.4 | Schema field validation | Field descriptions, input stripping, empty value prevention |
| 0.0.3 | Pydantic Blueprint schema | Pydantic, type safety, validation, structured data |
| 0.0.2 | Initial project structure | Starter file skeleton: app, generator, schemas, prompts, env example |
| 0.0.1 | Project foundation | Python project structure, uv, virtual environments, .env, Git |

Test status: **92 passed** across 21 test modules.

## Current Structure

```text
ai-project-bluegen/
│
├── app.py                  # Launcher: from cli import main
├── cli.py                  # CLI: configure_logging, args → request → application → formatted output (replaceable)
├── application.py          # Application + create_application (composition root, creates RequestContext + TraceContext)
├── container.py            # DependencyContainer: prompt manager / structured LLM / recorder / cost / generator / service
├── context.py              # RequestContext (frozen request_id + trace_id, create(), create_span_id())
├── service.py              # ProjectBlueprintService (receives the TraceContext, forwards it to the generator)
├── interfaces.py           # ProjectGeneratorInterface + StructuredLLMInterface + PromptManagerInterface
│                           #   + TelemetryRecorderInterface (ABCs), LLMUsage; TraceContext under TYPE_CHECKING
├── generator.py            # ProjectGenerator: injectable, opens/closes spans via TraceContext, records usage + cost
├── structured_llm.py       # LangChainStructuredLLM: ChatOpenAI + with_structured_output(include_raw=True)
├── prompt_manager.py       # PromptManager: loads versioned prompt files (implements PromptManagerInterface)
├── logger.py               # StructuredLogger: info/error/exception with request_id/operation extras
├── tracing.py              # TraceContext: owns the span stack (start_span/finish_span, LIFO); Span is internal
├── schemas.py              # ProjectBlueprint, GenerateBlueprintRequest/Response, GenerationTelemetryResponse
├── exceptions.py           # ProjectGenerationError
├── telemetry.py            # GenerationTelemetry, TelemetryEvent, GenerationResult (frozen dataclasses)
├── telemetry_recorder.py   # InMemoryTelemetryRecorder (stores TelemetryEvent list)
├── cost.py                 # ModelPricing, GenerationCost, CostCalculator (deterministic)
├── operations.py           # Operation (event_type + name) + Operations catalogue
├── span_status.py          # SpanStatus (value) + SUCCESS/ERROR + SpanStatuses catalogue
├── errors.py               # ErrorCategory + ErrorCategories (validation/configuration/llm/timeout/internal)
├── failure.py              # Failure (error_type + category + message + retryable)
├── retry.py                # RetryDecision + RetryPolicy.decide(failure, attempt)
├── backoff.py              # ExponentialBackoff.calculate_delay(attempt) — capped, never sleeps
├── recovery.py             # RecoveryAction enum + RecoveryDecision + RecoveryStrategy.recover(failure)
├── retry_executor.py       # RetryExecutor.execute(operation, fallback) + RetryOutcome — the retry loop
├── logging_config.py       # RequestContextFilter + configure_logging() (StreamHandler, clears handlers)
├── config.py               # Settings (env) + LLMConfig + PricingConfig + loaders — the configuration boundary
├── config/
│   ├── llm.yaml            # provider, base_url, model, temperature, max_tokens
│   ├── prompts.yaml        # project_blueprint: version + path
│   └── pricing.yaml        # model → cost-per-million-tokens (placeholder zeros pending verified rates)
├── prompts/
│   └── project_blueprint/
│       └── v1/
│           ├── system.txt  # system prompt template
│           └── user.txt    # user prompt template ({project_idea})
├── tests/
│   ├── fakes.py            # FakeLLM, FlakyLLM (fails N then succeeds), FakePromptManager, FakeProjectGenerator
│   ├── test_schemas.py     # request/response schema tests
│   ├── test_config.py      # LLMConfig + pricing config validation
│   ├── test_settings.py    # Settings/.env
│   ├── test_prompt_manager.py
│   ├── test_context.py     # RequestContext creation + immutability
│   ├── test_tracing.py     # Span/TraceContext: success, error, parent/child, LIFO, attributes, failure
│   ├── test_service.py     # fake generator + injected TraceContext
│   ├── test_application.py # fake generator + injected container; CapturingGenerator trace-ownership test
│   ├── test_generator.py   # fake LLM + fake prompts + recorder + cost through the real generator
│   ├── test_telemetry.py   # TelemetryEvent data + generic (tool_call) shape
│   ├── test_telemetry_recorder.py
│   ├── test_cost.py        # cost math + zero-token case
│   ├── test_operations.py  # Operation validation/immutability + Operations catalogue
│   ├── test_span_status.py # SpanStatus validation/immutability + SpanStatuses catalogue
│   ├── test_errors.py      # ErrorCategory validation/immutability + ErrorCategories
│   ├── test_failure.py     # Failure validation, retryable default, immutability
│   ├── test_retry.py       # RetryPolicy.decide branches + RetryDecision invariants
│   ├── test_backoff.py     # exponential growth, capping, construction validation
│   ├── test_recovery.py    # category → FAIL/FALLBACK/ESCALATE mapping, value-vs-identity, fail-closed
│   └── test_retry_executor.py # attempt loop, backoff sequence, fallback/escalate, unclassified errors
├── .env                    # OPENROUTER_API_KEY (set), OPENROUTER_MODEL
├── .env.example
├── .gitignore
├── pyproject.toml
├── uv.lock
├── CHANGELOG.md            # 0.0.1–0.0.52 (newest first)
├── README.md               # Full 21-section project document
├── docs/
│   ├── ROADMAP.md          # 42-step roadmap with status markers (8✅ / 2◐ / 32⬜)
│   ├── STEPS.md            # granular learning steps 1–52 with "choices + why"
│   └── SESSION_HANDOFF.md  # this file
└── .venv/
```

## Key Decisions

* Start simple; add complexity only when it solves a real problem.
* Use AI for ambiguity and reasoning; use deterministic Python for rules and guarantees — cost math is a plain class, never an LLM call.
* Each increment of work = next `0.0.x` release; entries added to `CHANGELOG.md` only as work completes.
* Building convention: `concept → implementation → failure modes` at each step.
* Not jumping directly to a multi-agent system; evolving Level 1 → pipeline → agentic.
* Depend on abstractions (`ProjectGeneratorInterface`, `StructuredLLMInterface`, `PromptManagerInterface`, `TelemetryRecorderInterface`), inject at the composition root.
* `config.py` is the single configuration boundary — settings (`Settings`), LLM config (`LLMConfig`), and pricing (`PricingConfig`) are loaded there and injected, never fetched at point of use.
* `DependencyContainer` constructs infrastructure (`PromptManager`, `LangChainStructuredLLM`, `InMemoryTelemetryRecorder`, `CostCalculator`, `ProjectGenerator`, `ProjectBlueprintService`); it never runs the use case. Tests can inject a container to avoid touching `.env`/`config/*.yaml`.
* Structured output is an adapter concern (`LangChainStructuredLLM`) — the generator is provider-agnostic.
* Observability is one generic `TelemetryEvent` discriminated by `event_type`; the recorder contract never leaks generation vocabulary. `request_id` correlates all events.
* Tracing goes through a single `TraceContext` (`tracing.py`) that owns the span stack: `start_span(operation: Operation)` assigns the span id, links `parent_span_id` to the enclosing span, and timestamps the unit; `finish_span(span, status: SpanStatus, model, prompt_version, tokens, costs, failure: Failure | None)` records one `TelemetryEvent` and pops the span (LIFO enforced). The generator holds no manual timing or event construction, and `Span` is an internal detail of `TraceContext`.
* **Closed vocabularies over loose strings (0.0.41–0.0.44).** `Operation` merged the two free strings (`event_type`, `name`) that call sites previously had to keep in sync into one object that cannot disagree with itself. `SpanStatus`, `ErrorCategory` and the `*s` catalogue classes follow the same pattern: one authoritative value, always valid, always comparable. `ErrorCategory` deliberately separates *what kind of failure it was* (`llm`, `timeout`, `validation`) from *which class raised it* (`openai.APITimeoutError`), so retry and recovery decisions can be made on a controlled vocabulary instead of exception-type branching.
* **A clear domain/representation boundary (0.0.43–0.0.45).** Tracing APIs take the typed objects; `Span.finish()` is the one place they become the plain `str`/numeric fields on `TelemetryEvent`. This keeps the telemetry record flat and trivially storable/serializable while keeping the code that *decides* anything type-safe. Note the cost of this boundary: `Failure.message` and `Failure.retryable` are deliberately **not** propagated to telemetry, so they are available to the retry/recovery decision but absent from the recorded event.
* **`attributes` is the escape hatch, not a schema (0.0.42).** `TelemetryEvent.attributes: dict` holds operation-specific detail (currently `{"provider": "openrouter"}`) without widening the event for every new field. Caveat: the dataclass is `frozen` but this dict is mutable, so it is only frozen by convention.
* **Recovery policies are pure value objects, composed by a loop above the generator (0.0.46–0.0.52).** `RetryPolicy.decide` → `ExponentialBackoff.calculate_delay` → `RecoveryStrategy.recover` are each independently testable with no I/O, no clock, and no sleeping. `RetryDecision` and `RecoveryDecision` both carry a machine-readable `reason`, so a decision stays explainable after the fact instead of something you re-derive from logs.
* **The retry loop is a `RetryExecutor` collaborator, not code inside the service or generator (0.0.52).** This keeps the service a thin use-case boundary, keeps the executor testable against a plain callable with no LLM or filesystem, and — the load-bearing reason — lets the generator stay a **single attempt**, so each attempt emits its own span. Retry cost and latency therefore stay attributable per attempt instead of being averaged into one span.
* **`sleep` is an injected dependency (0.0.52).** This is what lets the tests assert the exact delay sequence (`[0.5, 1.5, 4.5, 13.5]`) while the whole suite still runs in seconds, and it is the seam that will accept a jittered/randomised sleeper later without touching the loop.
* **Unclassified failures bypass the loop (0.0.52).** A `ProjectGenerationError` with no `Failure` attached propagates immediately instead of consuming the attempt budget — retrying something you cannot classify turns a fast, clear error into a slow, mysterious one.
* `RecoveryStrategy` keys only on `category` and ignores `Failure.retryable`, so a retryable and a non-retryable timeout currently take the same recovery path. The retry policy is what consults `retryable`; the recovery strategy runs only after retries are exhausted, so the two do not conflict in practice.
* Backoff is pure capped exponential with **no jitter** — deliberately, so the math is exactly predictable in tests. Jitter is the right answer in production and is deferred until the call site can inject a random source.
* **The application owns request-level context.** `Application.generate_blueprint()` creates `RequestContext` and `TraceContext` once per request and passes the trace down; the generator consumes the trace it is given and never creates request identity itself.
* Trace hierarchy: `trace_id` groups the request pipeline, `span_id` identifies each operation, `parent_span_id` links child spans to their parent — prerequisites for reconstructing the call graph once agents and tools exist.
* `interfaces.py` imports `TraceContext` under `TYPE_CHECKING` only, because `tracing.py` imports `interfaces`; a runtime import would be circular.
* Prompts are versioned files (`prompts/<name>/<version>/`); `config/prompts.yaml` selects the active version; the version is recorded in telemetry.
* The interaction surface (`CLI`) is replaceable: the application speaks typed request/response contracts.
* LLM config lives in `config/llm.yaml` (typed `LLMConfig`); secrets live in `.env` (typed `Settings`); pricing lives in `config/pricing.yaml` (typed `PricingConfig`).
* **Never invent token counts or cost** — token fields stay `None` unless the provider reports usage; cost is computed only when input and output tokens are both present.
* `RequestContext` is a frozen dataclass (`request_id` + `trace_id`) created at the application boundary; the `request_id` it owns is the one used everywhere (service → generator → telemetry → logs → events).
* All application logging goes through `StructuredLogger` with `request_id`/`operation` extras; `RequestContextFilter` keeps non-application logs from crashing the formatter.
* Free model in use: `nvidia/nemotron-3-ultra-550b-a55b:free` (confirmed structured output). Fallback candidate: `openai/gpt-4o-mini`. Both present in `config/pricing.yaml` with zero placeholder rates pending verification.

## Dependencies

```text
langchain>=1.4.2          langchain-openai>=1.6.2    langchain-openrouter>=0.2.8
openai>=3.16.2            pydantic>=2.12.5           pydantic-settings
python-dotenv>=1.2.3      pyyaml
dev: pytest>=9.1.1
```

Python `>=3.12`.

## Commands

```text
uv run python app.py "Build an AI system that classifies corporate documents."
uv run pytest        # 92 passed
```

## Next Steps — From STEPS.md (Roadmap Step 7: Complete Single-Agent Blueprint)

The goal is to expand `ProjectBlueprint` beyond name + business outcome to a complete single-agent blueprint.

Planned fields (from the blueprint reasoning list):

```text
requirements
boundaries
constraints
agents
orchestration
context
state
memory
knowledge
actions
authority
runtime
recovery
evaluation
observability
security
```

Objectives:

* Nested Pydantic models (per-section schemas)
* List fields with validation
* Update prompt v2 (`prompts/project_blueprint/v2/`) to generate the full blueprint
* Extend tests

## Immediate Follow-ups

1. **Wire a real fallback model (Roadmap Step 22, the remaining ◐).** The `FALLBACK` action is implemented and tested, but with no `fallback` callable it logs and re-raises. A genuine fallback needs a second LLM, a pricing entry for it, and a config key selecting it — deliberately not fabricated in 0.0.52. Next release: add `fallback_model` to `config/llm.yaml`, resolve its pricing in the composition root, and have the service pass a fallback callable that generates with it.
2. **Narrow the generator's failure classification.** Every exception from the LLM call is currently `ErrorCategories.LLM` with `retryable=True`, so a validation error surfacing inside the call would be retried 3×. Map exception types to categories (timeout → `TIMEOUT`, config/validation → non-retryable) so the loop's inputs are honest.
3. **Open the `application` and `service` spans** (`Operations.APPLICATION_GENERATE_BLUEPRINT`, `SERVICE_GENERATE_BLUEPRINT` are defined but unused) so the trace becomes a real `application → service → llm` tree. This is what makes the `parent_span_id` machinery from 0.0.37–0.0.39 observable.
4. Expand `schemas.py` toward the full blueprint (Roadmap Step 7).
5. Add `CHANGELOG.md` rows/entries as each version completes (current latest: 0.0.52). **Note:** table rows for 0.0.36/0.0.37/0.0.38 still have no detail sections — pre-existing, and worth backfilling.
6. Do not create agents/, tools/, api/ directories yet — they come later per plan.

## Known Gaps / Loose Ends

* **No production fallback provider** — see follow-up 1. `RecoveryAction.FALLBACK` is reachable but currently degrades to a re-raise.
* **Failure classification is too coarse** — see follow-up 2. Everything from the LLM is `LLM`/`retryable=True`.
* **`ProjectGenerator.telemetry_recorder` is dead state.** The generator writes exclusively through the trace's recorder (`trace.finish_span`), so the injected recorder is never used — and `container.create_generator(..., telemetry_recorder=...)` misleadingly suggests otherwise. Remove the parameter, or keep it and document why.
* `Failure.message` and `Failure.retryable` are dropped at the telemetry boundary; if failures ever need debugging from recorded events alone, that gap will matter.
* `TelemetryEvent.attributes` is mutable despite the frozen dataclass.
* `event_type` divergence is test-only, not production: the generator correctly records `event_type="llm"` via `Operations.LLM_PROJECT_BLUEPRINT_GENERATION`, but `tests/test_telemetry.py` still hand-rolls `"generation"` / `"tool_call"`, neither of which exists in the `Operations` catalogue (the real tool event type is `"tool"`). Harmless as generic shape tests, but they never exercise the shipped vocabulary.
* Provider is hardcoded as `openrouter` in the generator's success attributes; it should come from config.
* Validation failures are still unclassified: the empty-`project_idea` guard runs before the span opens, so it never becomes a `Failure`/`ErrorCategory`.
* **No linter or type checker is configured** (`pyproject.toml` has no ruff/mypy). Formatting consistency is currently maintained by hand — the codebase follows a ~60-char wrap style that nothing enforces.

## Todo

- [x] Typed observability vocabulary (0.0.41–0.0.45, `Operation` / `SpanStatus` / `ErrorCategory` / `Failure`)
- [x] Recovery policy value objects (0.0.46–0.0.49, `RetryPolicy` / `ExponentialBackoff` / `RecoveryStrategy`)
- [x] Composition root container-injection fix (0.0.50)
- [x] Recovery decisions use `ErrorCategories` constants (0.0.51)
- [x] Retry loop wired end-to-end (0.0.52, `RetryExecutor` + span-per-attempt)
- [x] Docs synced — SESSION_HANDOFF, STEPS 1–52, ROADMAP Step 22 ◐
- [x] Token usage capture from the provider (0.0.33, `LLMUsage` + `include_raw`)
- [x] Per-generation cost via config pricing (0.0.34/0.0.35, `CostCalculator` + events)
- [x] Trace + span IDs (0.0.37, `RequestContext.trace_id` + `TelemetryEvent.trace_id`/`span_id`)
- [x] Span helper (0.0.38, `tracing.Span` start/finish in the generator)
- [x] Parent span linkage (0.0.39, optional `parent_span_id` on `Span.start`/`TelemetryEvent`)
- [x] Application-owned trace (0.0.40, `Application` creates `TraceContext`; generator opens/closes spans through it)
- [ ] Roadmap Step 22 — wire a real fallback model (completes the remaining ◐)
- [ ] Narrow failure classification so validation errors are not retried
- [ ] Open `application`/`service` spans for a real trace tree
- [ ] Remove or document `ProjectGenerator.telemetry_recorder`
- [ ] Add a linter/type checker to `pyproject.toml`
- [ ] Backfill `CHANGELOG.md` detail sections for 0.0.36–0.0.38
- [ ] Roadmap Step 7 — Complete single-agent blueprint (`schemas.py` expansion + prompt v2)
- [ ] Step 8 — Prompt engineering v2 (`prompts/<name>/v2` with few-shot examples)
- [ ] Step 9 — Validation layer (deterministic Python validation)
- [ ] Integration tests for the real LLM path (free model)
- [ ] Roadmap Step 11+ — per `docs/ROADMAP.md`