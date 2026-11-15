# Apparitions plus marquées — V2

Le script conserve la voix, le texte et la direction claire de la version précédente. Il ajoute des entrées sur des calques indépendants : titre, objet principal et groupe de mots.

- Objet : arrivée en 0,48 s, taille initiale de 58 %, dépassement de 5,5 %, léger retour à 98,8 %, puis arrêt à 100 %.
- Déplacement vertical initial de 155 pixels et pivot amorti de 4,5 degrés.
- Fondu et léger flou limités au tout début de l’arrivée ; aucune boucle de mouvement après l’arrêt.
- Titres et mots : entrée plus courte, de 0,34 s, avec une amplitude moindre pour conserver la lisibilité.
- Étapes : apparition décalée de 0,18 s et trajet plus franc, puis maintien de lecture.
- Les changements de plan qui conservent le même exercice ou la même application évitent de faire rebondir à nouveau l’objet.

Réglages regroupés dans `entrance()` dans `Realisation.py`. Reproduction avec l’environnement Python existant du projet, comme la version précédente. `--preview` exporte les dix premières secondes pour contrôler les entrées ; le lancement sans option exporte la vidéo entière.

Le fichier `Controle/Apparitions.jpg` contient des images du véritable aperçu MP4 prises à courts intervalles, afin de contrôler les positions d’entrée et d’arrêt. Il ne remplace pas une lecture continue pour juger la fluidité perçue.
