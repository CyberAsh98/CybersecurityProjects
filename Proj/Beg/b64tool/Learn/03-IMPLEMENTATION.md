# Implementation

## constants.py

Defines:

- EncodingFormat enum
- Thresholds
- Character sets
- Exit codes

---

## encoders.py

Pure encode/decode functions.

Strict decoding:
```
b64decode(validate=True)
```

Ensures RFC compliance.

---

## detector.py

Confidence scoring system.

Each format:
- Structural validation
- Decode validation
- Printable text bonus
- Score clamped to [0.0 – 1.0]

---

## peeler.py

Iterative multi-layer decoding.

Stops when:
- No valid detection
- Confidence below threshold
- Decoded output not valid UTF-8

---

## formatter.py

Rich UI for terminals.  
Raw output when piped.

---

## utils.py

Handles:
- stdin
- file input
- CLI arguments
- safe byte preview