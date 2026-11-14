# 13. Gérer son compte, son équipe et ses clés

> Ce chapitre apprend à se repérer dans les réglages du compte, à inviter un collègue dans son équipe, à accepter une invitation, à partager une base avec l'équipe, à régler son profil (nom, avatar, fuseau horaire, mot de passe), à créer et supprimer une clé d'accès pour les programmes, et à ouvrir la console d'administration de l'installation.
> **Point de départ** : menu du compte (pastille aux initiales, en haut à droite) › « Équipe ».
> **Durée** : environ 20 minutes. **Avant** : chapitre 03.

**Attention** : une clé d'accès donne à un programme tous les droits du compte (lire, modifier, supprimer les bases), et la fenêtre « Clé API » affiche chaque clé en entier : ne pas l'ouvrir pendant un partage d'écran, et supprimer toute clé qui a pu être vue. La console d'administration permet de supprimer n'importe quel compte ; elle n'est protégée que par le mot de passe du compte d'administration : ne jamais rendre l'interface accessible à d'autres machines sans l'avoir changé.

## Ce qu'il faut savoir

Chaque **compte** a son propre espace de travail : ses bases, ses assistants, ses agents et ses clés. Une **équipe** permet de partager une partie de cet espace : un objet dont les « Autorisations » valent « Équipe » (une base dans sa « Configuration », un agent dans « Gestion » › « Paramètres ») devient visible des membres invités. Une **clé d'accès** (l'interface dit « Clé API ») permet à un programme d'agir au nom du compte sans mot de passe, par exemple un script qui ajoute chaque soir des documents à une base. Enfin, RAGFlow crée à l'installation un compte d'administration, `admin@ragflow.io`, qui ne sert qu'à la **console d'administration** : la liste des comptes et l'état des services de l'installation. Le travail courant se fait avec un compte ordinaire.

## Se repérer dans les réglages du compte

**Étape 1. Ouvrir la page « Équipe »**
*Où* : menu du compte › « Équipe ».
Cliquer sur la pastille du compte (pastille 1) : la page des réglages s'ouvre, avec son menu à gauche. Cliquer sur « Équipe » (pastille 2).

![Page Équipe](../img/13-exploitation/01-equipe.png)
*Écran : réglages du compte, page « Équipe ».*

| N° | Élément | Rôle |
|---|---|---|
| 1 | pastille du compte | ouvre les réglages du compte ; le menu de gauche donne « Fournisseurs de modèles » (chapitre 03), « Sources de données » et « Canaux de chat » (chapitre 12), « MCP » (chapitre 10), « Équipe », « Profil », « API » ; en bas, la version « v1.0.0 » et la bascule entre thème clair et sombre |
| 2 | « Équipe » | page de l'espace de travail, ici « Banc RAGFlow Espace de travail » |
| 3 | « Membres de l'équipe » | comptes invités : « Nom », « Date de mise à jour », « Adresse e-mail », « Rôle », « Action » ; vide au départ |
| 4 | « Inviter » | ouvre la fenêtre d'invitation (étape suivante) |
| 5 | « Équipes rejointes » | espaces d'autres comptes dont ce compte est membre ; ici son propre espace |
| 6 | « Déconnexion » | ferme la session et revient à la page de connexion |

*Résultat* : la page « Équipe » est affichée.

## Inviter un collègue

L'exemple invite un collègue fictif, « Manuel-Invite », dans l'équipe du compte « Banc RAGFlow ». Il se déroule en deux temps : le propriétaire invite (étapes 2 à 4), puis le collègue accepte depuis son propre compte (étapes 5 et 6). Sur un seul poste, les deux comptes se succèdent dans le même navigateur, grâce à « Déconnexion » ; une fenêtre de navigation privée ouverte à côté permet aussi de garder les deux sessions ouvertes en même temps.

**Étape 2. Créer le compte du collègue**
*Où* : page « Équipe » › « Déconnexion » (capture de l'étape 1, pastille 6), puis page de connexion › « Sign up ».
L'invitation ne crée pas de compte : le collègue doit d'abord avoir le sien. Cliquer sur « Déconnexion », puis, sur la page de connexion, sur « Sign up ». Remplir le formulaire « Create an account » montré au chapitre 02, étape 8 : « Email » `manuel.invite@exemple.fr`, « Nickname » « Manuel-Invite », un mot de passe, puis « Continue ». Se reconnecter ensuite avec le compte propriétaire (chapitre 03, étape 1), et revenir à « Équipe ».

*Résultat* : le compte « Manuel-Invite » existe ; la page « Équipe » du propriétaire est de nouveau affichée.

**Étape 3. Inviter le collègue**
*Où* : « Équipe » › « Inviter ».
Saisir l'adresse du compte à inviter (pastille 1), puis cliquer sur « Oui » (pastille 3). La consigne (pastille 2) rappelle que seul un compte existant peut être invité : avec une adresse sans compte, le message « Astuce : 102 user not found » s'affiche en haut à droite et la fenêtre reste ouverte.

![Fenêtre d'invitation](../img/13-exploitation/02-inviter.png)
*Écran : « Équipe », fenêtre d'invitation remplie.*

| N° | Élément | Rôle |
|---|---|---|
| 1 | « Adresse e-mail » | adresse du compte à inviter, ici `manuel.invite@exemple.fr` |
| 2 | consigne | « Only registered users can be invited. Please register the account before sending an invitation. » |
| 3 | « Oui » | envoie l'invitation ; « Non » annule |

*Résultat* : la fenêtre se ferme et le membre apparaît dans la liste (étape suivante).

**Étape 4. Vérifier le membre invité**
*Où* : « Équipe » › « Membres de l'équipe ».
Le compte invité apparaît dans la liste (pastille 1), avec son rôle (pastille 2). La corbeille (pastille 3) le retire, après confirmation « Supprimer le membre » ; elle sert aussi plus tard, pour retirer un membre qui a accepté.

![Membre invité](../img/13-exploitation/03-membre-invite.png)
*Écran : « Équipe », membre invité.*

| N° | Élément | Rôle |
|---|---|---|
| 1 | membre invité | « Manuel-Invite », date de l'invitation, `manuel.invite@exemple.fr` |
| 2 | « Rôle » | « Invite » : invitation en attente ; il devient « Member » quand le collègue accepte (étape 6) |
| 3 | corbeille | retire le membre, après confirmation |

*Résultat* : l'invitation est envoyée ; le collègue doit maintenant l'accepter.

## Accepter une invitation et partager une base

**Étape 5. Se connecter avec le compte du collègue**
*Où* : menu du compte › « Équipe » › « Déconnexion », puis page de connexion.
Cliquer sur « Déconnexion », puis se connecter avec `manuel.invite@exemple.fr` et son mot de passe, comme au chapitre 03, étape 1 (ou ouvrir une fenêtre de navigation privée et s'y connecter). Ouvrir ensuite le menu du compte (pastille ronde « M », en haut à droite) › « Équipe ».

*Résultat* : la page « Équipe » du collègue s'affiche (étape suivante).

**Étape 6. Accepter l'invitation**
*Où* : compte invité › menu du compte › « Équipe » › « Équipes rejointes ».
La page est celle de l'étape 1, vue depuis l'autre compte. En haut, « Manuel-Invite Espace de travail » : l'espace propre du collègue, dont « Membres de l'équipe » est vide (« Aucune donnée disponible »). En bas, « Équipes rejointes » (pastille 1) : l'équipe qui invite (pastille 2), avec deux boutons, puis, en dernière ligne, son propre espace. Sur la machine d'essai, la page de ce compte neuf s'est affichée avec un en-tête réduit : un bouton de menu (trois traits) à gauche et une icône de traduction à droite remplacent la barre du haut et le menu « Français » ; le contenu de la page est le même. Cliquer sur « Accepter » (pastille 3).

![Invitation reçue](../img/13-exploitation/10-invitation-recue.png)
*Écran : réglages du compte invité, page « Équipe », invitation reçue.*

| N° | Élément | Rôle |
|---|---|---|
| 1 | « Équipes rejointes » | équipes dont ce compte est membre ; la dernière ligne est son propre espace |
| 2 | équipe qui invite | nom du compte qui invite (ici « Banc RAGFlow »), date de l'invitation et adresse |
| 3 | « Accepter » | rejoint l'équipe |
| 4 | « Refuser » | décline l'invitation |

*Résultat* : le message « Opéré » confirme ; les deux boutons disparaissent de la ligne, qui reste dans « Équipes rejointes ». Côté propriétaire, après reconnexion, le rôle du membre passe de « Invite » à « Member ».

**Étape 7. Partager une base avec l'équipe**
*Où* : compte propriétaire › barre du haut › « Base de connaissances » › base ouverte › menu de gauche › « Configuration » › « Autorisations ».
Ouvrir la liste « Autorisations » (montrée au chapitre 06, étape 6, pastille 5), choisir « Équipe » au lieu de « Moi uniquement », puis cliquer sur « Enregistrer » en bas de la page. Un message « No PaddleOCR models added… » peut s'afficher en même temps : il ne concerne que le choix du lecteur des PDF et n'empêche pas l'enregistrement.

*Résultat* : le message « Mis à jour » confirme, et « Équipe » reste affiché après rechargement. Le membre voit la base dans sa propre liste « Base de connaissances », avec le nom du propriétaire sur la carte, et peut l'ouvrir avec tous ses onglets. Un agent se partage par le même réglage, dans « Gestion » › « Paramètres » (chapitre 10, étape 12) ; ce dernier cas n'a pas été essayé.

## Régler son profil

**Étape 8. Ouvrir la page « Profil »**
*Où* : menu du compte › « Profil ».
Chaque réglage a son bouton « Modifier » à droite.

![Page Profil](../img/13-exploitation/04-profil.png)
*Écran : réglages du compte, page « Profil ».*

| N° | Élément | Rôle |
|---|---|---|
| 1 | « Nom d'utilisateur » | nom affiché (« Banc RAGFlow ») |
| 2 | « Télécharger » | change l'« Avatar » (image) |
| 3 | « Fuseau horaire » | « GMT+08:00 Asia/Shanghai » par défaut ; « Modifier » ouvre l'étape suivante |
| 4 | « Adresse e-mail » | identifiant de connexion, non modifiable (« Une fois enregistrée, l'adresse e-mail ne peut pas être modifiée. ») |
| 5 | « Mot de passe » | « Modifier » ouvre « Edit Password » : « Mot de passe actuel », « Nouveau mot de passe », « Confirmer le nouveau mot de passe », puis « Annuler » ou « Enregistrer » |

*Résultat* : le profil est affiché et modifiable.

**Étape 9. Changer le fuseau horaire**
*Où* : « Profil » › « Modifier » en face de « Fuseau horaire ».
Choisir le fuseau dans la liste (pastille 1), par exemple celui de Paris, puis cliquer sur « Enregistrer » (pastille 3).

![Fenêtre Edit Time Zone](../img/13-exploitation/05-fuseau-horaire.png)
*Écran : fenêtre « Edit Time Zone ».*

| N° | Élément | Rôle |
|---|---|---|
| 1 | « Fuseau horaire » | liste des fuseaux, de « GMT-11:00 Pacific/Midway » vers l'est |
| 2 | « Annuler » | referme sans rien changer |
| 3 | « Enregistrer » | enregistre le fuseau du compte |

*Résultat* : le fuseau du compte est changé. Attention : plusieurs pages affichent leurs heures en temps universel quel que soit ce réglage (date de téléversement, détail des tâches, historique des versions d'un agent) ; pour Paris, ajouter une heure en hiver, deux en été.

## Créer et supprimer une clé d'accès

**Étape 10. Ouvrir la page « API »**
*Où* : menu du compte › « API ».
La page « RAGFlow API » donne l'adresse du serveur (pastille 3) et l'accès aux clés (pastille 2).

![Page API](../img/10-api-et-sdk/01-page-api.png)
*Écran : réglages du compte, page « API ».*

| N° | Élément | Rôle |
|---|---|---|
| 1 | « API » | entrée du menu du compte qui ouvre cette page |
| 2 | « Clé API » | ouvre la fenêtre des clés (étape suivante) |
| 3 | « Serveur API » | adresse de base des appels, vue depuis l'interface ; depuis Windows ou WSL, les programmes utilisent `http://127.0.0.1:9380` |
| 4 | copier | copie l'adresse du serveur |
| 5 | « Afficher le contenu » | déplie le sommaire de la documentation des appels, en anglais (détail dans l'annexe A3) |

*Résultat* : la page est ouverte. Sous la documentation, la carte « Langfuse » relie RAGFlow à un service de suivi des appels aux modèles ; elle n'a pas été utilisée.

**Étape 11. Créer une clé**
*Où* : page « API » › « Clé API » › « Créer une nouvelle clé ».
Cliquer sur « Créer une nouvelle clé » (pastille 5) : la clé s'ajoute au tableau (pastille 1). La copier (pastille 3) et la coller dans le programme qui en a besoin. Les clés sont masquées sur la capture.

![Fenêtre Clé API](../img/10-api-et-sdk/02-cles-api.png)
*Écran : fenêtre « Clé API ».*

| N° | Élément | Rôle |
|---|---|---|
| 1 | nouvelle clé | colonne « Token » : la clé entière, en clair (`ragflow-` suivi de 32 caractères), masquée ici |
| 2 | « Créé » | date et heure de création ; la première ligne est la clé utilisée par les scripts de l'installation |
| 3 | copier | copie la clé |
| 4 | corbeille | supprime la clé (étape suivante) |
| 5 | « Créer une nouvelle clé » | ajoute une clé ; aucun nom ni droit à choisir : toute clé a tous les droits du compte |

*Résultat* : la clé est créée et copiée.

**Étape 12. Supprimer une clé**
*Où* : fenêtre « Clé API » › corbeille de la ligne.
Cliquer sur la corbeille de la clé, puis sur « Supprimer » (pastille 2) dans la confirmation.

![Confirmation de suppression d'une clé](../img/10-api-et-sdk/03-supprimer-la-cle.png)
*Écran : fenêtre « Clé API », confirmation de suppression.*

| N° | Élément | Rôle |
|---|---|---|
| 1 | « Non » | annule |
| 2 | « Supprimer » | supprime la clé : tout programme qui l'utilise est ensuite refusé |

*Résultat* : la clé disparaît du tableau ; les autres clés continuent de fonctionner. L'usage des clés dans un programme est décrit dans l'annexe [A3. Automatiser par l'API](../annexes/A3-automatiser-par-l-api.md).

## Ouvrir la console d'administration

La console d'administration n'a aucun lien dans l'interface ordinaire : elle s'ouvre par son adresse, `http://127.0.0.1:8088/admin`, et seul le compte `admin@ragflow.io` y entre. Son mot de passe a été tiré au hasard à l'installation ; il se trouve à la ligne `ADMIN_DEFAULT_PASSWORD` du fichier `donnees/ragflow/ragflow.env`.

**Étape 13. Se connecter à la console**
*Où* : navigateur Windows › `http://127.0.0.1:8088/admin`.
Saisir le courriel (pastille 2) et le mot de passe (pastille 3), puis cliquer sur « Se connecter » (pastille 4).

![Connexion à la console](../img/13-exploitation/06-console-connexion.png)
*Écran : page de connexion de la console d'administration.*

| N° | Élément | Rôle |
|---|---|---|
| 1 | « Console d'administration » | titre de la page |
| 2 | « Email » | `admin@ragflow.io` |
| 3 | « Mot de passe » | mot de passe d'administration, masqué sur la capture |
| 4 | « Se connecter » | ouvre la page « Services » |

*Résultat* : la page « Services » s'affiche (étape suivante).

**Étape 14. Lire l'état des services**
*Où* : console › « Services ».
Chaque ligne est un service de l'installation (pastille 2), avec son état (pastille 3).

![Services](../img/13-exploitation/07-services.png)
*Écran : console d'administration, page « Services ».*

| N° | Élément | Rôle |
|---|---|---|
| 1 | « Services » | page des services ; « Utilisateurs » et « Bac à sable » en dessous |
| 2 | service | par exemple « elasticsearch » (moteur de recherche), port 9200 ; de même « mysql », « minio », « kvrocks », « nats » |
| 3 | « Statut » | « Actif » pour ces cinq services de stockage et de messages |
| 4 | serveur RAGFlow | « ragflow-server-… », port 9380 : affiché « Délai Expiré », comme « ingestor-… » et « syncer-… » |

*Résultat* : l'état est lu. Les trois processus de RAGFlow sont marqués « Délai Expiré » alors que l'interface fonctionnait normalement : cet affichage n'est pas fiable ; l'état réel se vérifie comme au chapitre 02, étape 9.

**Étape 15. Gérer les comptes**
*Où* : console › « Utilisateurs ».
La page liste les comptes (pastille 1) ; les icônes d'action d'une ligne apparaissent au survol.

![Utilisateurs](../img/13-exploitation/08-utilisateurs.png)
*Écran : console d'administration, page « Utilisateurs ».*

| N° | Élément | Rôle |
|---|---|---|
| 1 | « Utilisateurs » | comptes de l'installation : `admin@ragflow.io` (« Superutilisateur ») et `banc.demo@exemple.fr` (« Normal ») |
| 2 | « Nouvel utilisateur » | crée un compte sans passer par l'inscription |
| 3 | « Statut » | « Actif » ; un compte désactivé ne peut plus se connecter |
| 4 | « Type d'utilisateur » | « Normal » ou super-utilisateur |
| 5 | icône de compte à cadenas | change le mot de passe du compte |
| 6 | corbeille | supprime le compte et ses données |

*Résultat* : les comptes sont listés. Ces actions n'ont pas été essayées, pour ne pas toucher au compte de démonstration.

**Étape 16. Lire le réglage du bac à sable**
*Où* : console › « Bac à sable ».
Cette page règle où s'exécute le code lancé par le bloc « Code » des agents (chapitre 10, étape 15).

![Bac à sable](../img/13-exploitation/09-bac-a-sable.png)
*Écran : console d'administration, page « Bac à sable ».*

| N° | Élément | Rôle |
|---|---|---|
| 1 | « Bac à sable » | page de réglage de l'exécution de code |
| 2 | « Sélection du fournisseur » | sept choix : « Self-Managed », « SSH », « Aliyun Code Interpreter », « E2B », « Tenki », « UCloud Agent Sandbox », « Local » |
| 3 | « Self-Managed » | choisi par défaut : un service d'exécution séparé, non installé ici ; « Tester la connexion », « Enregistrer » |
| 4 | « Local » | exécute le code directement dans le serveur, sans aucune isolation : à éviter |

*Résultat* : le réglage est lu, sans modification. « Déconnexion », en bas de la colonne de gauche, ferme la session d'administration.

## Bon à savoir

- Le compte d'administration ne sert qu'à la console ; il ne peut pas être utilisé par les programmes.
- La clé d'accès se crée sans nom : noter à part à quel programme sert chaque clé, pour savoir laquelle supprimer.
- L'inscription libre reste ouverte (lien « Sign up ») : sans risque tant que l'interface n'est joignable que depuis la machine elle-même, comme dans l'installation du chapitre 02.
- Les réglages de sauvegarde, de mise à jour et de sécurité de l'installation sont décrits dans l'annexe [A4. Exploitation](../annexes/A4-exploitation.md).

## En cas de problème

| Symptôme | Cause | Que faire |
|---|---|---|
| « Astuce : 102 user not found » à l'invitation | l'adresse n'a pas de compte | faire créer le compte (« Sign up », étape 2), puis inviter |
| Heures décalées dans certaines pages | heures affichées en temps universel | ajouter une heure (deux en été) pour Paris ; régler aussi « Fuseau horaire » (étape 9) |
| Un programme est refusé après la suppression d'une clé | la clé supprimée était la sienne | créer une nouvelle clé (étape 11) et la donner au programme |
| « Délai Expiré » sur le serveur dans la console | affichage peu fiable de la console | vérifier l'état comme au chapitre 02, étape 9 |

Les autres problèmes sont traités au chapitre [15. En cas de problème](15-en-cas-de-probleme.md).

---
*Version décrite : RAGFlow v1.0.0, essais des 9 et 11 novembre 2026. Détails et preuves : [rapport d'essais](../annexes/A6-rapport-d-essais.md).*
