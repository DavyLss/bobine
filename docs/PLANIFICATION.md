# Publications en masse, imports et calendrier

Ouvrir **Publications** dans la navigation du studio (`/#publications`). Aucun média n’est envoyé aux réseaux pendant la sélection, l’import ou la saisie des textes.

## Sélection et import

Sélectionner jusqu’à 50 vidéos terminées du studio, ou importer plusieurs fichiers MP4, MOV, M4V, WebM ou MKV depuis le poste. Les imports sont traités un par un : 500 Mo et 10 minutes maximum par fichier, dimensions d’entrée limitées à 8192 pixels par côté.

Chaque import est contrôlé et converti localement en MP4 H.264/AAC, 30 images/s, dimensions limitées à 1920 pixels par côté. Le studio extrait un poster et supprime les métadonnées globales et chapitres de la copie normalisée. Le fichier original sur le poste reste inchangé. Prévoir de la place sur le disque ; la conversion peut prendre plusieurs minutes. Les limites du réseau et de l’offre Cloudinary restent applicables après conversion.

Les vidéos importées apparaissent dans la bibliothèque et peuvent être téléchargées. Elles n’ont pas de scénario ni de sous-titres du studio. Leur titre, description, trois à cinq hashtags et texte de miniature sont saisis manuellement dans le formulaire de diffusion. Le studio ne déduit pas le contenu d’une vidéo externe à partir de son nom de fichier.

## Publication en lot

1. Choisir les vidéos dans l’ordre de diffusion.
2. Cocher les réseaux communs : YouTube, Instagram, TikTok via Buffer.
3. Choisir « Planifier » ou « Dès que possible, en séquence ».
4. Pour planifier, définir la première date et un intervalle en minutes, puis cliquer sur **Appliquer les dates**. Chaque date reste modifiable individuellement.
5. Vérifier les textes de chaque vidéo, puis **Enregistrer les publications**.

Les métadonnées des vidéos du studio sont reprises lorsqu’elles existent ; elles restent éditables avant validation. Les miniatures sont générées localement avec Pillow à partir du poster et du texte confirmé. Le format standard est accepté pour YouTube seul ; Instagram/TikTok nécessitent une vidéo verticale dans cette version du studio.

La validation vérifie les vidéos du lot avant d’enregistrer les plans. Elle refuse une vidéo déjà planifiée, en préparation ou en cours d’envoi, ainsi que les réseaux pour lesquels un reçu ou une tentative de publication existe déjà. La liste signale les réseaux déjà utilisés. Après validation, les textes sont réservés : modifier ou annuler le plan avant d’éditer le kit par ailleurs.

## Horaires et fonctionnement local

Les dates sont affichées et saisies dans le fuseau horaire du navigateur, indiqué dans l’interface. Elles sont enregistrées sous forme d’instants UTC pour conserver la même échéance après un changement de fuseau ou un redémarrage.

**Le PC et le serveur du studio doivent rester allumés et disposer d’une connexion Internet.** Le navigateur peut être fermé. La planification est exécutée par le studio, pas transférée à l’avance aux services distants. À l’heure prévue, la vidéo rejoint la file d’envoi commune ; les envois se font un par un. Le traitement par les réseaux et une file déjà occupée peuvent retarder la publication effective.

Le planificateur vérifie les échéances environ toutes les deux secondes. Pour TikTok, il demande un envoi immédiat à Buffer à l’heure prévue, au lieu de dépendre des créneaux de la file Buffer. Cela reste soumis aux conditions du compte et du réseau.

Une échéance dépassée de plus de cinq minutes n’est pas envoyée automatiquement. Après redémarrage, tout plan encore en attente dont la date est passée demande également une reprogrammation. Le statut devient **Échéance dépassée** : utiliser **Déplacer** pour autoriser une nouvelle date.

Désactiver les envois dans **Connexions** empêche le déclenchement des nouveaux plans. La pause de production concerne la génération des vidéos ; elle est distincte de la diffusion planifiée.

## Calendrier et suivi

Le calendrier mensuel affiche les publications enregistrées par ce module. Choisir un jour filtre l’agenda ; **Tout le mois** rétablit la liste du mois. Les publications historiques réalisées avant ce module ne sont pas reconstituées artificiellement.

- **Planifiée** : en attente de l’heure prévue.
- **Envoi engagé** : transmise à la file de publication ; attendre les reçus.
- **Publiée** : tous les réseaux choisis ont confirmé.
- **À contrôler** : un échec, une interruption ou une ambiguïté nécessite de consulter les reçus.
- **Bloquée** : impossible de démarrer l’envoi ; lire le message, annuler le plan puis le recréer après correction si aucune tentative distante n’existe.
- **Annulée** : plan retiré avant son envoi ; fichiers conservés.

Les plans en attente peuvent être déplacés ou annulés dans l’agenda. Dès qu’un envoi est engagé, l’annulation locale est refusée : vérifier le fournisseur et les reçus, sans renvoi aveugle. Un studio arrêté pendant la transmission demande un contrôle manuel après redémarrage.

Les connexions et hébergements nécessaires sont décrits dans [PUBLICATION.md](PUBLICATION.md). La purge Cloudinary attend toujours la confirmation de publication de tous les réseaux concernés.

## Vérification hors ligne

`python scripts/check_planner.py` vérifie un véritable petit import MP4, les limites et le nettoyage des imports refusés, le déclenchement à échéance, la prévention des doublons, les réservations, le déplacement, l’annulation et le redémarrage. `node scripts/check_planner_ui.cjs` vérifie la sélection multiple, l’espacement des dates, les actions du calendrier, les textes sûrs et l’import simulé. Les services de publication sont simulés ; aucun envoi réel n’est effectué pendant les tests.
