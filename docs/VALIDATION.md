# Validation de cette version

Vérifications effectuées le 15 novembre 2026 sous Windows, Python 3.11 :

- Installation du studio et des dépendances de test dans un environnement virtuel neuf, à partir des fichiers de dépendances du dépôt ; `pip check` ne signale aucun conflit.
- Compilation/import Python du serveur, du moteur et du pipeline.
- 32 plans rendus hors ligne : huit compositions, deux chartes et deux formats, dimensions et pixels vérifiés.
- Export court réel H.264/AAC en CPU, réouverture du fichier et contrôle des dimensions, de la présence audio et de la durée.
- API : interface et JavaScript disponibles, validation des paramètres, refus des origines externes, protection des écritures, refus des hôtes externes, port configurable, aucune tâche créée pendant ces tests.
- SHA-256 de la référence vocale synthétique conforme au profil.
- Syntaxe PowerShell des scripts d'installation et de lancement contrôlée.

Limites : les poids et l'environnement Qwen existants ont déjà servi aux vidéos précédentes. Cette préparation du dépôt n'a pas refait une installation vocale complète dans un environnement neuf, téléchargé à nouveau tous les poids, ni généré une nouvelle vidéo intégrale. L'installation Linux/macOS et la future exécution GitHub Actions n'étaient pas encore validées au moment de ce document.

Pour relancer les contrôles :

```powershell
.venv/Scripts/python.exe -m pip install -r requirements-test.txt -c requirements-lock.txt
.venv/Scripts/python.exe scripts/check.py
.venv/Scripts/python.exe scripts/check_api.py
```

L'export de contrôle utilise une sinusoïde, pas la narration IA ; il vérifie le conteneur et la piste audio, pas la qualité de la voix.
