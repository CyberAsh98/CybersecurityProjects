```ruby
██████╗  ██████╗ ███████╗████████╗ ██████╗  ██████╗ ██╗
██╔══██╗██╔════╝ ██╔════╝╚══██╔══╝██╔═══██╗██╔═══██╗██║
██████╔╝██║  ███╗███████╗   ██║   ██║   ██║██║   ██║██║
██╔══██╗██║   ██║╚════██║   ██║   ██║   ██║██║   ██║██║
██████╔╝╚██████╔╝███████║   ██║   ╚██████╔╝╚██████╔╝███████╗
╚═════╝  ╚═════╝ ╚══════╝   ╚═╝    ╚═════╝  ╚═════╝ ╚══════╝
```

[![Cybersecurity Projects](https://img.shields.io/badge/Cybersecurity--Projects-Aayush%20Pandey-red?style=flat&logo=github)](https://github.com/CyberAsh98/CybersecurityProjects)
[![Python](https://img.shields.io/badge/Python-3.12+-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)

> Multi-format encoding/decoding CLI with recursive layer detection for security analysis and obfuscation testing.

---

## What This Project Does

`b64tool` is a production-grade encoding analysis CLI designed for real-world security workflows.

It supports:

- Base64
- Base64URL
- Base32
- Hex
- URL Encoding

The core feature is **recursive peeling**, which automatically detects and strips multiple encoding layers — a common technique used in malware and WAF bypass attempts.

You provide encoded input. The tool:

1. Detects likely encoding format using confidence scoring
2. Decodes it
3. Checks if the result is itself encoded
4. Repeats until original data is revealed

---

## Why This Exists

In real security work:

- JWTs are base64url
- Certificates are base64
- DNS exfiltration uses base32
- Malware hides payloads in multi-layer encodings
- WAF bypass often uses double URL encoding

Security engineers must be able to **recognize, validate, and safely decode obfuscated data**.

This tool operationalizes that workflow.

---

## Quick Start

```bash
git clone https://github.com/CyberAsh98/CybersecurityProjects
cd CybersecurityProjects/Proj/base64-tool

uv sync
uv run b64tool --help
```

### Basic Usage

```bash
uv run b64tool encode "Hello World"
uv run b64tool decode "SGVsbG8gV29ybGQ="
uv run b64tool detect "SGVsbG8gV29ybGQ="
```

### Multi-layer Peeling

```bash
uv run b64tool chain "alert(1)" --steps base64,hex
uv run b64tool peel "5957786c636e516f4a33687a63796370"
```

### Pipeline Support

```bash
echo "SGVsbG8=" | uv run b64tool decode
cat payload.txt | uv run b64tool peel
```

---

## Commands

| Command | Description |
|----------|-------------|
| `encode` | Encode data into selected format |
| `decode` | Decode encoded data |
| `detect` | Auto-detect encoding with confidence scoring |
| `peel` | Recursively decode multi-layer encodings |
| `chain` | Apply multiple encoding steps |

---

## Learning Modules

This project includes in-depth learning materials:

| Module | Topic |
|--------|-------|
| [00 - Overview](learn/00-OVERVIEW.md) | Setup and fundamentals |
| [01 - Concepts](learn/01-CONCEPTS.md) | Encoding theory & security implications |
| [02 - Architecture](learn/02-ARCHITECTURE.md) | System design & module relationships |
| [03 - Implementation](learn/03-IMPLEMENTATION.md) | Code walkthrough |
| [04 - Challenges](learn/04-CHALLENGES.md) | Advanced extensions |

---

## Project Structure

```
base64-tool/
├── src/b64tool/
│   ├── cli.py
│   ├── constants.py
│   ├── encoders.py
│   ├── detector.py
│   ├── peeler.py
│   ├── formatter.py
│   └── utils.py
├── learn/
├── tests/
├── pyproject.toml
└── README.md
```

---

## Security Focus Areas

- Encoding detection heuristics
- Confidence scoring systems
- RFC 4648 compliance
- WAF bypass analysis
- Multi-layer obfuscation detection
- Pipeline-safe CLI design
- Strict decoding validation

---

## License

MIT License