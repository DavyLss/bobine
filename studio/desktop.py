"""Bobine's Windows window, with a forced WebView2 engine and isolated storage."""
import ctypes
import logging
import sys
from pathlib import Path

from config import ROOT, PORT


def main():
    import webview

    if '--check' in sys.argv:
        from webview.platforms import winforms
        if not winforms.is_chromium:
            raise RuntimeError('Installer Microsoft WebView2 Runtime : https://developer.microsoft.com/microsoft-edge/webview2/')
        print('WebView2 disponible.')
        return

    storage = ROOT / '.local' / 'webview2-profile'
    storage.mkdir(parents=True, exist_ok=True)
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('DavyLss.Bobine')
    webview.settings['ALLOW_DOWNLOADS'] = True
    webview.settings['ALLOW_FILE_URLS'] = False
    entry = ROOT / 'studio/static/index.html'
    revision = entry.stat().st_mtime_ns if entry.exists() else 0
    webview.create_window('Bobine', f'http://127.0.0.1:{PORT}/?ui={revision}', width=1280,
                          height=900, min_size=(800, 600), background_color='#101113',
                          text_select=True)
    # Never fall back to an old engine or to the user's browser.
    webview.start(gui='edgechromium', debug=False, private_mode=False,
                  storage_path=str(storage), icon=str(ROOT / 'studio/static/brand/favicon.ico'))


if __name__ == '__main__':
    try:
        main()
    except Exception:
        folder = ROOT / '.local'
        folder.mkdir(exist_ok=True)
        logging.basicConfig(filename=folder / 'desktop-error.log', encoding='utf-8', level=logging.ERROR)
        logging.exception('La fenêtre Bobine ne peut pas démarrer.')
        if '--check' in sys.argv:
            raise
        ctypes.windll.user32.MessageBoxW(None,
            'Impossible de démarrer la fenêtre Bobine. Exécuter Installer-Fenetre.ps1 et vérifier le runtime Microsoft WebView2. Détails : .local/desktop-error.log',
            'Bobine', 0x10)
        sys.exit(1)
