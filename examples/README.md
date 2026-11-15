# Exemples

`DevOps-Cest-Quoi.json` et `DevOps-Trois-Voies.json` sont des requêtes prêtes à envoyer au studio lancé :

```powershell
.venv/Scripts/python.exe scripts/submit_example.py examples/DevOps-Cest-Quoi.json
```

La requête lance une nouvelle génération complète et apparaît dans l'interface ; ce n'est pas une copie du montage historique. Le texte fourni sert de brief au modèle local.

`sources/` préserve les scénarios, directions et moteurs personnalisés des quatre épisodes précédents (Golden Circle clair/sombre et les deux DevOps). Ces sources historiques attendent des médias `Narration.wav`, `Sous-titres.srt`, `Mots-alignes.json` et parfois `Chronologie.json` dans leur propre dossier. Ils sont volontairement exclus du dépôt. Certaines sources historiques conservent les hypothèses d'origine (Windows, NVENC, format vertical). Utiliser `studio/` pour les installations portables et les nouveaux sujets ; adapter les sources historiques pour reconstruire exactement un ancien montage.
