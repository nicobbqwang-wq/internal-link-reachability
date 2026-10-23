# URL validation maintenance: actual verification

By BBQ / BBQ Growth Lab. Executed 2026-10-23 on Python 3.9.6 / macOS. Other interpreters and operating systems were not tested.

Seventeen unittest methods passed (ten existing, seven new). Before the fix, the same 17 methods produced 25 failing subcases; the original public script accepted an empty fragment delimiter, empty user information and literal NUL, and crashed when printing a JSON-escaped unpaired surrogate. These are synthetic reproductions, not customer observations or hostile network tests.

The fix checks literal whitespace, Unicode Cc control characters and Cs surrogate code points before URL parsing, rejects any literal # delimiter, and detects even empty username/password components. It returns valid strings unchanged. The original six-page example and its complete report stay identical; the graph traversal algorithm and report-selection flag did not change.

[RUN.json](RUN.json) binds production code, tests, five inputs and outputs. Valid input exits 0/ANALYZED; all four invalid examples exit 2/INVALID with JSON and no traceback. The root [historical validation](../../VALIDATION.md) retains the original 2026-10-09 record.

| Input | Result |
|---|---|
| [Original graph](../../examples/graph.json) | 0 / ANALYZED; 6 selected, 3 reachable |
| [Empty fragment delimiter](../../examples/invalid-empty-fragment.json) | 2 / INVALID |
| [Empty credentials](../../examples/invalid-empty-credentials.json) | 2 / INVALID |
| [Literal control](../../examples/invalid-control.json) | 2 / INVALID |
| [Unpaired surrogate](../../examples/invalid-surrogate.json) | 2 / INVALID |

This is a bounded input guard, not a comprehensive URL validator: it does not decode percent escapes, validate DNS or hostnames, fetch pages, infer relevance or prove crawlability, indexing, rankings or AI citations. Valid Unicode paths and percent-encoded #/@ remain exact strings. No customer data, human baseline, Skill-host compatibility or SEO/GEO effect is claimed.

From the repository root:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
python3 reachability.py examples/graph.json
python3 reachability.py examples/invalid-surrogate.json
```

The final command intentionally returns 2; read its INVALID JSON. 中文：本次只修输入拒绝与错误返回，图分析结果、分母含义及局限保持；程序测试不能代替线上抓取、编辑判断或效果验证。
