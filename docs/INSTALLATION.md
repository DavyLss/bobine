# Installation détaillée

Windows 64 bits, Python 3.11. Exécuter depuis la racine du dépôt :

```powershell
py -3.11 -m venv .venv
py -3.11 -m venv .venv-voice
.venv/Scripts/python.exe -m pip install -r requirements.txt -c requirements-lock.txt
.venv-voice/Scripts/python.exe -m pip install torch==2.6.0 torchaudio==2.6.0 --index-url https://download.pytorch.org/whl/cpu
.venv-voice/Scripts/python.exe -m pip install -r requirements-voice.txt
.venv/Scripts/python.exe scripts/download_models.py
ollama pull qwen3:4b
.venv/Scripts/python.exe studio/server.py
```

Ollama doit être lancé. La génération utilise ses fichiers locaux et les poids téléchargés dans `.local/models`. Les deux environnements sont nécessaires : ne pas fusionner leurs dépendances. Ne pas versionner les environnements virtuels.

Pour un second studio sans toucher au premier : `$env:STUDIO_PORT = '8511'`. Les chemins peuvent être déplacés via les variables de `.env.example`, à définir avant le lancement. Choisir également des dossiers `STUDIO_DATA_DIR` et `STUDIO_JOBS_DIR` distincts si deux instances travaillent simultanément.

Le lanceur PowerShell ne termine jamais un service déjà actif. Pour voir les erreurs, lancer `python studio/server.py` au premier plan. Les journaux du lanceur sont dans `.local/`.

Après une mise à jour du code, `Redemarrer-Studio.ps1` peut relancer le studio. Il refuse d'arrêter un rendu/transfert actif et vérifie que le processus du port appartient à ce dépôt avant de l'arrêter. Les préférences, vidéos et reçus sont conservés. Une préparation distante déjà acceptée continue chez le fournisseur.

Le code de rendu prévoit les polices Segoe sous Windows et DejaVu sous Linux. Aucun installateur Linux/macOS complet n'est fourni et ces plateformes n'ont pas été validées. Une police personnalisée exige les variables `STUDIO_FONT` et `STUDIO_FONT_BOLD`.

Pour une migration : cloner le dépôt, installer, puis restaurer séparément les dossiers de modèles et de travail. L'historique existant de l'ancien poste n'est pas importé automatiquement. Les chemins relatifs du dépôt ne contiennent aucun chemin personnel du poste d'origine.

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

### Python introuvable depuis le raccourci

Un environnement créé depuis une application Windows empaquetée peut contenir un chemin Python virtualisé, accessible depuis cette application mais pas depuis le Bureau. L’installateur normalise désormais les chemins de chaque environnement avec `scripts/fix_venv_paths.py`, sans réinstaller les paquets ni modifier les modèles.

Pour corriger une installation existante, depuis le contexte où son Python fonctionne :

```powershell
.venv/Scripts/python.exe scripts/fix_venv_paths.py
```

Les erreurs de réouverture sont consignées dans `.local/tray-error.log`. Les erreurs de démarrage du serveur et de la fenêtre se trouvent dans `.local/server-error.log` et `.local/desktop-error.log`.
