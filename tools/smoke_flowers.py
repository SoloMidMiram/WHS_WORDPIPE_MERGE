"""Run a synthetic Chronicle smoke test without restricted Flowers sources.

Install .[chronicle,test] first. Requires Windows PowerShell or pwsh.
"""
from pathlib import Path
import json
import shutil
import subprocess
import tempfile


def main():
    root = Path(__file__).resolve().parents[1]
    shell = shutil.which('pwsh') or shutil.which('powershell')
    if shell is None:
        raise SystemExit('PowerShell is required')
    with tempfile.TemporaryDirectory(prefix='flowers-synthetic-') as temp:
        work = Path(temp)
        source = work / 'input'
        source.mkdir()
        (source / 'synthetic.md').write_text(
            '- **2026-01-01 - Synthetic plant market:** Retail plant price in Tehran.\n',
            encoding='utf-8',
        )
        output = work / 'output'
        assert not output.exists()
        subprocess.run([shell, '-NoProfile', '-File', str(root / 'pipeline/chain.ps1'),
                        '-InputDir', str(source), '-OutputDir', str(output), '-Verify'],
                       cwd=root, check=True)
        evidence = json.loads((output / 'run.json').read_text(encoding='utf-8-sig'))
        assert evidence['status'] == 'ok'
        assert [stage['status'] for stage in evidence['stages']] == ['ok'] * 5
        assert (output / 'appendix/event_index.md').is_file()
        print('synthetic_smoke: PASS (five stages; no restricted source text)')


if __name__ == '__main__':
    main()
