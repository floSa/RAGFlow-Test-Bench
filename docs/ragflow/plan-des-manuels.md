# Plan des manuels RAGFlow

Plan établi au cadrage le 9 novembre 2026 à partir du plan type du kit et des thèmes de la fiche RAGFlow. Les écarts constatés en cours de rédaction sont notés en fin de page.

## Sommaire

- [Les manuels en une phrase](#les-manuels-en-une-phrase)
- [Contenu détaillé](#contenu-détaillé)
- [Écarts au plan](#écarts-au-plan)

## Les manuels en une phrase

| N° | Manuel | En une phrase |
|---|---|---|
| 00 | [Notions fondamentales](00-notions-fondamentales.md) | Ce qu'est un RAG, et comment RAGFlow l'organise en services. |
| 01 | [Installation sous Windows et WSL2](01-installation.md) | Installer RAGFlow branché sur LLM-Service, sans rien exposer au réseau. |
| 02 | [Prise en main](02-prise-en-main.md) | Visite de l'interface, puis du premier document importé à la première réponse citée, tout à la souris. |
| 03 | [Datasets et découpage](03-datasets-et-decoupage.md) | Choisir un gabarit de découpage et mesurer son effet. |
| 04 | [DeepDoc et correction des passages](04-deepdoc.md) | Lire les scans, les tableaux et la mise en page, puis corriger les passages. |
| 05 | [Assistants de chat et citations](05-assistants-et-citations.md) | Régler la recherche et vérifier les citations. |
| 06 | [Agentic RAG](06-agentic-rag.md) | Comparer la réponse directe et le mode agentique. |
| 07 | [Knowledge Compilation](07-knowledge-compilation.md) | Ce que produisent graphes, arbres, cartes mentales, frises et wikis. |
| 08 | [Agents et gabarits](08-agents.md) | Construire un flux d'agent complet à partir d'un gabarit. |
| 09 | [Sources externes](09-sources-externes.md) | Ingestion par sitemap et synchronisation de sources. |
| 10 | [API HTTP et SDK Python](10-api-et-sdk.md) | Page « API » et clés à la souris, puis automatiser datasets, ingestion et questions. |
| 11 | [Recettes](11-recettes.md) | Cas d'usage complets, de bout en bout. |
| 12 | [Qualité et performances](12-qualite-et-performances.md) | Résultats du banc, jetons et contexte lus dans l'interface, profils matériels, préconisations. |
| 13 | [Exploitation](13-exploitation.md) | Sauvegarde, mise à jour, journaux, sécurité, comptes, équipe et console d'administration. |
| 14 | [Dépannage et FAQ](14-depannage.md) | Les échecs réellement rencontrés, leurs écrans et leur remède. |
| 15 | [Applications de recherche](15-recherche.md) | Créer une page de recherche sur une ou plusieurs bases, la régler et la partager. |

## Contenu détaillé

La [carte de l'interface](annexes/carte-interface.md) dit, page par page, quel manuel couvre chaque écran, menu et réglage.

### 00. Notions fondamentales

RAG, embeddings, découpage, recherche hybride (mots-clés et vecteurs), reranking, citations ; architecture de RAGFlow 1.0 (serveur Go, ingestion, Elasticsearch, MySQL, MinIO, Kvrocks, NATS) avec schéma des services et des ports ; place de LLM-Service ; visite générale de l'interface (barre du haut, en-tête, accueil).

### 01. Installation sous Windows et WSL2

Prérequis mesurés ; relecture du compose ; override (ports sur `127.0.0.1`, secrets générés, données dans `donnees/ragflow/`) ; branchement à LLM-Service ; mémoire consommée par service au repos et en indexation ; premier démarrage ; compte local (formulaire d'inscription) ; « Fournisseurs de modèles » à la souris (ajout et suppression d'une instance, « Définir les modèles par défaut ») ; mise à jour ; désinstallation complète.

### 02. Prise en main

Connexion, choix de la langue, accueil, création d'une base de connaissances, import par « Ajouter un fichier », lancement de l'analyse, lecture des passages, création d'un assistant dans « Discussion », choix de la base, première question, lecture des citations ; une capture annotée par étape. La déclaration des modèles passe au manuel 01.

### 03. Datasets et découpage

Gabarits disponibles en 1.0 (General, Q&A, Manual, Table, Paper, Book, Laws, Presentation, Picture, One, Audio, Email) ; comparaison sur le corpus (au moins General, Table, Paper, Presentation) : nombre de passages, effet sur le banc. Ajouts tirés de la carte : onglet « Configuration » complet (informations de base, « Mode d'analyse », réglages par format), onglet « Journaux », « Créer un fichier vide » et téléversement de dossier, onglet « Ingestion pipeline » de la page « Agent » (pipelines intégrés), page « Gestion des fichiers ».

### 04. DeepDoc et correction des passages

OCR du PDF scanné, structure des tableaux, mise en page ; temps d'analyse par page sur CPU ; visualisation et correction manuelle d'un passage.

### 05. Assistants de chat et citations

Réglages de recherche : top-n, seuil de similarité, poids mots-clés et vecteurs, reranker (absent du socle), message de réponse vide ; effet mesuré sur le banc. Ajouts tirés de la carte : onglet « Test de récupération », « Paramètres du modèle » (« Liberté », « Température », « Top P », pénalités, « Nombre max de tokens », « Thinking »), « Paramètres avancés » (« Afficher la citation », « Texte en parole », « Web search provider », « Métadonnées »), « Plusieurs modèles », actions sur une réponse, icône de partage de l'assistant.

### 06. Agentic RAG

Mode agentique (champ `reasoning`) comparé à la réponse directe : qualité et latence.

### 07. Knowledge Compilation

Composant Compiler d'un pipeline d'ingestion : ce que chaque type d'artefact produit sur un document court, durée observée. Ajouts tirés de la carte : onglet « Artifacts » d'une base (« Wiki », « Tree/PageIndex », « Graph », « Mind map », « Timeline »), onglet « Compilation operator » de la page « Agent ».

### 08. Agents et gabarits

Un gabarit d'agent, un flux complet, exécution par l'interface et par l'API. Ajouts tirés de la carte : menu de création (« Créer depuis un blanc », « Créer depuis un modèle », « Importer un fichier JSON »), boutons du canevas (« Save draft », « Exécuter », « Lancer », « Publier »), page « Mémoire » (création : « Type de mémoire », « Modèle d'embedding », « LLM »), page « MCP » du menu du compte (serveurs d'outils des agents).

### 09. Sources externes

Ingestion d'un site local de test par sitemap ; synchronisation de sources ; limites (adresses privées refusées). Ajouts tirés de la carte : page « Sources de données » du menu du compte (une quarantaine de connecteurs), « Lier une source de données » dans la configuration d'une base, page « Canaux de chat » (décrite ; branchement d'un bot non couvert : compte en ligne chez un tiers).

### 10. API HTTP et SDK Python

Clé d'API, datasets, téléversement, analyse, assistants, questions ; défauts relevés du SDK 1.0.0 et contournements ; exemples exécutés (`exemples/ragflow/`). Page « API » du menu du compte à la souris (« Clé API » : création et suppression d'une clé, « Serveur API », documentation intégrée ; carte « Langfuse » non couverte).

### 11. Recettes

Assistant documentaire d'entreprise sur le corpus ; automatisation d'une ingestion quotidienne par l'API ; résultat de chaque recette montré dans l'interface (base et assistant « Démo Vélanor », base remplie par la recette).

### 12. Qualité et performances

Banc (38 questions) : réglages par défaut, réglages recommandés, mode agentique ; jetons et durée lus sous une réponse ; taille de contexte réglée par « Tokens maximum » (« Modifier le modèle ») ; latences, RAM, VRAM ; profils matériels sans et avec GPU ; préconisations d'usage (réglages, contexte, matériel, causes de lenteur).

### 13. Exploitation

Sauvegarde et restauration des volumes, mise à jour (migration irréversible depuis 0.27), journaux, sécurité (ports, secrets, compte d'administration), comptes et équipes, API d'administration. Menu du compte, pages « Équipe » (« Inviter », invitation refusée pour une adresse sans compte, membre retiré) et « Profil » (nom, avatar, fuseau horaire réglé par défaut sur « GMT+08:00 Asia/Shanghai », mot de passe), thème, « Déconnexion » ; console d'administration `/admin` (« Services », « Utilisateurs », « Bac à sable »).

### 14. Dépannage et FAQ

Tableau Symptôme | Cause probable | Action, tiré des journaux d'essai ; écrans d'erreur provoqués exprès (connexion refusée, erreur de contexte, réponse « not found », page 404).

### 15. Applications de recherche

Page « Recherche » : création d'une application de recherche (« Nom »), choix des bases, réglages de recherche, affichage des résultats et partage. Manuel ajouté au plan d'après la carte de l'interface.

## Écarts au plan

- 11 novembre 2026, carte de l'interface (`carte-interface.md`) : le plan initial ne couvrait pas les pages « Recherche », « Mémoire », « Gestion des fichiers », ni, dans le menu du compte, « Sources de données », « Canaux de chat », « MCP », « Équipe », « Profil » et « API ». Elles sont rattachées aux manuels les plus proches (03, 05, 07, 08, 09, 10, 13, voir ci-dessus), sauf « Recherche », qui reçoit un manuel 15. Le numéro 15 suit le dépannage pour ne pas renuméroter les manuels déjà écrits et leurs liens.
- 11 novembre 2026 : la déclaration des modèles passe du manuel 02 au manuel 01 (« Fournisseurs de modèles » à la souris) ; le manuel 02 devient une procédure complète à la souris, de la connexion à la première réponse citée.
- 11 novembre 2026, manuels 03 à 06 réécrits en procédures à la souris : la page « Gestion des fichiers » et l'onglet « Ingestion pipeline » sont traités au manuel 03 ; l'icône d'avion en papier d'un assistant (« Intégrer dans la page web ») au manuel 05 et non au manuel 10 ; le manuel 04 montre un défaut de v1.0.0 (« Confirmer » sans effet sur un passage de PDF modifié) et son contournement par un passage ajouté. Les conversations ne se renomment pas dans l'interface v1.0.0.
- 11 novembre 2026, manuels 07 à 09 et 15 réécrits en procédures à la souris : le manuel 07 crée l'opérateur, le pipeline et la base dans l'interface (une base par type d'artefact ; Wiki et PageIndex échouent avec `gemma4:e4b`) ; le manuel 08 couvre aussi « Mémoire » et « MCP » ; le manuel 09 montre « Sources de données » et « Canaux de chat » ; le manuel 15 est écrit.
- 11 novembre 2026, manuels 10 à 14 : la console d'administration `/admin`, absente de la carte (aucun lien dans l'interface ordinaire), est ajoutée au manuel 13 ; la fenêtre « Modifier le modèle » (« Tokens maximum ») est décrite au manuel 12 ; l'onglet « Artifacts » vide n'est pas recapturé au manuel 14, qui renvoie au manuel 07.
