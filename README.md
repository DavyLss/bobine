<p align="center"><img src="studio/static/brand/logo-transparent.png" width="180" height="180" alt="Logo Bobine"></p>

# Bobine

**Vos idées prennent vie, image après image.**

[![Licence MIT](https://img.shields.io/badge/licence-MIT-green)](LICENSE) [![Vérifications hors ligne](https://github.com/DavyLss/bobine/actions/workflows/check.yml/badge.svg)](https://github.com/DavyLss/bobine/actions/workflows/check.yml)

Studio vidéo pédagogique en français, exécuté sur le poste : scénario IA, voix masculine, féminine ou dialogue Duo, sous-titres synchronisés et animations. Interface simple : titre, description, charte, durée moyenne, format, puis génération avec suivi et historique.

Quatre directions réutilisables : **Atelier sombre**, **Éditorial clair**, **Carnet animé** et **Papier découpé**. La dernière charte utilisée est mémorisée. Formats **Reel 1080 × 1920** et **Standard 1920 × 1080**, 30 images/s, MP4 H.264/AAC.

## Directions visuelles

| Direction | Univers | Valeur CSV | Charte |
| --- | --- | --- | --- |
| Atelier sombre | Scène sombre, objets illustrés, sous-titres en capitales | `dark` | [Règles](docs/chartes/Atelier-Sombre/Charte-reutilisable.md) |
| Éditorial clair | Fond lumineux, cartes et apparitions animées | `light` | [Règles](docs/chartes/Clair/Charte-reutilisable.md) |
| Carnet animé | Papier et encre, titres éditoriaux, guide optique | `carnet` | [Règles](docs/chartes/CARNET-ANIME.md) |
| Papier découpé | Collage, bandeaux découpés, objets en mouvement et oiseau origami | `papier` | [Règles](docs/chartes/PAPIER-DECOUPE.md) |

Les quatre directions fonctionnent en Reel et standard, avec les voix homme, femme ou Duo. Le rendu reste local. Le mode Duo alterne les deux voix de référence sans afficher le nom des intervenants.

**Papier découpé : image extraite d'un export local**, avec sous-titres synchronisés et personnage original.

<p align="center"><img src="docs/screenshots/papier-rendu.jpg" width="300" alt="Rendu Papier découpé : titre sur bandeau jaune, panneaux crème et oiseau origami sur fond vert"></p>

## Aperçu du studio

**Choix des quatre directions**, capture du 21 novembre 2026 :

![Choix de Papier découpé dans La réalisation, avec les quatre directions et l'aperçu de charte](docs/screenshots/directions.jpg)

Les captures suivantes datent du 15 novembre 2026.

**Création en trois étapes** : sujet, réalisation et diffusion, avec moniteur de prévisualisation.

![Écran de création : étapes du formulaire, commandes de production et aperçu vidéo](docs/screenshots/creation.png)

<details>
<summary>Voir la bibliothèque et les commandes de production</summary>

**Bibliothèque** : miniatures des vidéos, paramètres et état de publication.

![Bibliothèque des vidéos générées avec miniatures et statuts](docs/screenshots/bibliotheque.png)

**File de production** : pause, reprise, suppression de l’attente et arrêt forcé. Les commandes sans tâche correspondante sont désactivées.

![File de production avec les commandes de pause, vidage de l’attente et arrêt forcé](docs/screenshots/production.png)

</details>

## Installation Windows

Prérequis : [Python 3.11 64 bits](https://www.python.org/downloads/), [Git](https://git-scm.com/downloads) et [Ollama](https://ollama.com/download). Lancer Ollama avant l'installation. Prévoir plusieurs gigaoctets de téléchargements et de stockage ; 16 Go de RAM minimum conseillé, 32 Go préférable. La voix fonctionne sur CPU et peut prendre plusieurs minutes par vidéo. Un GPU NVIDIA compatible accélère le rendu ; le CPU est utilisé automatiquement si NVENC est indisponible.

```powershell
git clone https://github.com/DavyLss/bobine.git
cd bobine
.\Installer.ps1
.\Lancer-Studio.ps1
```

Ouvrir **http://127.0.0.1:8510/**. Si PowerShell bloque les scripts, ne pas modifier sa politique sans comprendre la règle du poste : les commandes Python équivalentes sont dans [INSTALLATION.md](docs/INSTALLATION.md).

`Installer.ps1 -SkipModels` installe seulement les dépendances. `Installer.ps1 -Python 'C:/chemin/python.exe'` sélectionne explicitement un Python 3.11. Les deux environnements Python isolent les dépendances du studio et celles de Qwen.

## Utilisation

1. Donner un titre et une description précise du public, du sujet et de l'exemple souhaité.
2. Choisir une charte, la durée cible (15 à 180 secondes), puis Standard ou Reel.
3. Lancer et suivre scénario → voix → synchronisation → rendu → vérification.
4. Relire et écouter avant publication. Télécharger la vidéo, le scénario et les sous-titres depuis l'interface.

### Générer plusieurs vidéos en séquence

Choisir **Plusieurs vidéos** pour saisir jusqu'à 500 titres/descriptions, ajouter ou retirer des lignes et changer leur ordre. La charte, la durée moyenne, le format et la voix sont communs à tout le lot.

Choisir **Importer un CSV** pour charger un fichier UTF-8. Le fichier est vérifié automatiquement, puis à chaque changement de réglage commun ; **Vérifier le fichier** permet aussi de relancer ce contrôle. L’aperçu affiche les valeurs réellement utilisées et tout blocage est rappelé près du bouton final. Télécharger le modèle dans l'interface ou partir de [cet exemple](examples/lot-devops.csv).

Colonnes : `titre, description, charte, duree, format, voix` (les noms anglais `title, description, theme, duration, format, voice` sont aussi acceptés). Seuls titre et description sont obligatoires. Une cellule de réglage vide reprend la valeur commune ; une cellule remplie remplace cette valeur pour la ligne. Séparateurs acceptés : virgule, point-virgule et tabulation. Encadrer de guillemets les descriptions contenant le séparateur ou des retours à la ligne.

Valeurs : charte `dark`/`light`/`carnet`/`papier` (ou `sombre`/`clair`/`carnet animé`/`papier découpé`), durée entière de 15 à 180 secondes, format `reel`/`standard` (ou `9:16`/`16:9`), voix `Narrateur-Homme-01`, `Narratrice-Femme-01` ou `Duo-Homme-Femme` (alias CSV `homme` / `femme` / `duo`). Les deux profils synthétiques sont locaux et réutilisables. Les fichiers sont limités à 1 Mo et 500 vidéos ; toute erreur bloque le lot avant sa mise en file, sans génération partielle.

Le panneau **Suivi des lots** affiche les vidéos dans l'ordre, l'étape courante, la progression globale, les succès, échecs et annulations, puis les liens de téléchargement. Le suivi automatique peut être désactivé pour consulter une autre vidéo. Tous les lots partagent la même file FIFO et **une seule vidéo est calculée à la fois** (500 vidéos actives/en attente au maximum).

Un échec laisse les vidéos suivantes continuer. **Annuler les vidéos en attente** laisse celle en cours se terminer. **Relancer les échecs** crée un nouveau lot pour les seules vidéos échouées ou interrompues. Fermer la page ne coupe pas la génération tant que le serveur fonctionne. La barre de production permet de **mettre en pause après la vidéo en cours**, puis de reprendre plus tard. La pause et les vidéos en attente sont conservées après un redémarrage du studio. Seule une vidéo dont le rendu était en cours au moment de l’arrêt est marquée interrompue et doit être relancée ; aucun rendu ne reprend au milieu de son calcul.

Dans **File de production**, vous pouvez retirer une seule vidéo en attente ou **vider toute l’attente** sans arrêter celle en cours. **Forcer l’arrêt en cours** termine le processus de rendu et ses sous-processus, puis laisse la file en pause pour décider de la suite. Les fichiers locaux sont conservés, et les vidéos retirées restent visibles comme annulées dans l’historique. La pause concerne la génération ; les publications déjà engagées conservent leur suivi.

La durée est une cible : la voix garde son rythme et ses pauses. Le moteur sélectionne huit compositions animées ; il ne génère pas librement des personnages 3D ni une mise en scène originale complète pour chaque sujet. Les modèles peuvent produire des erreurs et des variations de voix malgré la référence fixe.

## Publications en masse et calendrier

L’onglet **Publications** permet de choisir jusqu’à 50 vidéos terminées ou d’importer plusieurs fichiers externes (MP4, MOV, M4V, WebM, MKV ; 500 Mo et 10 minutes maximum par fichier). Les imports sont convertis localement, puis leurs textes restent à compléter avant diffusion.

Choisir les réseaux communs, préparer les textes par vidéo et publier en séquence ou répartir les dates à partir d’une première échéance et d’un intervalle. Le calendrier mensuel permet de consulter les statuts, déplacer une date et annuler un plan encore en attente.

**Planification locale : le PC et le studio doivent rester allumés.** Une échéance manquée demande une reprogrammation ; les vidéos ne sont pas renvoyées automatiquement en cas de résultat incertain. Voir [le guide de planification](docs/PLANIFICATION.md).

<details>
<summary>Voir l’espace Publications et son calendrier</summary>

![Publications en masse, import de vidéos, réglages de diffusion et calendrier mensuel](docs/screenshots/publications.png)

</details>

## Stack incluse

| Étape | Outil local |
| --- | --- |
| Interface et orchestration | FastAPI, HTML/CSS/JavaScript sans compilation |
| Scénario structuré | Ollama + Qwen3 4B |
| Voix masculine fixe | Qwen3-TTS 1.7B Base + référence synthétique fournie |
| Contrôle du texte et alignement | faster-whisper Base |
| Animation et export | Pillow, NumPy, MoviePy, FFmpeg, NVENC ou libx264 |

Le téléchargement initial nécessite Internet ; la génération de la vidéo et du kit de publication reste locale. Ollama et les modèles doivent être présents sur le poste. La diffusion est facultative : elle envoie les fichiers aux réseaux configurés et, pour Instagram/TikTok, à l'hébergement média Cloudinary.

## Publication automatique des Reels

Le studio peut publier sur **YouTube via son API native**, **Instagram via son API native** et **TikTok via Buffer**. Les connexions se règlent dans l'interface, avec une notice et les liens de création des accès pour chaque API. Voir [PUBLICATION.md](docs/PUBLICATION.md).

Pour chaque nouvelle vidéo, Ollama prépare localement le titre, la description et les hashtags. Pillow génère une miniature verticale et une miniature YouTube selon la charte ; elles restent éditables et téléchargeables. Le JPG est envoyé directement à YouTube et fourni comme couverture à Instagram. Buffer ne transmettant pas de miniature JPEG, une copie TikTok peut inclure la couverture générée pendant les 0,6 premières secondes, sans changer l'export original.

Les envois sont désactivés par défaut. Après configuration, cocher les réseaux et **Publier automatiquement les Reels terminés** pour une vidéo ou un lot. Les vidéos existantes disposent d'un bouton de préparation du kit et d'un envoi manuel. Le suivi conserve un reçu par réseau et distingue réception, traitement et publication confirmée. Les résultats incertains ne sont pas renvoyés aveuglément.

Les API YouTube et Instagram ne nécessitent pas d'abonnement de publication ; leurs quotas, comptes et autorisations restent applicables. Buffer et Cloudinary ont leurs propres offres et limites. Aucun achat n'est déclenché par le studio. Les accès de l'utilisateur sont indispensables pour une publication réelle ; les tests automatisés utilisent des services simulés.

Les poids volumineux sont téléchargés depuis leurs sources officielles, avec révisions fixées dans [models.json](models.json). Le tag Ollama peut évoluer : son empreinte observée est indiquée dans le manifeste. Les coûts éventuels de génération sont ceux du matériel et de l’électricité ; aucune clé API de publication n’est nécessaire pour générer localement.

Les dépendances du studio sont contraintes par `requirements-lock.txt`, issu d'une installation Windows propre. Les principales versions de l'environnement voix sont fixées séparément ; ses dépendances transitives ne sont pas intégralement verrouillées.

## Organisation

- `studio/` : serveur, orchestration, synthèse et moteur d'animation.
- `assets/voice/` : référence masculine **synthétique**, texte et profil ; aucun enregistrement personnel.
- `docs/chartes/` : les chartes et règles d'apparition réutilisables.
- `examples/` : descriptions prêtes à soumettre et sources des épisodes précédents.
- `scripts/` : téléchargement des modèles et lancement d'un exemple via l'API locale.
- `.local/` : modèles téléchargés, préférences, historiques, médias et journaux, ignorés par Git.

Les sources historiques personnalisées dans `examples/sources/` documentent les mises en scène d'origine. Elles nécessitent leurs médias et alignements régénérés et ne sont pas le point d'entrée du studio portable. Voir [les exemples](examples/README.md).

Pour réutiliser des modèles déjà installés, définir `STUDIO_MODELS_DIR` vers le dossier contenant `Qwen3-TTS-1.7B-Base/` et `whisper-base/`. `STUDIO_VOICE_PYTHON` peut désigner un environnement Qwen existant. Voir [.env.example](.env.example) pour tous les réglages. Ce fichier n'est pas chargé automatiquement.

Les mêmes réglages peuvent être conservés dans `.local/config.json` (clés `STUDIO_PORT`, `STUDIO_MODELS_DIR`, etc.). Les variables d'environnement ont priorité. Ce fichier propre au poste est ignoré par Git ; il ne migre pas les chemins d'une machine vers une autre.

## Vérification

```powershell
.venv/Scripts/python.exe scripts/check.py
.venv/Scripts/python.exe -m pip install -r requirements-test.txt -c requirements-lock.txt
.venv/Scripts/python.exe scripts/check_api.py
.venv/Scripts/python.exe scripts/check_batches.py
.venv/Scripts/python.exe scripts/check_social.py
```

Le contrôle hors ligne vérifie l'intégrité du profil vocal, les 32 combinaisons de rendu (8 compositions × 2 chartes × 2 formats), la configuration et un export court CPU. Il ne télécharge pas les modèles et ne certifie pas la qualité d'une nouvelle narration. [État des validations](docs/VALIDATION.md).

Les tests de lots utilisent de vrais sous-processus de simulation pour vérifier l'ordre et la reprise après échec, sans lancer les modèles IA. Les tests DOM de l'interface sont facultatifs pour le développement : Node.js 24.15+ (branche 24), `npm ci`, puis `npm test`. Node.js n'est pas requis pour utiliser le studio.

Le serveur écoute exclusivement sur localhost. Ne pas l'exposer directement à Internet. Les fichiers de travail ne sont pas sauvegardés sur GitHub : sauvegarder séparément `.local/` si nécessaire.

## Composants externes

[ComfyUI](https://github.com/comfyanonymous/ComfyUI), [Wan2.2](https://github.com/Wan-Video/Wan2.2) et [MoneyPrinterTurbo](https://github.com/harry0703/MoneyPrinterTurbo) faisaient partie des expérimentations précédentes. Le studio actuel n'en dépend pas ; leurs sources et modèles ne sont pas recopiés. Voir [la stack optionnelle](docs/STACK-OPTIONNELLE.md).

Les logiciels, poids et polices gardent leurs licences propres : [notices](THIRD_PARTY_NOTICES.md). Le code spécifique au projet, les chartes, les exemples et la référence vocale synthétique fournie sont partagés sous [licence MIT](LICENSE), dans la mesure des droits du mainteneur. Les bibliothèques, modèles, codecs et autres composants tiers conservent leurs licences propres. La voix de référence est réutilisable et n’est pas exclusive. Voir [sa notice](assets/voice/README.md).

## Contribuer et signaler un problème

Consulter [CONTRIBUTING.md](CONTRIBUTING.md) pour l’environnement de développement et les tests, [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) pour les échanges et [SECURITY.md](SECURITY.md) pour les signalements confidentiels. Le projet est fourni sans garantie ni support contractuel.

## Application Windows dédiée

L’installation crée un raccourci **Bobine** sur le Bureau. Bobine utilise une fenêtre native avec **Microsoft WebView2**, via pywebview : aucun navigateur Edge, Chrome ou Brave n’est requis pour afficher l’application. Le moteur WebView2 est imposé, sans repli silencieux vers un autre moteur. Les données de navigation sont isolées dans `.local/webview2-profile/`, ignoré par Git, et ne reprennent pas les extensions ni le profil du navigateur personnel.

Le [runtime WebView2 Evergreen](https://developer.microsoft.com/microsoft-edge/webview2/) doit être installé. Il est vérifié par l’installateur ; s’il manque, un message indique le lien officiel pour l’installer. Evergreen reçoit ses mises à jour de Microsoft : le moteur est commun, mais le numéro de version peut varier selon le déploiement des mises à jour Windows. Le runtime conserve ses conditions Microsoft, distinctes de la licence MIT de Bobine.

Pour mettre à niveau une installation existante, sans réinstaller les modèles :

```powershell
.\Installer-Fenetre.ps1
.\Creer-Raccourci.ps1
.\Lancer-Studio.ps1
```

Bobine reste dans la **zone de notification Windows** après fermeture de sa fenêtre (éventuellement sous la flèche des icônes masquées). Un double-clic ou **Ouvrir Bobine** réaffiche l’application. **Quitter Bobine** arrête son serveur et sa fenêtre dédiée ; une confirmation est demandée si une génération ou un transfert est actif. Les publications déjà acceptées à distance peuvent continuer. Les futures échéances ne seront pas exécutées tant que Bobine reste arrêté. Un seul gestionnaire de notification est lancé par dossier et port.

L’option `Lancer-Studio.ps1 -Navigateur` reste disponible pour ouvrir volontairement l’interface dans le navigateur habituel, sans gestionnaire de notification. Les liens externes (documentation, autorisation Google) peuvent aussi ouvrir ce navigateur ; l’interface Bobine reste dans WebView2. Les imports et téléchargements sont autorisés dans la fenêtre intégrée.

Les anciens réglages `STUDIO_BROWSER_PATH` et `-BrowserPath` ne sont plus utilisés. Si le dossier du projet est déplacé, relancer `Creer-Raccourci.ps1` pour actualiser le raccourci. Fermer la fenêtre laisse les traitements actifs ; utiliser **Quitter Bobine** pour les arrêter complètement.

<details>
<summary>Voir la fenêtre Bobine intégrée sous Windows</summary>

![Fenêtre Bobine indépendante avec le moteur WebView2](docs/screenshots/fenetre-bobine.png)

</details>

## Suivi global et notifications

La barre **Activité**, en bas de chaque page, conserve le suivi pendant la navigation : vidéo en cours, étape et pourcentage, attente de production, diffusions et planifications. Un clic ouvre le détail et les 30 dernières notifications de la session. Cliquer sur une tâche retrouve la vidéo ou son calendrier.

Les fins et échecs de génération, confirmations et problèmes de publication, ainsi que les échéances dépassées sont signalés dans l’application. Un envoi accepté ou placé dans une file distante reste distinct d’une publication confirmée par le réseau. Les notifications ne déclenchent aucun nouvel envoi. Ces notifications concernent l’interface ouverte, pas les notifications système Windows.

<details>
<summary>Voir le suivi global dans Bobine</summary>

![Barre persistante et centre d’activité de Bobine](docs/screenshots/activite.png)

</details>

La publication après génération est facultative : aucun compte ni réseau n’est nécessaire pour produire une vidéo. Si les options d’envoi sont incomplètes, la production continue sans publication automatique ; le motif reste visible dans le suivi de publication.

Le scénario passe par une relecture éditoriale locale avant la voix : accroche concrète, exemple suivi, progression des idées, nuances et conclusion utile. Les amorces répétées, les passages presque identiques et la répétition excessive du mot « équipe » déclenchent une réécriture ciblée. Trois essais maximum : un scénario encore répétitif est arrêté avant la synthèse vocale. Ces contrôles ne remplacent pas une vérification humaine du fond. Les vidéos déjà exportées restent inchangées.

Le mode **Duo · animateur et animatrice**, dans le choix de narration, produit un échange à deux voix locales fixes. Une réplique par plan, en alternance homme/femme : questions, réponses et nuances suivent un même exemple. La durée choisie concerne la conversation entière. Les noms des intervenants ne sont ni affichés dans la vidéo ni ajoutés aux sous-titres SRT ; ils ne sont pas prononcés. Les reprises de synthèse conservent la voix affectée à chaque réplique. Ce mode est disponible pour une vidéo, les réglages communs d’un lot et la colonne CSV `voix=duo`. Exemple : [lot-duo.csv](examples/lot-duo.csv).

La direction **Carnet animé** ajoute un univers papier et encre : grille de points, titres à empattements, annotations monospace, panneaux à ombre franche et guide optique dessiné pour Bobine. Elle fonctionne dans les deux formats et avec toutes les voix, dont le Duo. Sélectionner `carnet` dans le CSV ; aucune ressource Instagram n’est téléchargée ou utilisée dans les exports. [Charte et règles réutilisables](docs/chartes/CARNET-ANIME.md).

La direction **Papier découpé** transforme les explications en théâtre de collage : bandeaux découpés, panneaux qui se posent en rotation, messages en déplacement et oiseau origami original. Les sous-titres suivent la voix sur des papiers séparés. Disponible en Reel et standard, avec les voix homme, femme et Duo. CSV : `papier` ou `papier découpé`. [Charte réutilisable](docs/chartes/PAPIER-DECOUPE.md).
