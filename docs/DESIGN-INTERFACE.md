# Studio / - Interface de production, version 2

## Structure

Cinq écrans locaux, accessibles par URL :

- `#create` : composition en trois étapes (sujet, réalisation, diffusion). Les réglages restent en mémoire lors des changements d’étape. Le moniteur et le suivi de génération restent à côté du formulaire.
- `#batch-monitor` : contrôle global de la production (pause durable, reprise, purge de l’attente, arrêt forcé), liste des vidéos à venir avec retrait individuel, suivi des lots et reprise des échecs. Les commandes globales sont aussi disponibles dans l’écran de création.
- `#history` : bibliothèque avec les vrais posters locaux, paramètres, statut et suivi de diffusion. Sélectionner une vidéo ouvre son moniteur et son kit de publication.
- `#publication-settings` : un service visible à la fois, conservation du formulaire et des clés existantes lors des changements d’onglet.

- `#publications` : sélection multiple, import local, textes et dates par vidéo, calendrier mensuel et agenda de diffusion.

## Identité

Fond graphite, surfaces proches, texte argenté, signal lime réservé aux actions, sélections et progression. Les miniatures apportent les couleurs de chaque charte vidéo. Typographie système Segoe UI, repères de temps Consolas. Aucun appel à un CDN, aucune image générée pour décorer l’interface.

Les éléments réutilisables et les points de rupture sont dans `studio/static/design.css`. Le routage, les étapes, le résumé et les onglets des services sont dans `studio/static/design.js`. Les modules de génération et publication gardent leur responsabilité.

## Motion

Entrée des panneaux : 300–400 ms, déplacement vertical de 10 px et fondu. Indicateur d’étape glissant : 350 ms. Changement de charte/format du moniteur : 280 ms avec Web Animations lorsque disponible. Survol des chartes et des productions : déplacement court. Progression : interpolation de largeur. Aucune dépendance d’animation ajoutée. `prefers-reduced-motion` désactive les mouvements.

## Vérification

`npm test` couvre les anciens parcours, le CSV, les publications, les nouveaux écrans, la validation, le retour aux étapes précédentes, les onglets et la conservation des contrôles. Les trois scripts d’interface sont exécutés ; le contrôle de publication charge également le nouveau module d’interface.

Contrôle visuel dans le navigateur intégré : création, réalisation, bibliothèque et connexions, largeur proche de 830 px, sans débordement horizontal. Les règles mobiles sont présentes ; leur rendu à toutes les tailles n’a pas été contrôlé visuellement. Captures locales non versionnées : `.local/previews/`.

## Outils

Recherche de plugins effectuée : Product Design, MagicPath et Figma pertinents mais non connectés pendant cette refonte. Aucun de ces services n’a reçu le code, les médias ni les clés. Implémentation dans le dépôt existant, selon le workflow local du skill Sites.
