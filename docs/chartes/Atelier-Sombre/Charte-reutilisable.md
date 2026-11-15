# Atelier sombre — série pédagogique

Intention : montrer une idée en transformant et en déplaçant quelques objets concrets sur une scène sombre.

## Référence et portée

Référence fournie : https://www.instagram.com/reel/Dfuds2wxhnx/ . Passages observés dans le lecteur public : comparaison d'objets, brunissement et chaîne de cuisson. Observations par captures successives, sans écoute ni visionnage continu. Principes retenus : fond sombre, objets plats lisibles, titres courts en capitales, mots accentués, indicateur de progression. Les dessins, le contenu et la réalisation de cette adaptation sont originaux ; aucun média du Reel n'est incorporé.

## Constantes de série

- Fond anthracite avec lumière centrale chaude ; texte crème. Or pour le sens, rose pour la méthode, bleu-vert pour le résultat dans cet épisode.
- Typographie Segoe UI Black installée sur Windows. Sous-titres groupés par trois mots et alignés sur l'audio ; l'accent rose suit le mot parlé.
- Zone supérieure pour la parole, scène centrale pour l'action, partie basse pour la progression et la source.
- Apparitions courtes avec variation d'échelle, pivot léger et arrêt. Décaler les objets d'environ 0,24 seconde. Conserver une pose stable pour lire.
- Animation utile : ouvrir un livre, remplir une interface, compter des jetons, valider une réponse, réordonner les objets. Éviter les boucles gratuites.
- Voix locale validée conservée. Aucun bruitage ajouté.

## Variables d'épisode

Remplacer la narration, les sous-titres, l'alignement des mots, les objets et les actions. Concevoir les métaphores avant de programmer les plans. La cible, le livre et le téléphone ne doivent pas devenir une réponse automatique à tous les sujets. L'indicateur inférieur décrit une progression narrative, pas une mesure scientifique de compréhension.

## Reproduction locale

`Realisation.py` utilise `Moteur.py`, Pillow, NumPy et MoviePy. Fichiers requis dans le même dossier : `Narration.wav`, `Sous-titres.srt`, `Mots-alignes.json`. Python utilisé : environnement MoneyPrinterTurbo du projet. Export 1080 × 1920, 30 images/seconde, H.264 NVENC et AAC. Le rendu ne contacte aucun service distant.

Lancer `Realisation.py --preview` pour les dix premières secondes, puis sans option pour la vidéo complète. Pour un nouvel épisode, modifier également la chronologie et la durée de l'essai : elles sont spécifiques au Golden Circle.

## Contrôle

Contrôler des instants rapprochés des entrées et des croisements, les fins de plans, les sous-titres et l'export réel. Le contrôle de cet essai porte sur des images échantillonnées, les propriétés du fichier et les niveaux audio ; il ne vaut pas validation d'écoute ou de visionnage continu. Le son source est comparé par empreinte à la version précédente.
