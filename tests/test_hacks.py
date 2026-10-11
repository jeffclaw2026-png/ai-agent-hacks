import importlib.util
import json
import pathlib
import tempfile
import unittest
from unittest.mock import patch

ROOT = pathlib.Path(__file__).resolve().parents[1]


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


plugin = load('integrations/hermes/shared-response-style/__init__.py', 'style_plugin')
benchmark = load('benchmarks/pi_output_ab.py', 'benchmark')
privacy = load('scripts/privacy_check.py', 'privacy')


class Tests(unittest.TestCase):
    def test_prompt_path(self):
        self.assertEqual(plugin.STYLE_PATH, ROOT / 'prompts/conversation.md')
        self.assertIn('Once the user', plugin.render_style({}))

    def test_registration(self):
        class Context:
            def register_system_prompt_section(self, *args, **kwargs):
                self.args, self.kwargs = args, kwargs
        ctx = Context()
        plugin.register(ctx)
        self.assertEqual(ctx.args[0], 'shared-response-style.communication')
        self.assertEqual(ctx.kwargs['max_chars'], 4000)
        self.assertEqual(ctx.kwargs['position'], 'after_memory')

    def test_platforms(self):
        self.assertEqual(plugin.render_style({'platform': 'cron'}),
                         plugin.render_style({'platform': 'subagent'}))

    def test_invalid_prompt(self):
        with tempfile.TemporaryDirectory() as directory:
            p = pathlib.Path(directory) / 'prompt.md'
            with patch.object(plugin, 'STYLE_PATH', p):
                with self.assertRaises(FileNotFoundError): plugin.render_style({})
                p.write_text(' ')
                with self.assertRaises(ValueError): plugin.render_style({})
                p.write_text('x' * 4001)
                with self.assertRaises(ValueError): plugin.render_style({})

    def test_usage(self):
        events = [{'type': 'message_end', 'message': {'role': 'assistant',
                   'usage': {'input': 10, 'output': 3}, 'content': []}},
                  {'type': 'message_end', 'message': {'role': 'tool',
                   'usage': {'output': 999}}},
                  {'type': 'message_end', 'message': {'role': 'assistant',
                   'usage': {'input': 5, 'output': 7},
                   'content': [{'type': 'text', 'text': 'done'}]}}]
        usage, final, valid = benchmark.parse_usage('\n'.join(map(json.dumps, events)))
        self.assertEqual(usage['output'], 10)
        self.assertEqual(usage['input'], 15)
        self.assertEqual(final, 'done')
        self.assertTrue(valid)
        self.assertFalse(benchmark.parse_usage('not an event')[2])

    def test_privacy_detection(self):
        self.assertTrue(privacy.scan_text('gh' + 'p_' + 'a' * 30))
        self.assertTrue(privacy.scan_text('/' + 'home/' + 'someone/project'))
        self.assertTrue(privacy.scan_text('192' + '.168.1.2'))
        self.assertTrue(privacy.scan_text('person' + '@' + 'example.org'))
        self.assertFalse(privacy.scan_text('A generic prompt without private details.'))

    def test_local_seed_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            wd = pathlib.Path(directory)
            (wd / 'names.py').write_text(benchmark.SEED)
            (wd / 'test_names.py').write_text(benchmark.TESTS)
            self.assertNotEqual(benchmark.tests(wd).returncode, 0)


if __name__ == '__main__':
    unittest.main()
