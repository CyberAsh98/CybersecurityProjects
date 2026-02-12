# Architecture

## Design Philosophy

Each module has one responsibility.

- encoders.py → transforms data
- detector.py → scoring logic
- peeler.py → recursive orchestration
- formatter.py → output rendering
- cli.py → command wiring

No circular dependencies.
Strict downward module graph.

---

## Dependency Graph

```
cli
 ├─ encoders
 ├─ detector
 ├─ peeler
 ├─ formatter
 ├─ utils
 └─ constants
```

constants and utils have no internal dependencies.

---

## Data Flow Example (Peel)

Input
→ detect_best()
→ decode
→ re-check encoding
→ repeat until threshold fails

---

## Registry Pattern

ENCODER_REGISTRY maps formats to functions.

Adding a new format requires:

1. Add enum value
2. Add encoder/decoder
3. Add scorer

No CLI changes required.

---

## Pipeline-Safe Design

Rich output → stderr  
Raw data → stdout  

Ensures safe Unix piping.