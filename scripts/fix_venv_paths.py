"""Resolve Windows virtualized Python paths before using a venv outside its installer."""
import os
import sys
from pathlib import Path


def repair(config: Path, base_executable: Path):
    base = base_executable.resolve(strict=True)
    text = config.read_text(encoding='utf-8')
    lines = text.splitlines()
    values = {'home': str(base.parent), 'executable': str(base)}
    updated = []
    for line in lines:
        key = line.partition('=')[0].strip()
        updated.append(f'{key} = {values[key]}' if key in values else line)
    result = '\n'.join(updated) + '\n'
    if result != text:
        config.write_text(result, encoding='utf-8')
    return base


if __name__ == '__main__':
    config = Path(sys.prefix) / 'pyvenv.cfg'
    if sys.prefix == sys.base_prefix or not config.is_file():
        raise SystemExit('Exécuter avec le Python de l’environnement virtuel à corriger.')
    repair(config, Path(os.path.realpath(sys._base_executable)))
    print('Chemins Python normalisés pour le lancement depuis Windows.')
