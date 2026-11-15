# Provenance et licences

Les dépendances sont installées depuis leurs distributions officielles ; ce dépôt ne remplace pas leurs licences.

- Qwen3-TTS : https://github.com/QwenLM/Qwen3-TTS ; paquet qwen-tts 0.1.1 et modèle Qwen/Qwen3-TTS-12Hz-1.7B-Base. Consulter les licences du code et la fiche du modèle lors du téléchargement.
- Qwen3 4B : https://huggingface.co/Qwen/Qwen3-4B ; distribué localement par Ollama. https://ollama.com/library/qwen3
- faster-whisper : https://github.com/SYSTRAN/faster-whisper ; poids https://huggingface.co/Systran/faster-whisper-base
- FFmpeg : https://ffmpeg.org/legal.html ; le binaire livré par imageio-ffmpeg et ses codecs ont leurs conditions propres. Ne pas supposer que la licence Python couvre le binaire et tous les codecs.
- MoviePy, Pillow, NumPy, FastAPI, Uvicorn et autres bibliothèques conservent leurs notices dans les paquets installés.
- Les polices système ne sont pas redistribuées. Installer/utiliser une police autorisée sur le poste cible.

`assets/voice/Reference-Homme.wav` est la référence masculine synthétique créée pour cette série avec Qwen3-TTS. Elle ne contient pas l'enregistrement personnel fourni initialement par l'utilisateur. Son SHA-256 est enregistré dans le profil et vérifié par le script de contrôle. Réutiliser cette référence réduit les changements de timbre, sans garantie d'exclusivité ou d'identité parfaitement constante.

Les liens de références visuelles dans les chartes sont des inspirations. Aucun extrait Instagram/YouTube, musique ou personnage de ces créateurs n'est incorporé au dépôt.
