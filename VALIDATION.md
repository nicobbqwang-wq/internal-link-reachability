# Validation — 2026-10-09

Executed Python 3.9.6 on Darwin arm64.

- 10 unittest cases passed from the repository directory: disconnected cycles, minimum depth, entrypoint exemption, duplicate edges, self-links, noncrawlable edges, multiple starts, report denominator vs transit, malformed inputs, URL variants and CLI error handling.
- README example executed: 6 selected nodes, 3 reachable; guide depth 2; disconnected cycle retains incoming links; unlinked node flagged. Output saved in examples/report.json.
- Python 3.9+ is intended; only the runtime above was executed. No Windows/Linux execution, live crawl, indexing or ranking validation is claimed.
- Samples are synthetic. Public source articles and linked official documentation were accessible via web retrieval on 2026-10-09.

This checks a supplied graph, not the accuracy or completeness of a real site's export.
