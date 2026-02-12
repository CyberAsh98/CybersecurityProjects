# Concepts

## Encoding vs Encryption

This is the most important distinction in this project.

**Encoding**
- Transforms data representation
- Fully reversible
- No secret key
- Used for compatibility

**Encryption**
- Uses a secret key
- Not reversible without key
- Used for confidentiality

If you can reverse it without a key, it is encoding.

### Real Vulnerability Example

CWE-261: Weak Encoding for Password

Several embedded devices stored admin credentials as base64 instead of hashing them. Anyone could decode credentials instantly.

Encoding is not security.

---

## How Base64 Works

Base64 converts binary data into 64 ASCII characters.

Alphabet:
```
A-Z a-z 0-9 + /
```

Padding:
```
=
```

Three bytes → four characters  
33% size increase

---

## Base64URL

Used in JWTs.

Changes:
```
+ → -
/ → _
```

Removes URL-breaking characters.

---

## Base32

Alphabet:
```
A-Z 2-7
```

Used in:
- TOTP secrets
- DNS-safe encodings

Produces ~60% size overhead.

---

## Hex Encoding

Each byte → two hex characters

Example:
```
Hi → 4869
```

100% size overhead  
Used in hashes, dumps, malware analysis.

---

## URL Encoding

Replaces unsafe characters:

```
space → %20
& → %26
```

Double encoding is commonly used in WAF bypass attempts.

---

## Multi-layer Obfuscation

Attackers stack encodings:

```
base64 → hex → URL
```

Peeling layers reveals hidden payloads.

---

## Encoding Detection Signals

Base64:
- Length divisible by 4
- Mixed case letters
- Ends with =

Hex:
- Even length
- Only 0-9 a-f
- Consistent case

URL:
- Contains %XX patterns

Detection is probabilistic, not binary.

---

## Why Confidence Scoring Matters

Some strings match multiple formats.

This tool ranks formats by confidence (0.0 – 1.0).

Security tools must prioritize likely formats, not assume certainty.