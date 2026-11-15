# Sécurité

## Périmètre

La branche `main` reçoit les correctifs selon les disponibilités du mainteneur. Aucune maintenance de versions anciennes ni délai de correction n’est garanti.

Le studio est une application personnelle exécutée sur `127.0.0.1`. Il ne fournit pas d’authentification multi-utilisateur. Les contrôles d’origine et l’en-tête de requête locale ne remplacent pas une authentification. Ne pas le publier directement sur Internet ni le rendre accessible sur un réseau partagé sans protections adaptées.

## Signaler une vulnérabilité

Lorsque le signalement privé GitHub est activé, utiliser **Security → Report a vulnerability** :

https://github.com/DavyLss/bobine/security/advisories/new

Si ce formulaire est indisponible, ouvrir uniquement une issue intitulée « Demande de canal de signalement privé », sans détail technique sensible. Le mainteneur devra convenir d’un canal confidentiel avant de recevoir les détails. Ne jamais envoyer de clé ni de jeton dans une issue publique.

Inclure ensuite dans le canal privé : le commit concerné, le système utilisé, l’impact, les étapes minimales et des exemples avec de faux identifiants. Ne pas accéder aux comptes ou aux données d’autres personnes pour démontrer un problème.

## Données et secrets

- Les données de travail et accès sont conservés dans `.local/` par défaut, ou dans les dossiers configurés sur le poste, et sont ignorés par Git.
- Sous Windows, les secrets de publication utilisent DPAPI, lié au compte utilisateur. Les fichiers de configuration, médias et journaux ne sont pas tous chiffrés.
- Hors Windows, le stockage des secrets utilise des permissions de fichier restrictives mais n’est pas chiffré par ce mécanisme.
- L’API de réglages retourne des indicateurs de présence des secrets, pas leurs valeurs.
- Une sauvegarde du poste doit protéger les fichiers de travail et la configuration. Une sauvegarde DPAPI ne garantit pas leur réutilisation sur un autre compte Windows.
- Un secret publié doit être révoqué ou renouvelé auprès du fournisseur ; le supprimer du dernier commit ne suffit pas.

La génération et le kit de publication sont locaux après téléchargement des modèles. La diffusion facultative transmet des médias aux réseaux configurés et, pour Instagram/TikTok dans cette version, à Cloudinary. Les URL Cloudinary sont publiques jusqu’à la purge après confirmation de publication. Voir [PUBLICATION.md](docs/PUBLICATION.md).
