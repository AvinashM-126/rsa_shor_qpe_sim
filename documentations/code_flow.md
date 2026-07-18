# Period Function Code Flow (QPE Implementation)

This diagram represents the Quantum Phase Estimation (QPE) implementation in `period()`, which performs quantum period-finding followed by classical post-processing.

```mermaid
flowchart TD
  A["period(backend, a, N)<br/>backend, a, N provided"] --> B["Setup quantum registers<br/>15-qubit counting register<br/>15-qubit work register<br/>1-qubit ancilla"]
  B --> C["Initialize superposition<br/>on counting register"]
  C --> D["Apply controlled modular<br/>exponentiation f(x) = a^x mod N"]
  D --> E["Apply inverse QFT<br/>on counting register"]
  E --> F["Measure counting register<br/>to get phase estimate"]
  F --> G["Transpile to qasm_simulator<br/>backend and execute"]
  G --> H["Get measurement counts<br/>from 1000 shots"]
  H --> I["Post-process with<br/>continued fractions"]
  I --> J["Extract period r<br/>from phase estimate"]
  J --> K["Return period r<br/>or None if invalid"]
```

**Key Steps:**
- Superposition creation allows simultaneous evaluation of f(x) = a^x mod N
- Inverse QFT maps phase information to measurable computational basis
- Continued fractions extracts period r from discrete phase samples
- Graceful failure: Returns `None` if modulus N exceeds work register capacity (2^15)