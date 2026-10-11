"""Run a synthetic real-worker A/B experiment using existing Pi credentials."""
import argparse
import hashlib
import json
import pathlib
import subprocess
import sys
import tempfile
import time

ROOT = pathlib.Path(__file__).resolve().parents[1]
SEED = 'def unique_names(names):\n    return sorted(set(names))\n'
TESTS = '''import unittest
from names import unique_names
class Tests(unittest.TestCase):
 def test_empty(self): self.assertEqual(unique_names([]), [])
 def test_order(self): self.assertEqual(unique_names(['Zoe','Amy']), ['Zoe','Amy'])
 def test_strip(self): self.assertEqual(unique_names([' Amy ', ' Bob ']), ['Amy','Bob'])
 def test_case(self): self.assertEqual(unique_names(['Amy','amy','AMY']), ['Amy'])
 def test_blank(self): self.assertEqual(unique_names(['', ' ', '\\t']), [])
 def test_unicode(self): self.assertEqual(unique_names(['Straße','STRASSE']), ['Straße'])
 def test_combined(self): self.assertEqual(unique_names([' Bob ','amy','BOB','',' Amy ']), ['Bob','amy'])
 def test_no_mutation(self):
  a=[' Bob ','bob']; unique_names(a); self.assertEqual(a,[' Bob ','bob'])
if __name__=='__main__': unittest.main()
'''
TASK = ('Fix unique_names in names.py. Trim each input string, discard empty strings, '
        'deduplicate using casefold(), preserve first spelling after trimming and original '
        'order, and do not mutate input. Inspect files, reproduce tests, fix only names.py, '
        'and run python3 -m unittest -v. Do not edit test_names.py, install dependencies, '
        'change settings or touch files outside the current workspace. Report in Traditional Chinese.')


def parse_usage(raw):
    messages = []
    for line in raw.splitlines():
        try:
            event = json.loads(line)
        except ValueError:
            continue
        message = event.get('message', {})
        if event.get('type') == 'message_end' and message.get('role') == 'assistant':
            messages.append(message)
    fields = ('input', 'output', 'cacheRead', 'cacheWrite', 'reasoning', 'totalTokens')
    usage = {key: sum(m.get('usage', {}).get(key, 0) for m in messages) for key in fields}
    final = '\n'.join(c.get('text', '') for c in messages[-1].get('content', [])
                      if c.get('type') == 'text') if messages else ''
    return usage, final, bool(messages) and all('output' in m.get('usage', {}) for m in messages)


def tests(workdir):
    return subprocess.run([sys.executable, '-m', 'unittest', '-v'], cwd=workdir,
                          capture_output=True, text=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pi-command', default='pi', help='Executable or wrapper path, not shell syntax')
    parser.add_argument('--provider', required=True)
    parser.add_argument('--model', required=True)
    parser.add_argument('--thinking', default='low')
    parser.add_argument('--timeout', type=int, default=240)
    args = parser.parse_args()
    output_root = ROOT / 'benchmark-runs'
    output_root.mkdir(exist_ok=True)
    run_dir = pathlib.Path(tempfile.mkdtemp(prefix='pi-ab-', dir=output_root))
    style = (ROOT / 'prompts/worker-compact.md').read_text(encoding='utf-8')
    results = []
    for label in ('A', 'B'):
        workdir = run_dir / label
        workdir.mkdir()
        (workdir / 'names.py').write_text(SEED)
        (workdir / 'test_names.py').write_text(TESTS)
        red = tests(workdir)
        if red.returncode == 0:
            raise RuntimeError('Seed unexpectedly passed; benchmark is invalid')
        (run_dir / (label + '-red.txt')).write_text(red.stdout + red.stderr)
        command = [args.pi_command, '--offline', '--provider', args.provider,
                   '--model', args.model, '--thinking', args.thinking, '--no-session',
                   '--no-mcp', '--no-skills', '--no-context-files', '--mode', 'json']
        if label == 'B':
            command += ['--append-system-prompt', style]
        command += ['--print', TASK]
        started = time.monotonic()
        try:
            response = subprocess.run(command, cwd=workdir, capture_output=True,
                                      text=True, timeout=args.timeout)
            (run_dir / (label + '-events.jsonl')).write_text(response.stdout)
            (run_dir / (label + '-stderr.txt')).write_text(response.stderr)
            usage, final, usage_valid = parse_usage(response.stdout)
            green = tests(workdir)
            unchanged = (workdir / 'test_names.py').read_text() == TESTS
            extras = [p.name for p in workdir.iterdir()
                      if p.name not in ('names.py', 'test_names.py', '__pycache__')]
            result = dict(label=label, exit_code=response.returncode, usage=usage,
                          usage_valid=usage_valid, final=final, tests_exit=green.returncode,
                          tests_unchanged=unchanged, unexpected_files=extras,
                          implementation_sha256=hashlib.sha256((workdir / 'names.py').read_bytes()).hexdigest(),
                          seconds=round(time.monotonic() - started, 2))
            (run_dir / (label + '-tests.txt')).write_text(green.stdout + green.stderr)
        except subprocess.TimeoutExpired:
            result = dict(label=label, error='timeout')
        results.append(result)
        (run_dir / 'results.json').write_text(json.dumps(results, ensure_ascii=False, indent=2))
        print(json.dumps(result, ensure_ascii=False), flush=True)
    accepted = all(r.get('exit_code') == 0 and r.get('tests_exit') == 0
                   and r.get('tests_unchanged') and r.get('usage_valid')
                   and not r.get('unexpected_files') for r in results)
    print('Artifacts:', run_dir)
    if accepted:
        a, b = (r['usage']['output'] for r in results)
        if a:
            print('Output-token reduction: {:.1f}%'.format((a - b) / a * 100))
        print('Total tokens (A, B):', *(r['usage']['totalTokens'] for r in results))
        print('Identical implementation:', results[0]['implementation_sha256'] == results[1]['implementation_sha256'])
        print('Output reduction is not a total-cost claim.')
    return 0 if accepted else 1


if __name__ == '__main__':
    raise SystemExit(main())
