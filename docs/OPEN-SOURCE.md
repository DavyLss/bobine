# Préparation de la publication open source

État de préparation au 15 novembre 2026. Ce document décrit les contrôles effectués, sans certifier l’absence de toute vulnérabilité ou de toute question de droits.

## Choix du mainteneur

- Licence du code spécifique, des chartes, exemples et référence vocale fournie : MIT, dans la mesure des droits détenus ; auteur de la notice : DavyLss.
- Le mainteneur a confirmé disposer de l’autorité nécessaire pour publier ces contributions.
- La référence synthétique actuelle est incluse et réutilisable ; aucune exclusivité sur le timbre n’est promise.
- Les composants tiers conservent leurs licences propres. Le dépôt ne contient pas les poids des modèles ni les environnements installés.

## Contrôles de confidentialité

- Fichiers suivis et versions de fichiers de l’historique local examinés : recherche des clés configurées, de formats courants de jetons, de clés privées, de fichiers d’état et de chemins utilisateur personnels ; aucun résultat détecté lors du contrôle.
- Les données de travail, configurations privées, journaux et médias générés sont exclus de Git. La seule piste audio versionnée est la référence synthétique documentée.
- Les commits examinés utilisent une adresse GitHub noreply.
- Six journaux GitHub Actions terminés disponibles lors de l’audit ont été contrôlés : aucune clé configurée ni jeton correspondant aux formats recherchés détecté. Aucun artefact Actions n’était présent.

Ces recherches ciblées ne constituent pas une détection exhaustive de tous les secrets possibles. Tout accès compromis doit être révoqué auprès de son fournisseur.

## Documents et maintenance

- [Licence MIT](../LICENSE).
- [Notice des dépendances et ressources](../THIRD_PARTY_NOTICES.md).
- [Contributions et vérifications](../CONTRIBUTING.md).
- [Périmètre et signalement de sécurité](../SECURITY.md).
- [Règles de participation](../CODE_OF_CONDUCT.md).
- Modèles de bug, proposition et pull request dans `.github/`.
- Dependabot configuré pour pip et npm, avec un nombre limité de propositions de mise à jour. Aucune fusion automatique.
- Le workflow de vérification demande uniquement la lecture du contenu du dépôt.

## Validation et limites

Les tests hors ligne couvrent le profil vocal, 32 plans, un export CPU, l’API, les lots, la pause et reprise, l’arrêt des processus, la publication simulée, la purge et les interactions de l’interface. Windows constitue la plateforme d’utilisation documentée ; des contrôles hors ligne passent aussi sur Ubuntu. Une génération complète sur toutes les configurations matérielles n’est pas garantie.

L’inventaire des licences tierces recense les composants principaux. Une future redistribution de wheels, de modèles ou de binaires dans un installateur autonome exige une vérification supplémentaire des fichiers effectivement embarqués et de leurs obligations.

## Passage en public

La préparation documentaire ne change pas la visibilité du dépôt. Le passage en public doit être validé séparément par le mainteneur, après revue du commit préparé.

Au moment du passage en public :

1. Vérifier la réussite du workflow du commit publié.
2. Activer le signalement privé des vulnérabilités et vérifier l’accès au formulaire décrit dans SECURITY.md.
3. Vérifier les alertes de dépendances, le secret scanning et la protection des envois de secrets disponibles pour le compte.
4. Vérifier la détection de la licence MIT sur la page du dépôt.

Le code et les anciens commits, discussions et journaux publiés peuvent être copiés. Repasser ensuite le dépôt en privé ne retire pas les copies et forks déjà réalisés.
