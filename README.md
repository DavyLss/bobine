# Local Video Studio

Studio vidéo pédagogique en français, exécuté sur le poste : scénario IA, voix masculine de référence, sous-titres synchronisés et animations. Interface simple : titre, description, charte, durée moyenne, format, puis génération avec suivi et historique.

Deux directions conservées : **Atelier sombre** et **Éditorial clair**, avec apparitions, rebonds, objets et typographie. La dernière charte utilisée est mémorisée. Formats **Reel 1080 × 1920** et **Standard 1920 × 1080**, 30 images/s, MP4 H.264/AAC.

## Installation Windows

Prérequis : [Python 3.11 64 bits](https://www.python.org/downloads/), [Git](https://git-scm.com/downloads) et [Ollama](https://ollama.com/download). Lancer Ollama avant l'installation. Prévoir plusieurs gigaoctets de téléchargements et de stockage ; 16 Go de RAM minimum conseillé, 32 Go préférable. La voix fonctionne sur CPU et peut prendre plusieurs minutes par vidéo. Un GPU NVIDIA compatible accélère le rendu ; le CPU est utilisé automatiquement si NVENC est indisponible.

```powershell
git clone https://github.com/DavyLss/local-video-studio.git
cd local-video-studio
.\Installer.ps1
.\Lancer-Studio.ps1
```

Ouvrir **http://127.0.0.1:8510/**. Le dépôt étant privé, il faut un compte GitHub autorisé pour le cloner. Si PowerShell bloque les scripts, ne pas modifier sa politique sans comprendre la règle du poste : les commandes Python équivalentes sont dans [INSTALLATION.md](docs/INSTALLATION.md).

`Installer.ps1 -SkipModels` installe seulement les dépendances. `Installer.ps1 -Python 'C:/chemin/python.exe'` sélectionne explicitement un Python 3.11. Les deux environnements Python isolent les dépendances du studio et celles de Qwen.

## Utilisation

1. Donner un titre et une description précise du public, du sujet et de l'exemple souhaité.
2. Choisir une charte, la durée cible (15 à 180 secondes), puis Standard ou Reel.
3. Lancer et suivre scénario → voix → synchronisation → rendu → vérification.
4. Relire et écouter avant publication. Télécharger la vidéo, le scénario et les sous-titres depuis l'interface.

La durée est une cible : la voix garde son rythme et ses pauses. Le moteur sélectionne huit compositions animées ; il ne génère pas librement des personnages 3D ni une mise en scène originale complète pour chaque sujet. Les modèles peuvent produire des erreurs et des variations de voix malgré la référence fixe.

## Stack incluse

| Étape | Outil local |
| --- | --- |
| Interface et orchestration | FastAPI, HTML/CSS/JavaScript sans compilation |
| Scénario structuré | Ollama + Qwen3 4B |
| Voix masculine fixe | Qwen3-TTS 1.7B Base + référence synthétique fournie |
| Contrôle du texte et alignement | faster-whisper Base |
| Animation et export | Pillow, NumPy, MoviePy, FFmpeg, NVENC ou libx264 |

Le téléchargement initial nécessite Internet ; la génération n'appelle aucun service de synthèse, API payante ou hébergeur. Ollama et les modèles doivent être présents localement. Aucune publication automatique sur les réseaux n'est incluse.

Les poids volumineux sont téléchargés depuis leurs sources officielles, avec révisions fixées dans [models.json](models.json). Le tag Ollama peut évoluer : son empreinte observée est indiquée dans le manifeste. Les coûts éventuels sont ceux du matériel et de l'électricité ; aucune clé API n'est nécessaire.

Les dépendances du studio sont contraintes par `requirements-lock.txt`, issu d'une installation Windows propre. Les principales versions de l'environnement voix sont fixées séparément ; ses dépendances transitives ne sont pas intégralement verrouillées.

## Organisation

- `studio/` : serveur, orchestration, synthèse et moteur d'animation.
- `assets/voice/` : référence masculine **synthétique**, texte et profil ; aucun enregistrement personnel.
- `docs/chartes/` : les deux chartes et règles d'apparition réutilisables.
- `examples/` : descriptions prêtes à soumettre et sources des épisodes précédents.
- `scripts/` : téléchargement des modèles et lancement d'un exemple via l'API locale.
- `.local/` : modèles téléchargés, préférences, historiques, médias et journaux, ignorés par Git.

Les sources historiques personnalisées dans `examples/sources/` documentent les mises en scène d'origine. Elles nécessitent leurs médias et alignements régénérés et ne sont pas le point d'entrée du studio portable. Voir [les exemples](examples/README.md).

Pour réutiliser des modèles déjà installés, définir `STUDIO_MODELS_DIR` vers le dossier contenant `Qwen3-TTS-1.7B-Base/` et `whisper-base/`. `STUDIO_VOICE_PYTHON` peut désigner un environnement Qwen existant. Voir [.env.example](.env.example) pour tous les réglages. Ce fichier n'est pas chargé automatiquement.

## Vérification

```powershell
.venv/Scripts/python.exe scripts/check.py
```

Le contrôle hors ligne vérifie l'intégrité du profil vocal, les 32 combinaisons de rendu (8 compositions × 2 chartes × 2 formats), la configuration et un export court CPU. Il ne télécharge pas les modèles et ne certifie pas la qualité d'une nouvelle narration. [État des validations](docs/VALIDATION.md).

Le serveur écoute exclusivement sur localhost. Ne pas l'exposer directement à Internet. Les fichiers de travail ne sont pas sauvegardés sur GitHub : sauvegarder séparément `.local/` si nécessaire.

## Composants externes

[ComfyUI](https://github.com/comfyanonymous/ComfyUI), [Wan2.2](https://github.com/Wan-Video/Wan2.2) et [MoneyPrinterTurbo](https://github.com/harry0703/MoneyPrinterTurbo) faisaient partie des expérimentations précédentes. Le studio actuel n'en dépend pas ; leurs sources et modèles ne sont pas recopiés. Voir [la stack optionnelle](docs/STACK-OPTIONNELLE.md).

Les logiciels, poids et polices gardent leurs licences propres : [notices](THIRD_PARTY_NOTICES.md). Dépôt privé ; aucune licence publique de redistribution n'est accordée pour le code spécifique à cette série.
