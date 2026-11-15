# Contribuer à Local Video Studio

Les rapports de bugs, améliorations de documentation et contributions sont bienvenus. Le projet est maintenu sur le temps disponible, sans délai de réponse garanti.

## Préparer le poste

Suivre [l’installation](docs/INSTALLATION.md), puis travailler sur une branche dédiée. Windows 64 bits et Python 3.11 constituent la plateforme d’utilisation documentée. Node.js 24.15+ est nécessaire uniquement pour les tests d’interface.

Pour les vérifications hors ligne, les modèles et les clés de publication ne sont pas nécessaires :

```powershell
py -3.11 -m venv .venv
.venv/Scripts/python.exe -m pip install -r requirements.txt -r requirements-test.txt -c requirements-lock.txt
.venv/Scripts/python.exe scripts/check.py
.venv/Scripts/python.exe scripts/check_api.py
.venv/Scripts/python.exe scripts/check_batches.py
.venv/Scripts/python.exe scripts/check_social.py
.venv/Scripts/python.exe scripts/check_cleanup.py
npm ci
npm test
```

La CI exécute ces contrôles sous Ubuntu et vérifie la syntaxe des scripts PowerShell. Les tests de rendu et de lots utilisent de courts exports ou des sous-processus simulés ; ils ne certifient pas une génération IA complète sur toutes les machines.

## Proposer une modification

- Décrire le problème et le résultat attendu ; pour un changement important, ouvrir une discussion dans une issue avant une implémentation conséquente.
- Garder les changements ciblés, documenter les nouveaux réglages et ajouter une vérification utile pour les changements de comportement.
- Fournir les étapes de reproduction, les tests effectués et, pour l’interface, des captures sans données confidentielles.
- Préserver l’écoute sur localhost, les protections des requêtes et le caractère facultatif de la publication.
- Ne jamais utiliser de vrais comptes de publication dans les tests automatisés.

Ne pas committer `.local/`, `.env`, des clés, jetons, enregistrements personnels, journaux, vidéos générées, poids de modèles ou environnements Python. Vérifier également les captures, descriptions d’issues et journaux copiés.

En soumettant une contribution, vous confirmez disposer des droits nécessaires et acceptez sa distribution sous la [licence MIT](LICENSE). Ne pas reprendre de code ou d’actifs tiers sans licence et attribution appropriées. Signaler les vulnérabilités selon [SECURITY.md](SECURITY.md).
