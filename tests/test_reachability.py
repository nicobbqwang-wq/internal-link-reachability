import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from reachability import analyze


class ReachabilityTests(unittest.TestCase):
    def setUp(self):
        self.g=json.loads(Path('examples/graph.json').read_text())

    def test_island_has_incoming_but_is_unreachable(self):
        r=analyze(self.g); pages={p['url']:p for p in r['pages']}
        island=pages['https://example.com/island-a/']
        self.assertFalse(island['reachable'])
        self.assertFalse(island['no_incoming_candidate'])
        self.assertIsNone(island['min_hops'])
        self.assertEqual(r['reachable_discoverable_pages'],3)

    def test_depth_and_entrypoint_exemption(self):
        p={p['url']:p for p in analyze(self.g)['pages']}
        self.assertEqual(p['https://example.com/guide/']['min_hops'],2)
        self.assertFalse(p['https://example.com/']['no_incoming_candidate'])
        self.assertTrue(p['https://example.com/unlinked/']['no_incoming_candidate'])

    def test_duplicate_edges_deduplicated(self):
        self.g['links'].append(self.g['links'][0].copy())
        r=analyze(self.g)
        self.assertEqual(r['unique_traversable_pairs'],4)

    def test_self_links_do_not_rescue_orphans(self):
        u='https://example.com/unlinked/'
        self.g['links'].append({'source':u,'target':u,'kind':'context','crawlable':True})
        self.assertTrue(next(p for p in analyze(self.g)['pages'] if p['url']==u)['no_incoming_candidate'])

    def test_noncrawlable_does_not_create_path(self):
        self.g['links'][0]['crawlable']=False
        self.assertEqual(analyze(self.g)['reachable_discoverable_pages'],1)

    def test_multiple_entries(self):
        self.g['entrypoints'].append('https://example.com/island-a/')
        self.assertEqual(analyze(self.g)['reachable_discoverable_pages'],5)

    def test_denominator_flag_does_not_block_transit(self):
        self.g['pages'][1]['discoverable']=False
        r=analyze(self.g)
        self.assertEqual(r['discoverable_pages'],5)
        self.assertTrue(next(p for p in r['pages'] if p['url'].endswith('/guide/'))['reachable'])

    def test_bad_schema_and_unknown_endpoint(self):
        for mutation in ['missing','duplicate','endpoint','boolean']:
            g=copy.deepcopy(self.g)
            if mutation=='missing': del g['entrypoints']
            if mutation=='duplicate': g['pages'].append(g['pages'][0])
            if mutation=='endpoint': g['links'][0]['target']='https://example.com/missing/'
            if mutation=='boolean': g['links'][0]['crawlable']='false'
            with self.assertRaises(ValueError): analyze(g)

    def test_url_variants_not_merged(self):
        self.g['pages'].append({'url':'https://example.com/guide','discoverable':True})
        self.assertTrue(next(p for p in analyze(self.g)['pages'] if p['url'].endswith('/guide'))['no_incoming_candidate'])

    def test_cli_missing_file(self):
        r=subprocess.run([sys.executable,'reachability.py','absent.json'],capture_output=True,text=True)
        self.assertEqual(r.returncode,2);self.assertEqual(json.loads(r.stdout)['status'],'INVALID')


if __name__=='__main__': unittest.main()
