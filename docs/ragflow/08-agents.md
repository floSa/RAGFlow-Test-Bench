# 08. Agents et gabarits

> **Objet** : construire un agent à la souris à partir d'un gabarit, le relier à une base de connaissances, comprendre chaque bloc du canevas et son panneau de réglages, l'essayer (« Exécuter »), converser avec lui (« Lancer »), le publier, l'exporter et le réimporter, partir d'un canevas vide ; lui donner une mémoire (page « Mémoire ») ; connaître la page « MCP » ; l'interroger enfin par l'API.
> **Prérequis** : [assistants de chat et citations](05-assistants-et-citations.md) (réglages de recherche) ; [Knowledge Compilation](07-knowledge-compilation.md) (canevas d'un pipeline, même principe) ; [API HTTP et SDK Python](10-api-et-sdk.md) pour la partie programmée.
> **Version décrite** : RAGFlow v1.0.0 (image `infiniflow/ragflow:v1.0.0`), Windows 11 + WSL2 (Ubuntu 24.04), LLM-Service branche `service-vllm` (vLLM 0.29.0 : `gemma4:e4b`, `bge-m3`), contexte déclaré de 16 384 jetons.
> **Statut des informations** : [Vérifié] observé ou mesuré les 9 et 11 novembre 2026 sur la machine d'essai (Ryzen 5 9600X, 32 Go, RTX 4060 Ti 16 Go) ; [Source] documentation officielle ou code source au tag v1.0.0 ; [Estimation] calcul non mesuré ; [À tester] non documenté et non essayé.
> **Précautions** : agents « Manuel-Agent-Documentaire », « Manuel-Agent-Importe », « Manuel-Agent-Vierge » et mémoire « Manuel-Memoire » créés par le scénario de captures puis supprimés (`outils/ragflow/nettoyer_manuel.py`) ; la base « Démo Vélanor » est seulement lue par l'outil de recherche ; l'agent « Agent démo Vélanor » du jeu de démonstration n'est pas modifié ; aucun outil en ligne (recherche web, courriel) ni serveur MCP n'est branché.

**Risque — croix des panneaux.** Dans le panneau d'un bloc agent, la croix à droite d'un outil (« Retrieval ») retire l'outil de l'agent, sans confirmation, et l'enregistrement automatique le rend définitif. Seule la croix de l'en-tête du panneau, en haut à droite, ferme le panneau. Observé pendant la mise au point du scénario (outil retiré, agent recréé). [Vérifié] (`outils/resultats/ragflow/captures/08-agents/scenario.log`, et commentaire de `fermer_panneau` dans le scénario)

Une capture par écran nouveau ; les étapes qui reviennent sur un écran déjà montré renvoient à sa capture. Toutes les captures de ce manuel viennent du scénario `agents` de `outils/ragflow/captures/manuels_07_15.py`, qui fait chaque geste à la souris, dans l'ordre des sections. Le texte de chaque page capturée et la liste de ses éléments visibles sont dans `outils/resultats/ragflow/captures/08-agents/` (même nom que l'image), le déroulé, les durées et la correspondance avec les noms de capture d'origine dans `scenario.log`. [Vérifié]

## Sommaire

1. [La page « Agent »](#1-la-page--agent-)
2. [Créer un agent depuis un gabarit](#2-créer-un-agent-depuis-un-gabarit)
3. [Le canevas, bloc par bloc](#3-le-canevas-bloc-par-bloc)
4. [Essayer, converser, publier](#4-essayer-converser-publier)
5. [Le menu « Gestion » : variables, paramètres, intégration, export](#5-le-menu--gestion---variables-paramètres-intégration-export)
6. [Importer un fichier JSON](#6-importer-un-fichier-json)
7. [Créer depuis un blanc et ajouter un bloc](#7-créer-depuis-un-blanc-et-ajouter-un-bloc)
8. [Donner une mémoire à l'agent](#8-donner-une-mémoire-à-lagent)
9. [Serveurs MCP](#9-serveurs-mcp)
10. [Interroger l'agent par l'API](#10-interroger-lagent-par-lapi)
11. [Dépannage](#dépannage)
12. [Sources](#sources)

## 1. La page « Agent »

### Essentiel

Un agent est un flux : des blocs reliés, dont au moins un bloc qui interroge un modèle et décide lui-même d'appeler des outils (recherche dans une base, recherche web, code…). Il sert quand une question demande plusieurs étapes ou des outils ; pour des questions simples sur une base, un assistant de « Discussion » (manuel [05](05-assistants-et-citations.md)) suffit.

1. Cliquer sur « Agent » dans la barre du haut. L'onglet « Workflow » liste les agents (ici « Agent démo Vélanor », du jeu de démonstration), avec un filtre et « Rechercher » ; les onglets « Ingestion pipeline » et « Compilation operator » servent à l'ingestion (manuel [07](07-knowledge-compilation.md)). Cliquer sur « + » : le menu propose trois façons de créer un agent.

![Menu de création](img/08-agents/01-menu-de-creation.png)

| N° | Élément | Rôle |
|---|---|---|
| 1 | « Créer depuis un blanc » | canevas réduit au bloc « Commencer » (section 7) |
| 2 | « Créer depuis un modèle » | part d'un gabarit prêt à l'emploi (section 2) |
| 3 | « Importer un fichier JSON » | recrée un agent exporté (section 6) |

## 2. Créer un agent depuis un gabarit

### Essentiel

But : créer « Manuel-Agent-Documentaire », un agent qui répond aux questions à partir de la base « Démo Vélanor », depuis le gabarit « Your starter dataset chatbot ».

1. Cliquer sur « Créer depuis un modèle ». La page des gabarits s'ouvre, rangée par catégories. Survoler la carte « Your starter dataset chatbot », puis cliquer sur « Utiliser ».

![Gabarits d'agents](img/08-agents/02-gabarits.png)

| N° | Élément | Rôle |
|---|---|---|
| 1 | « Recommandé » | gabarits mis en avant (questions sur une base, recherche approfondie, rédaction…) |
| 2 | « Agent » | gabarits multi-agents ; viennent ensuite « Support client », « Marketing », « Application grand public » |
| 3 | « Autre » | gabarits divers |
| 4 | carte « Your starter dataset chatbot » | système de questions et réponses fondé sur une base de connaissances (description en anglais) |
| 5 | « Utiliser » | apparaît au survol ; ouvre la fenêtre « Create workflow » |

2. Dans la fenêtre « Create workflow », saisir le nom (« Manuel-Agent-Documentaire »), choisir le modèle dans la liste « Modèle », puis la base dans « Bases de connaissances » : la fenêtre la demande parce que le gabarit contient une étape de recherche sans base (« This template contains 1 retrieval step(s) without a bound dataset… »). Cliquer sur « Confirmer ».

![Fenêtre Create workflow remplie](img/08-agents/03-create-workflow.png)

| N° | Élément | Rôle |
|---|---|---|
| 1 | « Modèle » | `gemma4:e4b` de l'instance `llm-service-chat` (manuel [01](01-installation.md)) : modèle de tous les blocs agents du gabarit ; obligatoire |
| 2 | « Bases de connaissances » | « Démo Vélanor », appliquée à chaque étape de recherche, modifiable ensuite ; la croix retire la base |
| 3 | « Confirmer » | crée l'agent et ouvre son canevas |

### Pour aller plus loin

La page des gabarits en compte 19, en anglais, dont plusieurs supposent un service en ligne (recherche web Tavily, bourse, courriel) et deux sont des pipelines d'ingestion (« Title Chunker », « Chunk Summary »). La liste se lit aussi par l'API : `GET /api/v1/agents/templates` [Testée]. [Vérifié] (`outils/resultats/ragflow/essai-2026-11-09-agent.log` ; catégories relevées dans `scenario.log`)

## 3. Le canevas, bloc par bloc

### Essentiel

But : comprendre ce que fait chaque bloc de l'agent et où se règle chaque chose. Un clic sur un bloc ouvre son panneau de réglages à droite ; la croix de l'en-tête du panneau le ferme.

1. Le canevas montre le flux du gabarit : une question entre par « Commencer », passe par l'agent, qui appelle l'outil de recherche, puis la réponse sort par « Message_0 ». En haut, « Save draft » enregistre le brouillon (le canevas s'enregistre aussi tout seul), « Exécuter » essaie l'agent dans un panneau, « Lancer » ouvre la page de conversation, « Publier » crée une version, « Gestion » ouvre le menu de l'agent (section 5).

![Canevas de l'agent](img/08-agents/04-canevas.png)

| N° | Élément | Rôle |
|---|---|---|
| 1 | « Commencer » | point d'entrée, mode « Conversationnel » ; son panneau règle « Mode », « Activation de l'accueil », « Message de bienvenue » et « Entrée » (variables demandées à l'utilisateur avant la conversation, aucune ici) |
| 2 | « Docs QA Agent » | bloc agent : modèle `gemma4:e4b` et consignes (étape 2) |
| 3 | « Retrieval » | outil de l'agent, relié sous lui : recherche dans la base (étape 3) |
| 4 | « Message_0 » | renvoie la sortie de l'agent (étape 4) |
| 5 | note | « Workflow Overall Description » : texte libre, sans effet sur l'exécution |

2. Cliquer sur « Docs QA Agent ».

![Panneau de l'agent](img/08-agents/05-agent.png)

| N° | Élément | Rôle |
|---|---|---|
| 1 | « Modèle » | modèle du bloc ; l'entonnoir filtre la liste par type |
| 2 | « Invite système » | consignes du bloc, en anglais dans le gabarit (« Answer questions EXCLUSIVELY based on information retrieved from the connected knowledge base… ») ; les variables s'insèrent par `/` ou par l'icône « (x) » |
| 3 | essai du bloc | triangle de l'en-tête : exécute ce bloc seul |

Plus bas dans le même panneau, sans nouvelle capture :

- « Invite utilisateur » : message transmis au modèle, « The user query is » suivi de la variable « Entrée de départ / sys.query » (la question posée) ;
- « Outils » : « Retrieval », avec son crayon (réglages) et sa croix, qui retire l'outil immédiatement (voir le risque en tête de manuel) ; « Ajouter des outils » ouvre une liste à deux onglets : « Intégré » (rubriques « Rechercher » : Tavily, Querit, Google, DuckDuckGo, Wikipedia, SearXNG, Keenable, You.com, Sofya, Search1API, YahooFinance, PubMed, BGPT, Google Scholar, ArXiv, WenCai ; « Communication » : Email ; « Développeur » : GitHub, ExeSQL, Code ; « Récupération ») et « MCP » (outils des serveurs MCP, section 9) ;
- « Agent », « Ajouter un agent » : sous-agent que cet agent peut appeler (agents en équipe) ;
- « Paramètres avancés », ouvert par défaut : « Afficher les citations », « Nombre maximum de cycles de réflexion » (5 tours appel d'outil puis réflexion), « Taille de la fenêtre d'historique des messages », « Nombre maximum de tentatives » et « Délai après une erreur », « Méthode d'exception », puis « Sortie » (`content: string`) et « Sortie structurée » (format JSON imposé).

[Vérifié] (`outils/resultats/ragflow/captures/08-agents/05-agent.txt` ; liste des outils dans `scenario.log`)

3. Fermer le panneau, puis cliquer sur l'outil « Retrieval » sous l'agent.

![Panneau Retrieval](img/08-agents/06-retrieval.png)

| N° | Élément | Rôle |
|---|---|---|
| 1 | « Récupération depuis » | « Ensemble de données » (une base) ou « Mémoire » (une mémoire, section 8) ; « Description » au-dessus dit au modèle quand utiliser l'outil |
| 2 | « Démo Vélanor » | base interrogée, reprise de la fenêtre de création ; la liste permet d'en choisir d'autres |
| 3 | « Paramètres avancés » | réglages de la recherche, comme pour un assistant (manuel [05](05-assistants-et-citations.md)) : « Seuil de similarité » (20), « Poids de similarité par mots-clés » (full-text 0,70, vector 0,30), « Rerank candidates » (64), « Top N » (8), « Modèle de réordonnancement » (aucun dans le banc), « Métadonnées », « Recherche inter-langues » |

4. Fermer le panneau, puis cliquer sur « Message_0 ».

![Panneau Message](img/08-agents/07-message.png)

| N° | Élément | Rôle |
|---|---|---|
| 1 | « Messages » | contenu renvoyé : la variable « Docs QA Agent / content » |
| 2 | « Ajouter un message » | ajoute un autre contenu de sortie (texte fixe ou variable) |
| 3 | « Type de fichier à télécharger » | format de fichier dans lequel proposer la réponse au téléchargement [À tester] |
| 4 | « Lecture automatique audio » | lit la réponse à voix haute (demande un « Modèle TTS », absent du banc) |
| 5 | « Enregistrer en mémoire » | mémoire où archiver l'échange (section 8) ; « ID utilisateur » en dessous |

5. Cliquer sur « Save draft ».

## 4. Essayer, converser, publier

### Essentiel

But : vérifier que l'agent répond juste, puis le rendre utilisable.

1. Cliquer sur « Exécuter ». Le panneau « Discussion » s'ouvre à droite. Saisir « Qui est le directeur de production de Vélanor ? » et cliquer sur l'avion en papier. La réponse s'affiche en 5,4 s ; les icônes au-dessus copient, lisent à voix haute ou affichent le détail de l'exécution.

![Essai par Exécuter](img/08-agents/08-executer.png)

| N° | Élément | Rôle |
|---|---|---|
| 1 | réponse | « According to the documentation, Julien Moreau is the production director at Vélanor. This information comes from a voicemail recorded on November 3rd. » : juste, tirée du message vocal transcrit, mais en anglais |

2. Fermer le panneau, puis cliquer sur « Lancer ». La page de conversation s'ouvre : « Sessions » (avec « + » pour une nouvelle session et « Rechercher des sessions ») à gauche, zone « Saisissez votre message ici... » en bas (trombone, micro, envoi). Saisir « Quel est le plafond des pénalités de retard du contrat Batterix ? » et appuyer sur Entrée. La réponse arrive en 6,3 s.

![Conversation par Lancer](img/08-agents/09-lancer.png)

| N° | Élément | Rôle |
|---|---|---|
| 1 | session | « Quel est le plafond des pénalités… » : la session prend le texte de la première question ; l'essai de l'étape 1 apparaît aussi comme session |
| 2 | réponse | « …0.5% of the order amount per day of delay, capped at 8% of the order amount », avec la source (« Article 6 » du contrat BX-2025-117) |

3. Revenir au canevas et cliquer sur « Publier » : la fenêtre demande un « Alias » (ici « v1 ») puis « Confirmer », comme pour un pipeline (manuel [07](07-knowledge-compilation.md), section 3, étape 11). L'intégration web et l'API servent la version publiée. « Gestion », « Historique des versions » liste ensuite la version « Manuel-Agent-Documentaire_2026-11-11 15:29:36 v1 », avec l'aperçu de son canevas et trois boutons : télécharger en JSON, restaurer dans le brouillon, supprimer. [Vérifié] (`scenario.log`, ligne « historique »)

Les deux réponses sont justes, en anglais, comme le 9 novembre par l'API (section 10). [Vérifié] (`scenario.log`, lignes « réponse dans »)

### Pour aller plus loin

- Pour des réponses en français, traduire l'« Invite système » et l'« Invite utilisateur » du bloc agent [À tester].
- Les heures ne sont pas homogènes : le nom de la version porte l'heure de Paris (15:29:36), la mention « Créé » et « Sauvegardé automatiquement » l'heure universelle (14:29:36). [Vérifié] (`scenario.log`, ligne « historique »)

## 5. Le menu « Gestion » : variables, paramètres, intégration, export

### Essentiel

Le menu « Gestion » du canevas propose :

- « Variable de conversation » : fenêtre avec « Ajouter », pour déclarer des variables lues et écrites par tous les blocs pendant une session ;
- « Historique des versions » : versions publiées (section 4, étape 3) ;
- « Exporter » : télécharge l'agent en JSON ; ici `Manuel-Agent-Documentaire.json`, 13 549 octets, clés `components`, `globals`, `graph`, `history`, `memory`, `messages`, `path`, `retrieval`, `variables` [Vérifié] (`scenario.log`, ligne « export ») ;
- « Paramètres » : « Titre », « Photo » (« Télécharger », 4 Mo au plus), « Description », « Autorisations » (« Moi » ou « Équipe », manuel [13](13-exploitation.md)), « Enregistrer » ;
- « Intégrer dans la page web » (étape 1).

1. « Gestion », « Intégrer dans la page web » donne le code à coller dans un site ; le jeton d'accès qu'il contient est masqué sur la capture.

![Intégrer dans la page web](img/08-agents/10-integrer.png)

| N° | Élément | Rôle |
|---|---|---|
| 1 | « Embed Setup » | réglages : « Type d'intégration », « Thème » (« Clair », « Sombre »), « Cacher l'avatar », « Publié » |
| 2 | « Widget Customization » | titre, textes et couleurs du widget |
| 3 | « Type d'intégration » | « Chat plein écran (iframe traditionnel) » ou « Widget flottant (style Intercom) » |
| 4 | « Paramètres régionaux » | langue du widget ; « ID utilisateur » en dessous, puis « Code d'intégration » (masqué) et « Agent ID » |
| 5 | « Ouvrir dans un nouvel onglet » | ouvre la page de conversation partagée |

### Pour aller plus loin

Le code d'intégration contient un jeton `auth=` qui donne accès à l'agent sans compte : ne le publier que sur un site de confiance, servi en `127.0.0.1` dans ce banc. Les mêmes réglages existent pour un assistant (manuel [05](05-assistants-et-citations.md)).

## 6. Importer un fichier JSON

### Essentiel

But : recréer un agent à partir d'un export, par exemple pour le copier vers une autre installation.

1. « Agent », « + », « Importer un fichier JSON ». Saisir un nom, déposer le fichier exporté dans « DSL », puis cliquer sur « Enregistrer ». L'agent « Manuel-Agent-Importe » s'ouvre, puis apparaît dans la liste : c'est une copie de « Manuel-Agent-Documentaire » (mêmes blocs, même base).

![Importer un fichier JSON](img/08-agents/11-importer-json.png)

| N° | Élément | Rôle |
|---|---|---|
| 1 | « Nom » | ici « Manuel-Agent-Importe » |
| 2 | « DSL » | le fichier JSON de l'agent (onglet « Fichiers ») |
| 3 | `agent-exporte.json` | fichier exporté à la section 5 |
| 4 | « Enregistrer » | crée l'agent et ouvre son canevas |

## 7. Créer depuis un blanc et ajouter un bloc

### Essentiel

But : partir d'un canevas vide et ajouter un bloc.

1. « Agent », « + », « Créer depuis un blanc », saisir « Manuel-Agent-Vierge » et cliquer sur « Confirmer ». Le canevas ne contient que « Commencer ». Survoler ce bloc et cliquer sur le « + » de son bord droit : le menu « Étape suivante » liste les blocs.

![Menu des blocs](img/08-agents/12-menu-des-blocs.png)

| N° | Élément | Rôle |
|---|---|---|
| 1 | « + » | ajoute un bloc après « Commencer » |
| 2 | « Fondation » | « Agent », « Récupération », « Dialogue », « Message », « En attente de réponse » |
| 3 | « Agent » | bloc agent (modèle, consignes, outils) |
| 4 | « Flux » | « Interrupteur », « Itération », « Boucle », « Catégoriser » : branches et répétitions |
| 5 | « Manipulation des données » | « Code », « Traitement du texte », « Opérations sur les données », « Assignateur de variables », « Opérations sur les listes », « Agrégateur de variables » |
| 6 | « Outils » | outils en blocs : recherche web, ExeSQL, Email, GitHub, « Requête HTTP », « Générateur de Documents »… |

2. Choisir « Récupération », puis cliquer sur « Save draft ». Le bloc apparaît relié à « Commencer » ; il se règle comme l'outil « Retrieval » (section 3, étape 3), et « Checklist » signale le réglage manquant tant qu'aucune base n'est choisie. [Vérifié] (`scenario.log`, phase `blanc`)

### Pour aller plus loin

Le « + » n'ouvre le menu que sur un bloc sans suite ; les blocs se relient aussi en tirant un trait d'une poignée à l'autre. Le même canevas sert aux pipelines d'ingestion (manuel [07](07-knowledge-compilation.md)).

## 8. Donner une mémoire à l'agent

### Essentiel

Une mémoire garde les échanges d'un agent d'une session à l'autre, vectorisés pour être retrouvés ensuite (par l'outil « Retrieval » réglé sur « Mémoire »). But : créer « Manuel-Memoire » et y enregistrer les échanges de l'agent.

1. Cliquer sur « Mémoire » dans la barre du haut. La page affiche « Aucune mémoire créée pour le moment » et un « + ». Cliquer sur « + », saisir le nom, garder les modèles proposés.

![Créer une mémoire](img/08-agents/13-creer-une-memoire.png)

| N° | Élément | Rôle |
|---|---|---|
| 1 | « Nom » | ici « Manuel-Memoire » |
| 2 | « Type de mémoire » | ce qui est gardé ; liste à choix multiples : « (Tout sélectionner) », « brut » (échanges tels quels, gardé ici), « sémantique » (faits extraits), « épisodique » (événements datés), « procédural » (façons de faire), puis « Effacer » et « Fermer » ; refermer la liste par « Fermer », car Échap ferme toute la fenêtre |
| 3 | « Modèle d'embedding » | `bge-m3` : vectorise les souvenirs |
| 4 | « LLM » | `gemma4:e4b` : extrait les souvenirs des échanges |
| 5 | « Confirmer » | crée la mémoire |

2. La mémoire apparaît dans la liste ; un clic l'ouvre. Sa page a deux onglets : « Messages » (souvenirs enregistrés : « ID de session », « Agent », « Type », « Date de validité », « Oublier le », « Activer », « Action » ; « Aucune donnée disponible » au départ) et « Configuration » (« Nom », « Avatar », « Description », « Modèle d'embedding », « LLM », « Type de mémoire », « Taille de la mémoire (Bytes) », « Paramètres avancés » pour les invites et la température de l'extraction). [Vérifié] (`scenario.log`, lignes « page de la mémoire » et « configuration de la mémoire »)

3. Ouvrir le canevas de « Manuel-Agent-Documentaire », cliquer sur « Message_0 », ouvrir « Enregistrer en mémoire » (section 3, étape 4) et choisir « Manuel-Memoire ». Fermer le panneau et cliquer sur « Save draft ».

4. « Lancer », « + » (nouvelle session), puis la question « Combien de salariés compte Vélanor au 31 décembre 2025 ? ». L'agent répond 412 salariés, avec le détail par site. Revenir à la mémoire, onglet « Messages » : l'échange y figure.

![Messages de la mémoire](img/08-agents/14-messages-de-la-memoire.png)

| N° | Élément | Rôle |
|---|---|---|
| 1 | message mémorisé | session, agent « Manuel-Agent-Documentaire », type, date ; l'interrupteur « Activer » le met de côté sans l'effacer |
| 2 | « Type » | « Brut » |
| 3 | « Oublier le » | date d'oubli, vide : gardé sans limite |

Le souvenir est apparu moins de 10 s après la réponse. [Vérifié] (`scenario.log`, lignes « réponse avec mémoire » et « messages de la mémoire »)

### Pour aller plus loin

Relire la mémoire dans une session suivante demande un outil « Retrieval » réglé sur « Récupération depuis » « Mémoire » (section 3, étape 3) : non essayé, [À tester].

## 9. Serveurs MCP

### Essentiel

MCP (Model Context Protocol) est un protocole qui expose des outils (lire un agenda, interroger un logiciel métier…) à un modèle. Un serveur MCP déclaré ici ajoute ses outils à l'onglet « MCP » de « Ajouter des outils » (section 3, étape 2).

1. Cliquer sur l'avatar du compte (pastille aux initiales), puis sur « MCP ». La page « Serveurs MCP » affiche « Aucun serveur MCP disponible », avec « Rechercher », « Gestion en masse » (actions sur plusieurs serveurs), « Importer » et « Ajouter MCP ». Cliquer sur « Ajouter MCP ». La fenêtre est refermée sans enregistrer : le banc n'a pas de serveur MCP.

![Ajouter MCP](img/08-agents/15-ajouter-mcp.png)

| N° | Élément | Rôle |
|---|---|---|
| 1 | « Nom » | nom du serveur |
| 2 | « URL » | adresse du serveur MCP |
| 3 | « Type de serveur » | protocole de transport, « sse » par défaut |
| 4 | « Authorization Token » | jeton d'accès au serveur, s'il en demande un |
| 5 | « Enregistrer » | enregistre ; « 0 outils disponibles » se remplit quand le serveur répond |

### Pour aller plus loin

Brancher un vrai serveur MCP et l'utiliser dans un agent : [À tester]. Comme pour les sources de données (manuel [09](09-sources-externes.md)), une adresse privée est probablement refusée tant que `ALLOW_ANY_HOST` vaut 0 [À tester].

## 10. Interroger l'agent par l'API

### Essentiel

L'agent « Agent démo Vélanor » du jeu de démonstration a été créé le 9 novembre par l'API, depuis le même gabarit, par `outils/ragflow/essai_agent.py` (le script renseigne la base et le modèle du gabarit, deux `dataset_ids` et deux `llm_id`).

| Étape | Appel [Testée] |
|---|---|
| Créer l'agent | `POST /api/v1/agents` avec `{"title": "…", "dsl": …}` |
| Ouvrir une session | `POST /api/v1/agents/{agent}/sessions` avec `{}` |
| Poser une question | `POST /api/v1/agents/chat/completions` avec `{"agent_id", "session_id", "question", "stream": false}` |

Résultats [Vérifié] (`outils/resultats/ragflow/essai-2026-11-09-agent.log`) :

| Question | Durée | Réponse (début) |
|---|---|---|
| Qui est le directeur de production de Vélanor ? | 3,0 s | « According to the knowledge base, Julien Moreau is the production director at Vélanor. » |
| Quel est le plafond des pénalités de retard du contrat Batterix ? | 3,6 s | « …0.5% of the order amount per day of delay, capped at 8% of the order amount » |
| Combien de salariés compte Vélanor au 31 décembre 2025 ? (SDK) | 5,2 s | « …is **412 employees** (412 salariés) » |

### Pour aller plus loin

- La réponse est dans `data.data.content`, les passages dans `data.data.reference`.
- Le SDK fonctionne pour les agents : `agent.create_session()` puis `next(iter(session.ask(question, stream=False)))`. C'est l'inverse des assistants de chat, pour lesquels `Session.ask` répond 404 (manuel [10](10-api-et-sdk.md)). [Vérifié] (même journal)
- `RAGFlow.create_agent` du SDK renvoie `None` : retrouver l'agent par `list_agents()`. [Source] (`sdk/python/ragflow_sdk/ragflow.py`)

## Dépannage

| Symptôme | Cause probable | Action |
|---|---|---|
| L'agent répond en anglais à une question en français | consignes du gabarit en anglais | traduire « Invite système » et « Invite utilisateur » du bloc agent |
| L'agent ne trouve rien dans les documents | aucune base dans l'outil « Retrieval » | choisir la base (section 3, étape 3) ou à la création (section 2) |
| L'outil « Retrieval » a disparu de l'agent | croix à droite de l'outil cliquée dans le panneau de l'agent | « Ajouter des outils », « Récupération », puis régler la base ; ou « Historique des versions », restaurer |
| La fenêtre « Créer une mémoire » se ferme en choisissant le type | Échap ferme toute la fenêtre | refermer la liste par « Fermer » |
| « Checklist » signale un problème | bloc sans réglage obligatoire (base, modèle) | ouvrir le bloc signalé et compléter |
| `create_agent` du SDK ne rend pas l'agent | la méthode renvoie `None` | `list_agents()` puis filtrer par titre |

## Sources

- Scénario : `outils/ragflow/captures/manuels_07_15.py` (scénario `agents`, phases `liste`, `modele`, `canevas`, `essai`, `conversation`, `gestion`, `json`, `blanc`, `memoire`, `memoire_page`, `memoire_agent`, `mcp`), lancé par `outils/communs/captures/lancer.sh` ; nettoyage : `outils/ragflow/nettoyer_manuel.py`
- Images : `docs/ragflow/img/08-agents/` ; textes des pages et déroulé : `outils/resultats/ragflow/captures/08-agents/` (jeton du code d'intégration remplacé par `<masqué>`)
- Script et journal de l'API : `outils/ragflow/essai_agent.py`, [essai de l'agent](../../outils/resultats/ragflow/essai-2026-11-09-agent.log)
- Code au tag v1.0.0 : `internal/handler/agent.go`, `sdk/python/ragflow_sdk/` ; https://ragflow.io/docs/
