# Référence vocale partagée

Le dépôt fournit une référence masculine française synthétique :

- `Reference-Homme.wav` : signal de référence ;
- `Reference-Texte.txt` : transcription ;
- `Profil.json` : paramètres et SHA-256 de référence.

Cette voix a été créée avec Qwen3-TTS pour le projet. Elle ne contient pas les enregistrements personnels utilisés dans les expérimentations précédentes. Le mainteneur a choisi de partager cette référence avec le projet sous la [licence MIT](../../LICENSE), dans la mesure des droits qu’il détient sur ces éléments.

Vous pouvez réutiliser cette référence ; aucun timbre exclusif n’est promis. Le résultat peut varier selon les modèles et les réglages. Les modèles Qwen et leur code conservent leurs licences propres, indépendantes de celle du dépôt. Consulter [les notices](../../THIRD_PARTY_NOTICES.md).

Pour utiliser une autre référence, conserver les enregistrements privés hors des fichiers suivis par Git et adapter le profil, sa transcription et son empreinte. Le contrôle `scripts/check.py` vérifie la cohérence du profil fourni.
