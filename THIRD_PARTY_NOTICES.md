# Provenance et licences des composants tiers

La [licence MIT du dépôt](LICENSE) couvre les contributions spécifiques au projet dans la mesure des droits de leurs auteurs. Elle ne remplace pas les licences des dépendances, modèles, codecs ou polices.

## Bibliothèques principales

Les paquets sont installés depuis leurs distributions officielles et ne sont pas recopiés dans le dépôt. Les pages PyPI ci-dessous documentent les versions déclarées ; conserver les textes de licence et notices livrés avec les paquets et leurs composants lors d’une redistribution.

| Composant | Version déclarée | Licence déclarée / source |
| --- | --- | --- |
| FastAPI | 0.136.3 | [MIT](https://pypi.org/project/fastapi/0.136.3/) |
| Uvicorn | 0.32.1 | [BSD-3-Clause](https://pypi.org/project/uvicorn/0.32.1/) |
| Requests | 2.33.1 | [Apache-2.0](https://pypi.org/project/requests/2.33.1/) |
| MoviePy | 2.2.1 | [MIT](https://pypi.org/project/moviepy/2.2.1/) |
| Pillow | 11.3.0 | [MIT-CMU](https://pypi.org/project/Pillow/11.3.0/) |
| NumPy (studio) | 2.4.6 | [BSD-3-Clause et licences des composants embarqués](https://pypi.org/project/numpy/2.4.6/) |
| SoundFile | 0.14.0 | [BSD-3-Clause](https://pypi.org/project/soundfile/0.14.0/) ; libsndfile conserve sa licence propre |
| faster-whisper | 1.1.0 | [MIT](https://pypi.org/project/faster-whisper/1.1.0/) |
| imageio-ffmpeg (wrapper Python) | 0.6.0 | [BSD-2-Clause](https://pypi.org/project/imageio-ffmpeg/0.6.0/) ; distincte de la licence du binaire FFmpeg |
| huggingface-hub | 0.36.0 | [Apache-2.0](https://pypi.org/project/huggingface-hub/0.36.0/) |
| qwen-tts | 0.1.1 | [Apache-2.0](https://pypi.org/project/qwen-tts/0.1.1/) |
| Transformers | 4.57.3 | [Apache-2.0](https://pypi.org/project/transformers/4.57.3/) |
| PyTorch | 2.6.0 | [BSD-3-Clause et notices embarquées](https://pypi.org/project/torch/2.6.0/) |
| torchaudio | 2.6.0 | [BSD, texte de licence du projet](https://github.com/pytorch/audio/blob/v2.6.0/LICENSE) |
| jsdom (tests uniquement) | 31.0.1 | [MIT](https://github.com/jsdom/jsdom/blob/31.0.1/LICENSE.txt) |

Les environnements studio et voix sont séparés. Les versions et dépendances supplémentaires sont décrites dans `requirements*.txt` et `package-lock.json`. Cette table recense les composants principaux, pas un inventaire exhaustif de toutes les dépendances transitives ou des bibliothèques embarquées dans les wheels. Les textes et fichiers NOTICE distribués avec chaque paquet restent la référence pour ces composants.

## Modèles et moteurs locaux

- **Qwen3-TTS** : code [Apache-2.0](https://github.com/QwenLM/Qwen3-TTS/blob/main/LICENSE) ; modèle [Qwen/Qwen3-TTS-12Hz-1.7B-Base](https://huggingface.co/Qwen/Qwen3-TTS-12Hz-1.7B-Base), fiche déclarant Apache-2.0. La révision téléchargée est fixée dans `models.json`.
- **Qwen3 4B** : modèle [Apache-2.0](https://huggingface.co/Qwen/Qwen3-4B), exécuté via [Ollama](https://github.com/ollama/ollama). Le manifeste conserve une empreinte observée ; un tag Ollama peut évoluer.
- **Whisper Base converti** : [Systran/faster-whisper-base](https://huggingface.co/Systran/faster-whisper-base), fiche déclarant MIT ; modèle téléchargé à la révision du manifeste, issu de [Whisper](https://github.com/openai/whisper).

Les poids ne sont pas versionnés dans ce dépôt. Le téléchargement ne supprime pas les obligations attachées aux licences applicables aux poids et à leurs outils.

## FFmpeg, codecs et binaires

Le studio exécute FFmpeg via ses dépendances. FFmpeg est sous LGPL-2.1-or-later ou GPL selon les composants activés ; certains éléments peuvent rendre un binaire non redistribuable. Le wrapper Python ne détermine pas la licence du binaire.

La redistribution d’un exécutable ou d’une archive contenant FFmpeg, libx264, libsndfile, les wheels et leurs composants nécessite de vérifier la configuration réelle, les licences, les notices et les obligations de fourniture du code source correspondantes. Les éventuelles questions de brevets sur les codecs sont distinctes des licences du code. Voir [les informations officielles FFmpeg](https://ffmpeg.org/legal.html).

Le dépôt actuel distribue le code et les instructions d’installation, pas une copie des environnements installés ni un installateur autonome contenant ces binaires.

## Voix et ressources graphiques

`assets/voice/Reference-Homme.wav` est la référence masculine synthétique créée pour cette série avec Qwen3-TTS. Elle ne contient pas l’enregistrement personnel fourni dans les expérimentations initiales. Le mainteneur a choisi de la partager sous MIT dans la mesure de ses droits. Son SHA-256 est enregistré dans le profil et vérifié par le script de contrôle. Voir [la notice vocale](assets/voice/README.md). Aucun timbre exclusif ni identité parfaitement constante n’est garanti.

Les polices système (Segoe UI, DejaVu ou polices configurées) ne sont pas redistribuées. Leur présence sur un poste n’autorise pas nécessairement leur inclusion dans un futur installateur.

Les illustrations et animations spécifiques sont incluses dans le code du projet. Les liens Instagram/YouTube présents dans les chartes désignent des inspirations ; aucun extrait vidéo, musique ni personnage provenant de ces références n’est incorporé au dépôt. Le lien d’une référence ne confère pas de droit sur son contenu.

## Services de publication facultatifs

YouTube, Instagram, Buffer et Cloudinary sont des services externes, non fournis sous la licence du dépôt. Leurs conditions, comptes, autorisations, quotas et tarifs s’appliquent séparément. Les clés et jetons propres à chaque utilisateur ne sont pas fournis avec le projet. Voir [PUBLICATION.md](docs/PUBLICATION.md).

## Expérimentations antérieures

MoneyPrinterTurbo, ComfyUI et Wan2.2 sont cités dans la documentation de la stack optionnelle. Le studio actuel n’en dépend pas et leurs sources et modèles ne sont pas redistribués ici. Leur ajout ultérieur exige une vérification distincte de leurs licences.

## Fenêtre Windows intégrée

La fenêtre utilise [pywebview 6.2.1](https://github.com/r0x0r/pywebview) (BSD-3-Clause), avec les dépendances épinglées dans `requirements-desktop.txt`. Les licences livrées avec pythonnet, clr_loader, proxy_tools et Bottle restent applicables. Le [runtime Microsoft WebView2 Evergreen](https://developer.microsoft.com/microsoft-edge/webview2/) est installé séparément et conserve ses conditions Microsoft ; il n’est pas redistribué dans ce dépôt.
