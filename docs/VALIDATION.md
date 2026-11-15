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

## Extension lots et CSV

- Validation UTF-8/BOM, séparateurs, guillemets, descriptions sur plusieurs lignes, aliases français/anglais, valeurs communes et remplacements par ligne.
- Refus intégral des lots invalides sans créer de tâches ni de dossiers de vidéos ; limite de 50 vidéos.
- Tests API avec de vrais sous-processus de simulation : ordre FIFO entre lots, un seul calcul à la fois, poursuite après échec, relance des seuls échecs, annulation des attentes conservant le travail en cours, compatibilité vidéo seule et restauration des statuts interrompus après redémarrage.
- Tests DOM avec jsdom : saisie et réordonnancement, réglages, import et aperçu CSV, invalidation de l'aperçu après changement des paramètres, gestion des erreurs, suivi de progression et sélection manuelle, annulation, protection contre l'injection HTML, navigation clavier des onglets.
- Aucun test de lot ne lance les modèles IA. Les tests DOM ne remplacent pas un contrôle visuel dans un navigateur.

Le lancement automatique local de cette nouvelle version a été refusé par le contrôle d'approbation (« blocked by policy »). Le studio a été installé et ses réglages locaux préparés pour le port 8511 ; ouvrir manuellement `Lancer-Studio.ps1` pour contrôler son rendu dans le navigateur. L'ancien service 8510 n'a pas été modifié.
