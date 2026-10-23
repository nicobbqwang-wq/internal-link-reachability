"""Inspect a supplied link graph offline; never crawl, rank or edit a website."""
import argparse
import json
import unicodedata
from collections import deque
from urllib.parse import urlsplit

KINDS = {'navigation', 'breadcrumb', 'context', 'related', 'footer'}


def url(value):
    if (not isinstance(value, str) or not value
            or any(c.isspace() or unicodedata.category(c) in {'Cc', 'Cs'} for c in value)):
        raise ValueError('URLs must be nonempty HTTP(S) strings without whitespace, controls or surrogates')
    p = urlsplit(value)
    if (p.scheme not in {'http', 'https'} or not p.hostname
            or p.username is not None or p.password is not None or '#' in value):
        raise ValueError('URLs must use HTTP(S), have a host, and have no credentials or fragment')
    try:
        p.port
    except ValueError:
        raise ValueError('invalid URL port')
    return value


def analyze(data):
    if not isinstance(data, dict) or set(data) != {'pages', 'links', 'entrypoints'}:
        raise ValueError('root fields must be pages, links and entrypoints')
    if any(not isinstance(data[k], list) for k in data):
        raise ValueError('root fields must be arrays')
    if not data['pages'] or not data['entrypoints']:
        raise ValueError('pages and entrypoints must not be empty')
    pages = {}
    for page in data['pages']:
        if not isinstance(page, dict) or set(page) != {'url', 'discoverable'} or type(page['discoverable']) is not bool:
            raise ValueError('each page requires url and boolean discoverable')
        u = url(page['url'])
        if u in pages:
            raise ValueError('duplicate inventory URL: '+u)
        pages[u] = page['discoverable']
    entries = set()
    for entry in data['entrypoints']:
        entry = url(entry)
        if entry not in pages:
            raise ValueError('entrypoint absent from inventory')
        entries.add(entry)
    outgoing = {u: set() for u in pages}
    incoming = {u: set() for u in pages}
    context = {u: set() for u in pages}
    excluded = 0
    for edge in data['links']:
        if not isinstance(edge, dict) or set(edge) != {'source', 'target', 'kind', 'crawlable'}:
            raise ValueError('each link requires source, target, kind and crawlable')
        source, target = url(edge['source']), url(edge['target'])
        if source not in pages or target not in pages:
            raise ValueError('link endpoint absent from inventory')
        if not isinstance(edge['kind'], str) or edge['kind'] not in KINDS or type(edge['crawlable']) is not bool:
            raise ValueError('invalid kind or crawlable flag')
        if not edge['crawlable'] or source == target:
            excluded += 1
            continue
        outgoing[source].add(target)
        incoming[target].add(source)
        if edge['kind'] == 'context':
            context[target].add(source)
    distance = {u: 0 for u in sorted(entries)}
    queue = deque(sorted(entries))
    while queue:
        source = queue.popleft()
        for target in sorted(outgoing[source]):
            if target not in distance:
                distance[target] = distance[source]+1
                queue.append(target)
    rows = []
    for u in sorted(pages):
        if pages[u]:
            rows.append({'url': u, 'entrypoint': u in entries,
                         'reachable': u in distance, 'min_hops': distance.get(u),
                         'incoming_sources': sorted(incoming[u]),
                         'context_sources': sorted(context[u]),
                         'no_incoming_candidate': not incoming[u] and u not in entries})
    return {'status': 'ANALYZED', 'inventory_pages': len(pages),
            'discoverable_pages': len(rows),
            'reachable_discoverable_pages': sum(r['reachable'] for r in rows),
            'excluded_self_or_noncrawlable_rows': excluded,
            'unique_traversable_pairs': sum(len(v) for v in outgoing.values()),
            'pages': rows,
            'limits': 'Snapshot-only structural signals; not verified crawlability, relevance, indexation or ranking.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('graph_json')
    args = parser.parse_args()
    try:
        with open(args.graph_json, encoding='utf-8') as f:
            report = analyze(json.load(f))
    except (OSError, ValueError, TypeError) as exc:
        print(json.dumps({'status': 'INVALID', 'error': str(exc)}))
        return 2
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
