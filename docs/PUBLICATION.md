# Publication des Reels : YouTube direct, Instagram direct, TikTok via Buffer

Le studio crée **sur le poste** un titre, une description et 3 à 5 hashtags avec Ollama, puis deux miniatures JPEG avec Pillow dans la charte choisie. Il ne sollicite aucun générateur de texte ou d'image cloud. La diffusion transmet ensuite les médias et leurs textes aux services choisis.

## Où régler les connexions

Dans l'interface, ouvrir **Connexions de publication**, en bas de page. Chaque service possède sa notice et ses liens. Enregistrer les accès avant de tester. Les champs secrets laissés vides conservent les valeurs précédentes ; les clés ne sont jamais renvoyées par l'API du studio.

Sur Windows, les secrets persistés sont protégés par DPAPI pour l'utilisateur Windows courant. Ils ne sont pas portables vers un autre compte/machine. Sous Linux, le fichier a des permissions 0600 mais n'est pas chiffré. `.local/`, les données, les reçus et les médias ne doivent pas être ajoutés à Git.

Le bouton **Autoriser les envois vers les réseaux** active les connecteurs. Il est désactivé par défaut. Il ne publie pas les anciennes vidéos. Pour chaque génération ou lot, cocher **Publier automatiquement les Reels terminés** et les réseaux souhaités. Pour une vidéo existante, sélectionner sa carte, générer son kit, puis utiliser **Envoyer aux réseaux cochés**.

## YouTube : API native, sans Buffer et sans hébergement public intermédiaire

1. Créer un projet : https://console.cloud.google.com/
2. Activer YouTube Data API v3 : https://console.cloud.google.com/apis/library/youtube.googleapis.com
3. Configurer le consentement OAuth et ajouter son compte Google aux utilisateurs de test si le projet est en mode test.
4. Dans https://console.cloud.google.com/apis/credentials, créer un client OAuth 2.0 **Application Web**.
5. Ajouter l'URL de redirection affichée dans le studio. Exemple sur le poste de développement : `http://127.0.0.1:8511/api/social/youtube/callback`. Le port doit correspondre au studio réellement lancé ; `localhost` et `127.0.0.1` ne sont pas interchangeables dans une URL OAuth enregistrée.
6. Copier le Client ID et le secret, ou importer le JSON OAuth local. Enregistrer puis cliquer **Connecter avec Google**. Autoriser le compte propriétaire de la chaîne.
7. Tester la connexion et vérifier le nom de la chaîne. Choisir la visibilité (publique, non répertoriée ou privée) et l'audience enfants selon le contenu.

Scopes : `youtube.upload` et `youtube.readonly`. Une simple clé API Google ne permet pas de téléverser au nom d'un utilisateur : OAuth est nécessaire. Le refresh token permet de renouveler l'accès ; des autorisations en mode test peuvent expirer et imposer une reconnexion.

L'envoi utilise le protocole reprenable Google. La session est enregistrée localement ; après interruption, une reprise interroge la même session avant de transférer des octets. Le JPG YouTube est envoyé via `thumbnails.set`. Les droits du compte et les restrictions de miniatures des Shorts peuvent empêcher son application : le refus est signalé sans republier la vidéo. La classification comme Short et la présentation finale restent gérées par YouTube.

Pas d'abonnement de publication requis pour l'API ; quotas applicables à l'application et à la chaîne. Consulter les quotas du projet plutôt que supposer un nombre illimité d'envois.

- Envoi : https://developers.google.com/youtube/data/reference/rest/v3/videos/insert
- Protocole reprenable : https://developers.google.com/youtube/data/guides/using_resumable_upload_protocol
- OAuth : https://developers.google.com/identity/protocols/oauth2/web-server
- Miniatures : https://developers.google.com/youtube/data/reference/rest/v3/thumbnails/set

## Instagram : API native avec Instagram Login, sans Buffer

1. Utiliser un compte Instagram professionnel **Business ou Creator**.
2. Créer une application : https://developers.facebook.com/apps/
3. Configurer **Instagram API avec Instagram Login**, puis ajouter son compte dans les rôles/testeurs et accepter l'invitation. Ne pas mélanger les jetons de ce parcours avec ceux de Facebook Login.
4. Accorder `instagram_business_basic` et `instagram_business_content_publish`.
5. Générer un Instagram User access token dans la configuration Instagram de l'application. Le copier dans le studio, enregistrer puis tester : l'ID professionnel sera récupéré.
6. Pour un jeton court, renseigner aussi l'**Instagram App Secret** et cliquer **Passer le jeton à 60 jours**. Le studio enregistre l'expiration et tente de renouveler les jetons longue durée suivis avant échéance lors d'un envoi. Un jeton expiré ou révoqué nécessite une nouvelle autorisation.
7. Renseigner Cloudinary pour la vidéo et la couverture JPEG publiques.

Cette intégration utilise `graph.instagram.com` et le parcours Instagram Login. Une Page Facebook n'est pas requise pour ce parcours. Un examen Meta et des autorisations supplémentaires peuvent être nécessaires pour servir des comptes tiers, selon les rôles et le niveau d'accès de l'application.

Le studio crée un conteneur `REELS`, attend `FINISHED`, puis le publie. La préparation Meta peut durer quelques minutes : le statut est recontrôlé en arrière-plan. Un résultat `PUBLISHED` ou un identifiant de média confirme la publication. La couverture générée est fournie via `cover_url`. Le transfert natif reprenable, documenté pour d'autres parcours Facebook Login for Business, n'est pas supposé disponible ici : cette version utilise le transfert par URL publique.

Pas d'abonnement de publication requis pour l'API Meta ; limites de publication, rôles et autorisations restent applicables.

- Publication : https://developers.facebook.com/documentation/instagram-platform/content-publishing
- Connexion et jetons : https://developers.facebook.com/documentation/instagram-platform/instagram-api-with-instagram-login/business-login

## TikTok : Buffer uniquement

1. Créer un compte Buffer : https://buffer.com/
2. Connecter TikTok avec publication automatique : https://publish.buffer.com/settings/channels
3. Créer une clé : https://publish.buffer.com/settings/api
4. Autoriser la lecture des comptes/organisations/canaux/posts et la création de posts.
5. Coller la clé, enregistrer, puis **Récupérer les canaux TikTok**. Choisir le canal voulu et enregistrer à nouveau.
6. Configurer les horaires de la file Buffer pour le mode **Ajouter à la file**. Le mode **Envoyer immédiatement** demande `shareNow`. Une file en pause et les limites du compte peuvent retarder ou refuser la publication.

Le studio utilise l'API GraphQL actuelle `https://api.buffer.com`, pas les anciens endpoints REST. La clé doit autoriser les opérations demandées ; la disponibilité et les coûts éventuels dépendent de l'offre Buffer.

Buffer n'accepte pas d'envoi de fichier direct : il récupère une URL publique stable. Il ne transmet pas une miniature vidéo JPEG personnalisée via son API. L'option **Ajouter une couverture de 0,6 s** crée donc localement `TikTok.mp4`, avec la miniature au début, puis demande ce moment via `thumbnailOffset`. L'original `Video.mp4` n'est pas modifié. Le rendu final dépend de TikTok.

**Transmis à Buffer** n'est pas **publié sur TikTok**. Le studio conserve l'ID du post Buffer et interroge son état jusqu'à `sent` ou à un échec.

- API : https://developers.buffer.com/guides/getting-started.html
- Vidéo : https://developers.buffer.com/examples/create-video-post.html
- Hébergement et restrictions : https://developers.buffer.com/guides/hosting-media.html

## Cloudinary : hébergement intermédiaire pour Instagram et TikTok

1. Créer un compte : https://cloudinary.com/
2. Ouvrir la console : https://console.cloudinary.com/
3. Dans l'environnement produit et les réglages **API Keys**, relever Cloud name, API key et API secret.
4. Les saisir dans le studio et tester. Le test utilise un ping authentifié, sans transférer de vidéo.

Le serveur signe les envois ; aucun preset public non signé n'est nécessaire. Les vidéos sont envoyées en morceaux pour limiter la mémoire et gérer les gros fichiers. Les URL HTTPS retournées doivent rester accessibles jusqu'à la publication. Les fichiers Cloudinary de chaque vidéo sont supprimés automatiquement dès que tous ses réseaux de destination confirment la publication. Une file Buffer en attente, un échec ou un statut incertain bloque la purge. Les fichiers locaux sont conservés. En cas d’échec de purge, le studio réessaie lors des contrôles automatiques. L'offre gratuite a des quotas ; aucun achat n'est déclenché par le studio.

- API d'envoi : https://cloudinary.com/documentation/upload_images
- Administration/ping : https://cloudinary.com/documentation/admin_api

## Suivi, reprise et limites

- Le suivi de **génération** reste distinct du suivi de **publication**, avec des reçus par réseau.
- Un réseau en échec ne supprime pas la vidéo locale et n'empêche pas les autres réseaux d'être traités.
- Le compte de destination de la publication automatique est mémorisé à la création de la tâche. S'il change entre-temps, l'envoi est bloqué pour éviter de publier sur un autre compte.
- Un identifiant de publication déjà reçu n'est pas renvoyé. Si une coupure survient après la demande mais avant sa confirmation, le résultat est marqué **incertain**. Ne pas créer une nouvelle tâche pour contourner cet état : contrôler d'abord le réseau/Buffer. YouTube peut reprendre sa session existante sans recréer une vidéo.
- Les textes et miniatures peuvent être modifiés avant envoi. Cela ne modifie pas rétroactivement un post déjà reçu par un réseau.
- Les jetons et comptes ne sont pas fournis avec le dépôt. Sans configuration de l'utilisateur, seuls la génération locale et les tests simulés sont disponibles.

## CSV

En plus des colonnes de vidéo, les champs facultatifs sont `publication_auto` (`oui`/`non`), `reseaux` (`youtube|instagram|tiktok`) et `mode_publication` (`queue`/`now`, pour TikTok). Les noms anglais `auto_publish`, `publish_platforms` et `publish_mode` sont acceptés. Une cellule vide conserve le réglage commun. La publication automatique exige le format Reel et au moins un réseau correctement configuré.
