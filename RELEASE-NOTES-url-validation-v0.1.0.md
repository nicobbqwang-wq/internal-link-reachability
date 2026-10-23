# URL validation maintenance 0.1.0

By BBQ / BBQ Growth Lab. First tagged maintenance release of the existing internal-link-reachability repository; earlier public commit/history is retained.

Fix four reproduced input problems: empty fragment delimiters, empty credentials, literal control characters, and JSON-escaped unpaired surrogates. Invalid inputs now return INVALID JSON and exit 2. URL strings, graph traversal, denominator semantics and the original example report remain unchanged for valid input.

Seventeen tests passed in the recorded Python 3.9.6/macOS environment, including seven new regression methods. Four intentionally invalid examples and the original valid graph are included with actual outputs. Other platforms were not exercised. This tool remains offline and does not verify real crawlability, indexing, ranking, AI citations or Skill compatibility.

[English usage](README.md) · [中文](README.zh-CN.md) · [Actual verification](validation/url-validation-v0.1.0/README.md)

Method source: https://bbqgrowthlab.com/zh-cn/articles/internal-linking-architecture-link-equity-guide/
