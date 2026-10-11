"""Conservative content scan; findings contain paths/lines, never secret values."""
import pathlib
import re
import subprocess

ROOT = pathlib.Path(__file__).resolve().parents[1]
PATTERNS = {
    'credential-shaped token': re.compile(r'(?:gh[pousr]_|github_pat_|sk-)[A-Za-z0-9_-]{20,}'),
    'private key': re.compile(r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----'),
    'personal absolute path': re.compile(r'/(?:home|Users)/[A-Za-z0-9_.-]+/'),
    'private IPv4': re.compile(r'\b(?:10\.\d+\.\d+\.\d+|192\.168\.\d+\.\d+|172\.(?:1[6-9]|2\d|3[01])\.\d+\.\d+)\b'),
    'email address': re.compile(r'\b[A-Za-z0-9_.+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b'),
}


def scan_text(text):
    return [(number, name) for number, line in enumerate(text.splitlines(), 1)
            for name, pattern in PATTERNS.items() if pattern.search(line)]


def main():
    result = subprocess.run(['git', 'ls-files', '-z'], cwd=ROOT, capture_output=True, text=True)
    if result.returncode == 0 and result.stdout:
        paths = [ROOT / name for name in result.stdout.split('\0') if name]
    else:
        paths = [p for p in ROOT.rglob('*') if p.is_file()
                 and not any(part in ('.git', '__pycache__', 'benchmark-runs', '.venv')
                             for part in p.relative_to(ROOT).parts)]
    findings = []
    for path in paths:
        if path.is_symlink():
            findings.append((str(path.relative_to(ROOT)), 0, 'symlink requires manual review'))
            continue
        try:
            content = path.read_text(encoding='utf-8')
        except (UnicodeError, OSError):
            findings.append((str(path.relative_to(ROOT)), 0, 'unreadable/binary requires manual review'))
            continue
        findings.extend((str(path.relative_to(ROOT)), line, category)
                        for line, category in scan_text(content))
    for path, line, category in findings:
        print('{}:{}: {}'.format(path, line, category))
    print('Scanned {} files; {} findings.'.format(len(paths), len(findings)))
    return 1 if findings else 0


if __name__ == '__main__':
    raise SystemExit(main())
