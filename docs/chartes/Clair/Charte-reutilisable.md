# D’abord le sens - motion design pédagogique

## Référence examinée

https://www.youtube.com/shorts/Eo8zwQ9yxBg - « 5 SKILLS Claude Code qui vont changer ta façon de coder », TechUnlocked60.

Observations dans le lecteur YouTube : ouverture vers 3 et 8 secondes, plusieurs chapitres numérotés et conclusion vers 75 secondes. Fond très clair nuancé, grande typographie noire, numéros colorés en relief, cartes de contenu ombrées et mots de narration mis en avant dans le bas. Ces observations portent sur des images échantillonnées et la progression visible du lecteur ; elles ne constituent pas une analyse d’écoute ou un visionnage continu. Les sous-titres en boîte noire en haut étaient affichés par le lecteur et n’ont pas été repris comme élément de notre montage.

## Adaptation originale

Identité « D’abord le sens », palette bleu/violet/vert, démonstration originale d’un exercice 2 + 3, maquette d’application et construction du cercle d’or. Aucun logo, capture de site, extrait vidéo ou texte éditorial de la chaîne n’est incorporé. La narration Qwen précédente est conservée intégralement.

## Règles de série

- Fond clair très légèrement nuancé ; texte foncé très contrasté.
- Une couleur par étape, avec un rôle stable. Changer la palette selon le sujet si nécessaire.
- Titres courts ; objets centraux assez grands pour le téléphone.
- Relief discret sur les repères et ombres douces sous les objets.
- Chaque entrée, déplacement et clic explique une action ou un changement d’ordre.
- Une action principale à la fois, puis une pause pour comprendre le résultat.
- Mots de narration en groupes courts ; les termes clés prennent un accent de couleur pendant leur prononciation.
- Conclusion : une action réalisable, liée au contenu, sans appel générique à s’abonner.

## Variables du prochain épisode

Adapter la question initiale, les étapes, les objets et l’exemple, puis la consigne finale. Les objets de cet épisode ne doivent pas devenir un décor automatique pour tous les sujets. Réaligner les mots après tout changement de voix ou de texte.

## Reproduction

Le dossier contient `Realisation.py`, `Narration.wav`, `Sous-titres.srt` et `Mots-alignes.json`. Dépendances déjà présentes dans l’environnement du projet : Pillow, NumPy, MoviePy et FFmpeg. Police Windows Segoe UI Black/Segoe UI. L’encodage utilise NVENC ; adapter le codec si le dossier est déplacé sur une machine sans NVIDIA.

Depuis la racine du projet :

```powershell
& .venv/Scripts/python.exe examples/sources/Golden-Circle-Motion-Design-V2/Realisation.py
```

Options : `--preview` pour la démonstration de dix secondes, `--stills` pour les images de contrôle. Le rendu est local et ne dépend pas de ComfyUI. Les scènes de cette version sont animées par code, avec la voix IA Qwen ; elles ne sont pas des vidéos générées par diffusion.

Les contrôles de lisibilité et de trajectoire reposent sur des images échantillonnées et le code. Les contrôles techniques de l’export ne prouvent pas à eux seuls le naturel de la voix ou la fluidité perçue en lecture continue.
