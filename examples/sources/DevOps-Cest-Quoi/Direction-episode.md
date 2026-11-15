# C'est quoi le DevOps ?

Objectif : expliquer le DevOps à une personne qui débute, par la collaboration autour d'une modification de service. Montrer qu'il associe culture, pratiques et outils, avec une responsabilité qui continue après la livraison.

## Identité conservée

Charte Atelier sombre : objets illustrés originaux, palette crème/or/rose/bleu-vert, titres courts, sous-titres par groupes de mots, entrées avec pivot et rebond bref. Les deux chartes réutilisables restent dans `../Chartes-reutilisables/`.

Voix : profil local Narrateur-Homme-01, référence durable `../Voix-Masculine-Reference/Reference-Homme.wav`. Chaque phrase utilise le même prompt locuteur Qwen3-TTS 1.7B Base. Aucun appel à une synthèse vocale distante ni redessin VoiceDesign du timbre.

## Exemple et progression

Un site de réservation fictif reçoit un bouton Annuler. L'épisode commence par une différence entre fonctionnement local et service en ligne. Les deux rôles isolés se rapprochent, définissent un objectif partagé, préparent le changement avec qualité et sécurité, le testent et le déploient. Après la mise en ligne, ils observent, écoutent, corrigent et apprennent. La conclusion propose d'enlever un obstacle ensemble.

Animations spécifiques : séparation puis rapprochement des rôles ; apparition du bouton ; convergence des quatre compétences ; trajet du changement dans la chaîne de livraison ; tracé d'un signal de surveillance ; erreur puis correction visible ; retour vers l'équipe. La courbe est une illustration sans données réelles.

Les repères Collaborer / Automatiser / Apprendre facilitent la lecture de l'épisode. Ils ne sont pas présentés comme une définition normative exhaustive ou comme un nouveau modèle officiel.

## Sources

- Microsoft Learn, « What is DevOps? » : https://learn.microsoft.com/en-us/devops/what-is-devops . Culture, collaboration entre rôles, cycle de vie, automatisation, surveillance et apprentissage.
- Atlassian, « DevOps Culture » : https://www.atlassian.com/devops/what-is-devops/devops-culture . Collaboration et responsabilité partagée entre développement et exploitation.

L'exemple du site et les dessins sont originaux. Il n'est pas promis qu'une simple installation d'outils garantisse une performance ou supprime les incidents.

## Fichiers et contrôle

`Scenario.json` contient le texte de référence. `Narration.wav`, `Chronologie.json`, `Mots-alignes.json` et `Sous-titres.srt` sont recalés sur le son produit. Le rendu local utilise `Realisation.py` et `Mouvement.py` avec Python, Pillow, MoviePy et FFmpeg NVENC. `--preview` exporte dix secondes autour du problème du bouton et de sa correction ; sans option, le film complet.

Contrôle du texte par reconnaissance vocale, des niveaux et propriétés audio/vidéo, des douze plans et d'instants rapprochés dans l'extrait. Ce contrôle ne constitue pas un visionnage continu ou une validation d'écoute ; la transcription ne mesure ni le naturel ni la stabilité perceptive du timbre.
