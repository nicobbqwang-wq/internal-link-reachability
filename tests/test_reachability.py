import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from reachability import analyze, url


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

    def test_empty_fragment_delimiter_is_rejected(self):
        for value in ('https://example.com/#', 'https://example.com/?q=one#'):
            with self.subTest(value=value), self.assertRaises(ValueError):
                url(value)

    def test_empty_credentials_are_rejected(self):
        for value in ('https://@example.com/', 'https://:@example.com/'):
            with self.subTest(value=value), self.assertRaises(ValueError):
                url(value)

    def test_literal_control_characters_are_rejected_before_parsing(self):
        for control in ('\x00', '\x01', '\x1b', '\x7f', '\x85', '\x9f', '\t', '\n'):
            for value in (control + 'https://example.com/',
                          'https://example.com' + control + '/',
                          'https://example.com/path' + control,
                          'https://example.com/?q=' + control):
                with self.subTest(value=repr(value)), self.assertRaises(ValueError):
                    url(value)

    def test_unpaired_surrogates_are_rejected(self):
        for value in ('https://example.com/\ud800', 'https://example.com/\udfff'):
            graph={'pages':[{'url':value,'discoverable':True}], 'links':[], 'entrypoints':[value]}
            with self.subTest(value=repr(value)), self.assertRaises(ValueError):
                analyze(graph)

    def test_valid_unicode_and_encoded_delimiters_preserve_exact_urls(self):
        for value in ('https://example.com/%23?contact=person%40example.com',
                      'https://example.com/\u5185\u94fe/\U0001f4d6?q=a%20b',
                      'HTTPS://example.com:443/Path?A=1'):
            with self.subTest(value=value):
                graph={'pages':[{'url':value,'discoverable':True}], 'links':[], 'entrypoints':[value]}
                self.assertEqual(analyze(graph)['pages'][0]['url'], value)

    def test_invalid_url_cli_returns_json_without_traceback(self):
        for value in ('https://example.com/#', 'https://@example.com/',
                      'https://example.com\x00/', 'https://example.com/\ud800'):
            with self.subTest(value=repr(value)), tempfile.TemporaryDirectory() as tmp:
                graph={'pages':[{'url':value,'discoverable':True}], 'links':[], 'entrypoints':[value]}
                path=Path(tmp)/'graph.json';path.write_text(json.dumps(graph,ensure_ascii=True))
                result=subprocess.run([sys.executable,'-B','reachability.py',str(path)],
                                      capture_output=True,text=True)
                self.assertEqual(result.returncode,2)
                self.assertEqual(result.stderr,'')
                self.assertEqual(json.loads(result.stdout)['status'],'INVALID')

    def test_original_example_report_is_unchanged(self):
        self.assertEqual(analyze(self.g),json.loads(Path('examples/report.json').read_text()))


if __name__=='__main__': unittest.main()
