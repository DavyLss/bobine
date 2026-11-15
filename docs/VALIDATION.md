# Validation de cette version

Vérifications effectuées le 15 novembre 2026 sous Windows, Python 3.11 :

- Installation du studio et des dépendances de test dans un environnement virtuel neuf, à partir des fichiers de dépendances du dépôt ; `pip check` ne signale aucun conflit.
- Compilation/import Python du serveur, du moteur et du pipeline.
- 32 plans rendus hors ligne : huit compositions, deux chartes et deux formats, dimensions et pixels vérifiés.
- Export court réel H.264/AAC en CPU, réouverture du fichier et contrôle des dimensions, de la présence audio et de la durée.
- API : interface et JavaScript disponibles, validation des paramètres, refus des origines externes, protection des écritures, refus des hôtes externes, port configurable, aucune tâche créée pendant ces tests.
- SHA-256 de la référence vocale synthétique conforme au profil.
- Syntaxe PowerShell des scripts d'installation et de lancement contrôlée.

Le clonage neuf depuis le dépôt privé GitHub a également passé les tests de rendu et d'API sous Windows. Les mêmes contrôles hors ligne ont réussi sur un runner Ubuntu GitHub Actions : [exécution de référence](https://github.com/DavyLss/local-video-studio/actions/runs/43706843639).

Limites : les poids et l'environnement Qwen existants ont déjà servi aux vidéos précédentes. Cette préparation du dépôt n'a pas refait une installation vocale complète dans un environnement neuf, téléchargé à nouveau tous les poids, ni généré une nouvelle vidéo intégrale. Le succès des tests hors ligne sous Ubuntu ne valide pas une installation vocale complète Linux/macOS.

Pour relancer les contrôles :

```powershell
.venv/Scripts/python.exe -m pip install -r requirements-test.txt -c requirements-lock.txt
.venv/Scripts/python.exe scripts/check.py
.venv/Scripts/python.exe scripts/check_api.py
```

L'export de contrôle utilise une sinusoïde, pas la narration IA ; il vérifie le conteneur et la piste audio, pas la qualité de la voix.
