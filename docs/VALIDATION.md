# Validation de cette version

Vérifications effectuées le 15 novembre 2026 sous Windows, Python 3.11 :

- Installation du studio et des dépendances de test dans un environnement virtuel neuf, à partir des fichiers de dépendances du dépôt ; `pip check` ne signale aucun conflit.
- Compilation/import Python du serveur, du moteur et du pipeline.
- 32 plans rendus hors ligne : huit compositions, deux chartes et deux formats, dimensions et pixels vérifiés.
- Export court réel H.264/AAC en CPU, réouverture du fichier et contrôle des dimensions, de la présence audio et de la durée.
- API : interface et JavaScript disponibles, validation des paramètres, refus des origines externes, protection des écritures, refus des hôtes externes, port configurable, aucune tâche créée pendant ces tests.
- SHA-256 de la référence vocale synthétique conforme au profil.
- Syntaxe PowerShell des scripts d'installation et de lancement contrôlée.

Le clonage neuf depuis le dépôt GitHub a également passé les tests de rendu et d'API sous Windows. Les mêmes contrôles hors ligne ont réussi sur un runner Ubuntu GitHub Actions : [exécution de référence](https://github.com/DavyLss/local-video-studio/actions/runs/43706843639).

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

La version courante est installée sur le port 8511, avec les modèles locaux prêts et les cinq tâches historiques conservées. Le service 8510 n'a pas été modifié.

## Publication native et Buffer

Les contrôles `scripts/check_social.py` couvrent les secrets locaux (DPAPI sur Windows), les protections OAuth state/PKCE, les paramètres de publication CSV, les miniatures réellement générées, les contrats d'envoi YouTube/Instagram/Buffer, la reprise d'une session YouTube, le refus de doublons après un résultat incertain, les changements de compte, les signatures et morceaux Cloudinary. Un export court réel vérifie la copie TikTok, sa couverture de 0,6 s, le silence initial et la conservation du fichier original.

`scripts/check_social_ui.cjs` couvre les notices des quatre services, les champs secrets masqués après enregistrement, la connexion OAuth, les options automatiques, l'édition locale du kit, les liens de miniatures et les reçus par réseau.

Ces tests simulent tous les services externes : aucun envoi réel sur les comptes de l'utilisateur n'est prétendu. Un kit de publication a aussi été préparé avec l'Ollama du poste pour la vidéo existante sur la culture sans blâme ; les deux miniatures ont été inspectées et la collision du pied de page de la version horizontale a été corrigée.

Le service actualisé répond HTTP 200 sur l'interface, le JavaScript de publication, les réglages masqués, le kit d'une vidéo et la notice complète. Les envois restent désactivés et aucun accès réel n'a été renseigné. Le contrôle visuel automatisé du navigateur n'a pas pu être effectué : sa politique d'accès a refusé l'onglet resté sur une ancienne page d'erreur. Les tests DOM sont passés sans utiliser ce navigateur.
