# Carnet animé

Direction originale de Bobine, réutilisable avec `theme=carnet`. Intention : expliquer un raisonnement comme une note dessinée qui prend vie.

## Référence et limites de l’analyse

La publication [Instagram fournie](https://www.instagram.com/p/Df24CQ1J_Pc/) a été observée dans le navigateur à plusieurs moments de sa boucle de 31 secondes, notamment vers 1, 5, 16 et 30 secondes. Observations : fond crème à points, gros titres à empattements, petites légendes techniques, panneaux contrastés, compositions qui changent et petite mascotte orange déplacée entre les plans. Ces observations échantillonnées ne constituent pas une analyse image par image de la fluidité. Le son de cette référence n’a pas été évalué.

Bobine reprend des principes généraux de composition et de rythme. Aucun logo, texte, personnage, image ou extrait audio du créateur n’est intégré. Le guide optique circulaire, les diagrammes et les compositions de Bobine sont dessinés par code.

## Constantes de série

- Papier `#F0EBE0`, encre `#262923`, surface `#FCF9F2`.
- Vert pétrole `#24675F` pour organiser ; terre cuite `#BB5437` pour attirer le regard ; ocre `#B38632` pour le troisième niveau.
- Titres à empattements : Georgia Bold sur Windows, DejaVu Serif Bold sur Linux ; annotations en Consolas ou DejaVu Sans Mono. Polices du système, non redistribuées.
- Grille de points régulière, pas de grain aléatoire ; ombres solides décalées, angles légèrement adoucis ; aucun flou décoratif.
- Un petit instrument optique original accompagne le raisonnement. Il rejoint sa position, se pose et pointe vers le schéma ; pas de flottement permanent.
- Les noms des intervenants ne sont pas affichés, y compris en Duo.

## Récit et mouvement

Un plan porte une idée nouvelle. Le titre apparaît progressivement par mots, sur des lignes fixées à l’avance. Le diagramme entre latéralement sur 0,48 seconde puis poursuit son action utile : paquet transmis, boucle de retour, progression d’étapes, barres illustratives ou interaction de personnages. Les comparaisons sont neutres : pas de coche de réussite automatique.

Le cadrage utilise les limites fixes du diagramme complet pour éviter les changements d’échelle pendant son apparition. Le format Reel superpose titre, schéma, narration et guide ; le 16:9 place le récit à gauche et le schéma à droite. Les sous-titres de trois mots soulignent le mot actif, sans pavé coloré.

Variables par épisode : sujet, titre de chaque plan, type de schéma, libellés, narration, chronologie et voix. Le texte et les faits restent à relire ; la charte ne valide pas le fond.

## Utilisation et contrôle

Choisir **Carnet animé** dans La réalisation, ou `carnet` / `carnet animé` dans la colonne `charte` du CSV. Compatible avec narration homme, femme et Duo. La dernière direction utilisée est conservée comme pour les autres chartes.

Moteur : `studio/renderer_carnet.py`, réutilisant les compositions de `studio/renderer.py`. Contrôle reproductible : `python scripts/check_carnet.py` (huit schémas, deux formats, variation des images pendant l’entrée, miniatures et export court H.264/AAC). La variation de pixels ne certifie pas le naturel de l’animation ; inspecter aussi un extrait rendu avant publication.
