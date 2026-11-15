# Installation détaillée

Windows 64 bits, Python 3.11. Exécuter depuis la racine du dépôt :

```powershell
py -3.11 -m venv .venv
py -3.11 -m venv .venv-voice
.venv/Scripts/python.exe -m pip install -r requirements.txt -c requirements-lock.txt
.venv-voice/Scripts/python.exe -m pip install torch==2.6.0 torchaudio==2.6.0 --index-url https://download.pytorch.org/whl/cpu
.venv-voice/Scripts/python.exe -m pip install -r requirements-voice.txt
.venv/Scripts/python.exe scripts/download_models.py
ollama pull qwen3:4b
.venv/Scripts/python.exe studio/server.py
```

Ollama doit être lancé. La génération utilise ses fichiers locaux et les poids téléchargés dans `.local/models`. Les deux environnements sont nécessaires : ne pas fusionner leurs dépendances. Ne pas versionner les environnements virtuels.

Pour un second studio sans toucher au premier : `$env:STUDIO_PORT = '8511'`. Les chemins peuvent être déplacés via les variables de `.env.example`, à définir avant le lancement. Choisir également des dossiers `STUDIO_DATA_DIR` et `STUDIO_JOBS_DIR` distincts si deux instances travaillent simultanément.

Le lanceur PowerShell ne termine jamais un service déjà actif. Pour voir les erreurs, lancer `python studio/server.py` au premier plan. Les journaux du lanceur sont dans `.local/`.

Le code de rendu prévoit les polices Segoe sous Windows et DejaVu sous Linux. Aucun installateur Linux/macOS complet n'est fourni et ces plateformes n'ont pas été validées. Une police personnalisée exige les variables `STUDIO_FONT` et `STUDIO_FONT_BOLD`.

Pour une migration : cloner le dépôt, installer, puis restaurer séparément les dossiers de modèles et de travail. L'historique existant de l'ancien poste n'est pas importé automatiquement. Les chemins relatifs du dépôt ne contiennent aucun chemin personnel du poste d'origine.
