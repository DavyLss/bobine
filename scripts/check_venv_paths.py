import tempfile
from pathlib import Path
from fix_venv_paths import repair

with tempfile.TemporaryDirectory() as folder:
    root = Path(folder)
    physical = root / 'runtime with spaces' / 'python.exe'
    physical.parent.mkdir()
    physical.touch()
    config = root / 'pyvenv.cfg'
    config.write_text('home = invisible/runtime\ninclude-system-site-packages = false\nversion = 3.11.18\nexecutable = invisible/python.exe\n', encoding='utf-8')
    repair(config, physical)
    fixed = config.read_text(encoding='utf-8')
    assert f'home = {physical.parent.resolve()}' in fixed
    assert f'executable = {physical.resolve()}' in fixed
    assert 'include-system-site-packages = false' in fixed
    before = config.stat().st_mtime_ns
    repair(config, physical)
    assert config.stat().st_mtime_ns == before
print('OK: canonical runtime paths, paths with spaces, preserved venv settings and idempotence.')
