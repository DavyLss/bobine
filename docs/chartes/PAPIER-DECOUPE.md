# Papier découpé

Une explication devient un petit théâtre d'objets : des papiers se posent, des idées se transmettent et un oiseau plié accompagne la lecture.

## Référence et périmètre

Référence demandée : [publication de daris_sotraya](https://www.instagram.com/p/Df1ySwyINgC/). Observation directe de trois images du lecteur Instagram aux environs de 3,4 s, 11,3 s et 24 s, sur une vidéo de 27,5 s. Elles montrent des fonds en bandes vertes, ocre et violet sombre, des bandeaux irréguliers, des captures encadrées, des sous-titres sur papiers séparés et un personnage orange derrière un comptoir.

Ces prélèvements documentent la composition, pas une analyse continue du mouvement ni une écoute du son. Bobine reprend des principes généraux du collage et du théâtre de papier. Aucun média, texte, personnage, logo ou enregistrement de cette publication n'est intégré. Le personnage Bobine est un oiseau origami original, sans mains humaines. Les captures de sites de la référence sont remplacées par des schémas liés au scénario.

## Constantes de série

- Fond vert ardoise `#45665E`, brun `#876346` ou bleu ardoise `#4D5266`, alterné par plan, avec des joints de papier verticaux. Matière géométrique sans filtre de bruit.
- Papier crème `#F5EDDA`, encre `#252C2A`, accent jaune `#E2BD50`, objets sarcelle `#387A75` et brique `#B54F3D`.
- Titres en capitales condensées sur bandeaux découpés. Captions à empattements sur papiers individuels, mot actif jaune. Impact système pour les titres, avec repli DejaVu Sans Condensed Bold ; annotations et captions réutilisent les polices système et replis libres de Carnet animé. Aucune fonte propriétaire redistribuée.
- Oiseau en facettes : corps sarcelle, aile crème, bec jaune. Une articulation d'aile pointe puis revient au repos, sans boucle de flottement.
- Ombres franches décalées, bords irréguliers déterministes. Pas d'éclats, de confettis ni de bruitage ajouté.

## Mouvement et pédagogie

1. Le titre glisse pendant 0,45 s, puis reste lisible.
2. Les éléments entrent en décalé de 0,23 s : translation de 95 px et rotation maximale de 7 degrés, amorties en 0,55 s.
3. Une action liée au schéma se déroule : déplacement d'un message pour un flux, retour pour une boucle, construction de cible et arrivée de flèche, comparaison de panneaux.
4. L'oiseau entre pendant 0,6 s, soulève une note puis repose son aile. Il ne remplace pas l'action explicative.
5. Le plan suivant renouvelle le fond et les objets. La sortie finale s'efface en 0,35 s.

La durée et les mots viennent de la chronologie de narration. L'animation des objets est calée sur le début du plan ; elle ne possède pas encore de repérage sémantique geste par geste sur chaque mot. Les graphiques restent explicitement illustratifs, sans mesures inventées.

## Variables et utilisation

Titre, sujet, labels, type de schéma, narration et durée varient par épisode. Sélectionner **Papier découpé** dans La réalisation ; CSV : `charte=papier` ou `papier découpé`. Reel 9:16 et standard 16:9 possèdent leur cadrage natif. Les voix homme, femme et Duo utilisent les références validées ; aucun nom d'animateur n'est affiché.

Rendu local : `studio/renderer_papier.py`, diagrammes et polices réutilisés depuis les moteurs existants. Aucun téléchargement ou service d'images n'est requis. Le contrôle automatisé `scripts/check_carnet.py` couvre les deux directions papier, leurs alias, les huit diagrammes, les deux formats, les miniatures et de courts exports H.264/AAC. Il vérifie des différences de trames, pas une note de fluidité ni de naturel vocal. Une relecture artistique de chaque épisode reste nécessaire.
