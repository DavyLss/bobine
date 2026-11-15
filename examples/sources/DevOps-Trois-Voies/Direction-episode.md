# Les trois voies du DevOps

Reel pédagogique pour débutants et équipes informatiques. Objectif : distinguer flux, retours rapides et expérimentation/apprentissage, et comprendre qu'ils améliorent un seul système de travail.

## Continuité de série

Cet épisode emploie la charte Atelier sombre conservée dans `../Chartes-reutilisables/Atelier-Sombre/Charte-reutilisable.md`. Les deux chartes précédentes restent intactes. Même palette, même typographie, apparitions brèves et sous-titres synchronisés. La référence masculine est `../Voix-Masculine-Reference/Reference-Homme.wav` : aucune nouvelle voix VoiceDesign et aucun service de synthèse distant.

## Métaphore et actions propres à l'épisode

Le changement est un paquet doré. Il attend devant les tests, traverse les étapes et arrive à l'utilisateur. Les retours prennent le chemin inverse avec un signal rose. Une erreur déclenche une correction visible. L'analyse relie l'incident aux conditions du travail ; l'expérimentation compare deux situations illustratives, puis l'équipe partage l'apprentissage. Le graphique n'est pas une statistique réelle et ne promet pas un résultat chiffré.

Plans : blocage initial ; présentation des trois voies ; flux vers l'utilisateur ; réduction de la file d'attente ; livraison ; trajet retour ; échec, signal et correction ; expérimentation ; analyse des conditions ; mesure et partage ; synthèse des trois voies ; trois questions pour commencer.

Le modèle ne se réduit pas à une chaîne d'outils : l'explication inclut l'ensemble du système, les attentes, les retours, la discussion des erreurs et l'apprentissage partagé. La chaîne code/tests/production/utilisateur est un exemple volontairement simplifié.

## Source

Gene Kim, IT Revolution, « The Three Ways: The Principles Underpinning DevOps » : https://itrevolution.com/articles/the-three-ways-principles-underpinning-devops/ . Résumé indexé consulté ; page directe refusée par le serveur. Les trois principes sont présentés comme un cadre DevOps, pas comme une garantie de performance.

## Fichiers et reproduction

`Scenario.json` est le texte de référence. `Narration.wav`, `Sous-titres.srt`, `Chronologie.json` et `Mots-alignes.json` sont alignés sur les prises générées. `Realisation.py` et `Mouvement.py` produisent les médias localement avec Pillow, MoviePy et FFmpeg NVENC. Python utilisé : `../MoneyPrinterTurbo/.venv/Scripts/python.exe`.

Lancer `Realisation.py --preview` pour un extrait représentatif centré sur le blocage puis la livraison ; sans option pour le film entier. Les durées provisoires servent uniquement à préparer un essai visuel avant que la narration soit prête.

## Contrôle

Le contrôle technique vérifie dimensions, durée, présence et niveaux de l'audio ; la reconnaissance vocale vérifie le texte. Des captures rapprochées contrôlent les apparitions, le débouchage de la file et la transition ; des images extraites de l'export final contrôlent les douze plans. Ces contrôles ne constituent pas une écoute ou un visionnage continu. Le naturel et la stabilité perceptive de la voix ne sont pas mesurés par la transcription.
