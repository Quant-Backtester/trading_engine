## Coding Guidelines — Trading Engine (design philosophy)

### 1. Purpose and scope

These guidelines apply to all code under:

- `core/`
- `events/`
- `market_data/`
- `strategy/`

The primary goals are:

- Determinism
- Clear separation of responsibilities
- Testability
- Minimal and explicit side effects

---

### 2. Architectural principles

1. **Single responsibility per module**
   Each file must have one clear purpose (e.g., queueing, time, replay).

2. **Unidirectional dependencies**
   Dependencies must flow in this direction only:

   ```
   market_data → events → engine → strategy
   ```

   No reverse imports.

3. **Engine owns control flow**
   External components may inject events, but only the engine advances time and dispatches events.

4. **No global mutable state**
   All state must be owned by explicit objects.

---

### 3. Determinism rules

1. **No wall-clock time inside engine logic**
   `datetime.now()` and `time.time()` are forbidden outside setup or tests.

2. **Explicit timestamps only**
   All events must carry a timestamp.

3. **Stable ordering**
   Event ordering must be deterministic even when timestamps are equal.

4. **Fail fast on invariant violations**
   Silent corection is not allowed.

---

### 4. Event design rules

1. **Events are immutable:**

   - Events and payloads must be `@dataclass(frozen=True, slots=True)`.
   - `slots` is used to optimize memory usage and speed up attribute access in object instances.
   - `frozen` make the class immutable.

2. **No logic in events:**

   - Events contain data only.

3. **Payloads are typed:**

   - Use dataclasses or typed dictionaries. Avoid raw `dict`.

4. **EventEnum is exhaustive:**
   Adding a new event type requires:

   - Enum entry
   - Engine handler
   - Test

---

### 5. Engine rules

1. **Engine does not create events except synthetic ones**
   (e.g., TIMER, ORDER_FILL).

2. **Handlers must not push events directly**
   Handlers return actions; the engine enqueues them.

   Rationale: control and observability.

3. **All state transitions are logged at DEBUG or INFO**
   Payload contents are not logged by default.

4. **Engine never swallows exceptions**
   - Exceptions indicate invalid engine state.
   - Exceptions must be logged down for further analysis

---

### 6. EventQueue rules

1. **Priority queue only**

   - FIFO queues are forbidden.

2. **Ordering key**

   - `(timestamp, sequence_number)`

3. **No blocking or concurrency assumptions**

   - Single-threaded only.

4. **Queue underflow is an error**

---

### 7. Market data replay rules

1. **Replayer is read-only**

   - It does not mutate engine state directly.

2. **Replay validates ordering**

   - Out-of-order data must raise.

3. **No clock manipulation**

   - Timestamps are passed through untouched.

4. **One responsibility: data → events**

---

### 8. Strategy rules

1. **Strategies are passive**

   - They react to events; they do not control time.

2. **No I/O inside strategies**

   - No file access, network, or database calls.

3. **Strategies emit intents, not actions**
   - e.g., ORDER_SUBMIT, not direct order placement.

---

### 9. Logging rules

1. **Use the engine logger only**

   - `logging.getLogger("engine")`
   - or use `logging.getLogger(__name__)` for modules

2. **Log state transitions, not data streams**

3. **No logging in tight loops unless DEBUG-guarded**

4. **No prints**

---

### 10. Testing rules

1. **Every component has unit tests**

   - Clock, queue, replayer, engine.

2. **Tests must be deterministic**

   - No randomness without fixed seeds.

3. **Invariant violation tests are required**

4. **No mocking the engine core**
   - Prefer fake implementations.

---

### 11. Type and style rules

1. **Type hints are mandatory**

   - Public methods must be fully typed.

2. **Use `Literal` or `Enum`, not magic strings**

3. **Prefer composition over inheritance**

4. **Explicit is better than clever**

---

### 12. Prohibited patterns

The following are forbidden inside engine code:

- `datetime.now()`
- `time.sleep()`
- Threads or async
- Global variables
- Silent error handling
- Side-effects in constructors

> Note: reason is that this is a backtesting application, so it is not required to do threading except you want real-time backtesting, but that will need to be handle separatedly.

---

### 13. Code review checklist (self-review)

Before committing, verify:

- Does this change preserve determinism?
- Is the dependency direction respected?
- Are invariants checked and logged?
- Is the responsibility of this module clear?

---

### 14. `/common`

- this folder contain uncategorized codes that is used across multiple modules, like [types.py](../common/types.py) is where all the custom type that is required to use in multiple files.

---

### 15. `Others rules`
  - if you need >=3 nesting for a single function, then you need to break down your code to new function. In other words, function should not be deeply nested.
  - always use type hinting for function return and arguments, and whenever you think make the code more clean
  - If you need to construct a dict with specific fixed structure, use a `TypedDict`
  - If you need to create a tuple with specific fixed structure, use a `NamedTuple`
  - when you have a fixed, small set of named constant and they are related. And they are important constant that will require more runtime checking, use a `StrEnum` or `IntEnum` whatever one is applicable for your use case.
  - if the type is shortlive, and don't requrie runtime checking, use `type`
    - eg:
    ```py
    from typing import Literal

    type Side = Literal["BUY" | "SELL"]
    ```
### Final note

This engine is a **simulation kernel**, not an application.
Correctness, clarity, and determinism take priority over convenience.

---
