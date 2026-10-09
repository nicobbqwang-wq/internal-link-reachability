# Internal Link Reachability

Find pages with no incoming links **and** disconnected groups whose members link only to each other. This offline Python tool compares a complete page inventory with a supplied link graph and entrypoints. It reports reachability and minimum hops without crawling or changing your site.

By **BBQ / BBQ Growth Lab** · [中文](README.zh-CN.md) · [MIT](LICENSE)

## Start / Input / Review

- [Run the example](#run-the-example)
- [Prepare a graph](#prepare-a-graph)
- [Interpret the result](#interpret-the-result)
- [Limits and sources](#limits-and-sources)

## Run the example

For technical SEO practitioners and content teams investigating discovery paths. Requires Python 3.9+; standard library only. Download or clone the repository, then run inside it:

```sh
python3 reachability.py examples/graph.json
python3 -m unittest discover -s tests -v
```

The six `example.com` URLs are synthetic. Home → hub → guide gives three reachable pages. Island A ↔ Island B both have an incoming link but are unreachable from home. The final page has no incoming link. The guide has two hops; unreachable pages have `null` hops. See [expected output](examples/report.json).

Copy [the input template](templates/graph.json), replace its sample URL and add your inventory and edges:

```sh
python3 reachability.py my-graph.json > report.json
```

Exit code 0 means the graph was analyzed, even if it contains problems. Exit code 2 means invalid input. The tool only reads your JSON and prints a report. It does not send the graph anywhere.

## Prepare a graph

Use inventory from your CMS, sitemap or other known URL lists alongside a link export; a crawl-only list can omit the very pages you want to find. Decide the public-discovery scope yourself and record it in [the review worksheet](templates/review.md).

| Field | Required input |
| --- | --- |
| `pages` | Nonempty array of objects: absolute `url` and boolean `discoverable` |
| `entrypoints` | Nonempty array of URLs already present in pages; multiple starts supported |
| `links` | Array of objects with `source`, `target`, `kind`, boolean `crawlable` |
| `kind` | One of `navigation`, `breadcrumb`, `context`, `related`, `footer` |

All edge endpoints must be present in the inventory. Remove external links from the export or deliberately include their endpoints and explain that expanded scope. Do not merge URL variants without evidence: paths, query strings, case and trailing slashes are kept exactly as supplied. Fragments, credentials, whitespace and non-HTTP(S) URLs are rejected.

`discoverable` controls **report selection only**. A false value does not mean robots-disallowed or inaccessible, and does not block graph transit. A path can pass through that node. Exclude edges that cannot actually be traversed by setting `crawlable: false`; do not infer crawlability from the selection flag. All crawlability labels come from your export and remain unverified by this program.

## Interpret the result

The report returns one row per selected page: entrypoint status, reachability, minimum hops, distinct incoming source URLs, contextual source URLs and a no-incoming candidate flag. Self-links do not rescue an orphan. Repeated source/target pairs count once in traversal; distinct kinds can still identify a contextual source. Entry pages are exempt from the no-incoming flag because they are explicit starting points.

A page can have incoming links and still be unreachable, as the two-node island shows. Conversely, an entrypoint is reachable by definition even if nothing links to it in your export. Read these signals together; do not equate every unreachable page with a confirmed real-world orphan.

1. Confirm the page should remain independently discoverable and its content still serves a task.
2. Check inventory completeness and the actual rendered links on desktop and mobile.
3. Choose a relevant stable entry, then review the surrounding text and target promise.
4. Re-export the same scope after a change; keep the old report to explain denominator changes.

## Limits and sources

There is no HTTP status check, redirect following, canonical resolution, JavaScript rendering, rel/nofollow modeling, relevance judgment, PageRank estimate or indexing test. Hops are structural distances, not ranking factors or a mandated depth target. `context_sources` measures labels, not source relevance or stability. A reachable path is not proof of indexing or an SEO benefit. Discovery and AI citation outcomes are unmeasured.

Method source: BBQ Growth Lab's [internal linking architecture article](https://bbqgrowthlab.com/zh-cn/articles/internal-linking-architecture-link-equity-guide/), especially inventory completeness, edge types and discovery-path review. Reviewed 2026-10-08. This repository implements a narrow graph check; it does not reproduce the article's performance anecdotes. [Google's link guidance](https://developers.google.com/search/docs/crawling-indexing/links-crawlable) explains crawlable link markup; the tool does not itself inspect markup.

Code, examples and worksheets were created with Codex assistance. Only synthetic data were tested; see [validation](VALIDATION.md). Keep confidential URLs and customer data out of public reports. [Contributions](CONTRIBUTING.md) should include synthetic reproductions. MIT covers original repository files; linked sources retain their own terms.
