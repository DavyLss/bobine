"""Check the embedded window contract without opening a GUI or accessing networks."""
import sys
import tempfile
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'studio'))
import desktop

calls = {}
view = SimpleNamespace(settings={}, create_window=lambda *a, **kw: calls.update(window=(a, kw)),
                       start=lambda **kw: calls.update(start=kw))
native = SimpleNamespace(shell32=SimpleNamespace(SetCurrentProcessExplicitAppUserModelID=lambda value: None))
with tempfile.TemporaryDirectory() as folder, patch.object(desktop, 'ROOT', Path(folder)), \
        patch.object(desktop.ctypes, 'windll', native, create=True), patch.dict(sys.modules, webview=view):
    desktop.main()
    assert calls['window'][0] == ('Bobine', f'http://127.0.0.1:{desktop.PORT}/')
    assert 'js_api' not in calls['window'][1]
    assert calls['start']['gui'] == 'edgechromium'
    assert calls['start']['debug'] is False
    assert calls['start']['private_mode'] is False
    assert Path(calls['start']['storage_path']).is_relative_to(Path(folder))
    assert view.settings == {'ALLOW_DOWNLOADS': True, 'ALLOW_FILE_URLS': False}
print('OK: forced WebView2, isolated storage, downloads and no application Python bridge.')
