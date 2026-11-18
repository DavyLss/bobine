# Référence vocale partagée

Le dépôt fournit deux références françaises synthétiques, masculine et féminine :

- `Reference-Homme.wav` : signal de référence ;
- `Reference-Femme.wav` et `Profil-Femme.json` : référence féminine et transcription/paramètres ;
- `Reference-Texte.txt` : transcription ;
- `Profil.json` : paramètres et SHA-256 de référence masculine ;
- `Reference-Femme.wav` et `Profil-Femme.json` : référence féminine et son profil.

Ces voix ont été créées avec Qwen3-TTS pour le projet. Elles ne contiennent pas les enregistrements personnels utilisés dans les expérimentations précédentes. Le mainteneur a choisi de partager cette référence avec le projet sous la [licence MIT](../../LICENSE), dans la mesure des droits qu’il détient sur ces éléments.

Vous pouvez réutiliser cette référence ; aucun timbre exclusif n’est promis. Le résultat peut varier selon les modèles et les réglages. Les modèles Qwen et leur code conservent leurs licences propres, indépendantes de celle du dépôt. Consulter [les notices](../../THIRD_PARTY_NOTICES.md).

Pour utiliser une autre référence, conserver les enregistrements privés hors des fichiers suivis par Git et adapter le profil, sa transcription et son empreinte. Le contrôle `scripts/check.py` vérifie la cohérence du profil fourni.

La voix féminine se sélectionne avec `Narratrice-Femme-01`. Sa référence est créée une fois avec le modèle VoiceDesign, puis le modèle Base réutilise ce même timbre pour chaque phrase. Le script `scripts/create_female_voice.py` documente sa création locale ; il nécessite le modèle VoiceDesign déjà téléchargé et l’environnement Python vocal.
