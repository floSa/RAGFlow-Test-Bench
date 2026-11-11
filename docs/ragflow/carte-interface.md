# Carte de l'interface RAGFlow

Liste de contrôle de la couverture des manuels : chaque page, menu, onglet et réglage visible de l'interface web de RAGFlow v1.0.0, avec le manuel qui le décrit. Relevé le 11 novembre 2026, connecté avec le compte local et l'interface en français, par le scénario Playwright `outils/ragflow/captures/carte.py` (scénario `carte`). Le texte complet de chaque page, son adresse et l'inventaire de ses éléments visibles (boutons, onglets, champs, liens) sont dans `outils/resultats/ragflow/captures/carte/` (un fichier par capture, même nom).

Le parcours est en lecture seule : les fenêtres de création sont ouvertes puis fermées par « Échap » sans rien enregistrer ; le jeu de démonstration (« Démo Vélanor », « Agent démo Vélanor ») sert de page d'exemple sans être modifié.

## Sommaire

- [En-tête et accueil](#en-tête-et-accueil)
- [Base de connaissances](#base-de-connaissances)
- [Discussion](#discussion)
- [Recherche](#recherche)
- [Agent](#agent)
- [Mémoire](#mémoire)
- [Gestion des fichiers](#gestion-des-fichiers)
- [Menu du compte](#menu-du-compte)
- [Ce qui n'est pas couvert](#ce-qui-nest-pas-couvert)

Les manuels marqués « prévu » sont inscrits au [plan des manuels](plan-des-manuels.md) et pas encore écrits.

## En-tête et accueil

![Accueil](img/carte/01-accueil.png)

![Menu de langue ouvert](img/carte/02-menu-langue.png)

| Page ou menu | Chemin d'accès | Éléments (boutons, onglets, réglages) | Manuel qui le couvre |
|---|---|---|---|
| Barre du haut | toutes les pages, sauf la connexion et les pages plein écran (« Artifacts », passages, canevas d'agent) | logo, icône de maison (« Accueil »), « Base de connaissances », « Discussion », « Recherche », « Agent », « Mémoire », « Gestion des fichiers » | [00](00-notions-fondamentales.md) (visite) |
| Liens externes de l'en-tête | barre du haut, à droite | icône Discord (serveur de discussion du projet), icône GitHub (dépôt `infiniflow/ragflow`), icône « ? » (guide officiel `ragflow.io/docs`) | [00](00-notions-fondamentales.md) (visite) |
| Menu de langue | barre du haut, « English » ou « Français » | 18 langues (English, 简体中文, 繁體中文, Indonesia, 日本語, Español, Tiếng Việt, Русский, Português (Brasil), Deutsch, Français, Italiano, Български, العربية, Türkçe, 한국어, Azərbaycan, Oʻzbek) ; choix mémorisé par le navigateur | [02](02-prise-en-main.md) |
| Thème | barre du haut, icône de lune ; aussi soleil et lune en bas du menu du compte | bascule thème sombre et clair | [00](00-notions-fondamentales.md) (visite) |
| Avatar du compte | barre du haut, pastille aux initiales | ouvre le menu du compte (voir [Menu du compte](#menu-du-compte)) | [00](00-notions-fondamentales.md) (visite), [13](13-exploitation.md) |
| Accueil | icône de maison | « Bienvenue sur RAGFlow » ; section « Base de connaissances » (cartes des bases : nom, nombre de fichiers, date ; « Voir tout ») ; section à onglets « Discussion », « Recherche », « Agent », « Mémoire » (cartes des objets récents, « Voir tout ») | [00](00-notions-fondamentales.md), [02](02-prise-en-main.md) |
| Page de connexion | `http://127.0.0.1:8088/login`, avant connexion | en anglais : « Email », « Password », « Remember me », « Sign in », lien « Sign up » ; formulaire « Create an account » : « Email », « Nickname », « Password », « Continue », « Sign in » | [01](01-installation.md) (inscription), [02](02-prise-en-main.md) (connexion) |

## Base de connaissances

![Liste des bases de connaissances](img/carte/03-bases-de-connaissances.png)

![Fenêtre de création d'une base](img/carte/04-base-creation.png)

![Fichiers d'une base](img/carte/05-base-fichiers.png)

![Passages d'un document](img/carte/06-base-passages.png)

![Test de récupération](img/carte/07-base-test-de-recuperation.png)

![Journaux](img/carte/08-base-journaux.png)

![Configuration d'une base](img/carte/09-base-configuration.png)

![Artifacts](img/carte/10-base-artifacts.png)

![Types d'artefacts](img/carte/11-base-artifacts-types.png)

| Page ou menu | Chemin d'accès | Éléments (boutons, onglets, réglages) | Manuel qui le couvre |
|---|---|---|---|
| Liste des bases | « Base de connaissances » | filtre (entonnoir), « Rechercher », « Créer une base de connaissances », cartes des bases avec menu « … », pagination « 50 / Page » | [02](02-prise-en-main.md), [03](03-datasets-et-decoupage.md) |
| Fenêtre « Créer une base de connaissances » | liste des bases, « Créer une base de connaissances » | « Nom », « Modèle d'embedding » (`bge-m3`), gabarit de découpage (« General (built in) »), « Enregistrer », « Close » | [02](02-prise-en-main.md) |
| Onglet « Fichiers » | clic sur une base | en-tête de la base (nom, nombre de fichiers, taille, date) ; bandeau « Veuillez attendre la fin de l'analyse… » ; filtre, « Rechercher », « Ajouter un fichier » (« Téléverser un fichier », « Créer un fichier vide ») ; tableau « Nom », « Date de téléversement », « Activé », « Nombre de segments », « Métadonnées », « Analyser » (gabarit, lancement, état), « Action » (renommer, aperçu, télécharger, supprimer) ; cases à cocher et action groupée ; « Cancel parsing tasks » pendant l'analyse | [02](02-prise-en-main.md), [03](03-datasets-et-decoupage.md) |
| Fenêtre « Téléverser un fichier » | « Ajouter un fichier », « Téléverser un fichier » | « Analyser à la création », onglets « Fichiers » et « Dossier », zone de dépôt, liste des fichiers choisis, « Enregistrer » | [02](02-prise-en-main.md) |
| Passages d'un document (« Résultat du segment ») | clic sur un nom de fichier | « Retour », « Aperçu », « Artifact », « Texte complet » et « Ellipse », filtre, « Recherche », « + » (ajouter un passage), « Tout sélectionner », un bloc par passage avec case à cocher et interrupteur d'activation | [02](02-prise-en-main.md) (lecture), [04](04-deepdoc.md) (correction) |
| Onglet « Test de récupération » | base, menu de gauche | « Seuil de similarité », « Poids de similarité par mots-clés » (full-text 0,70, vector 0,30), « Modèle de réordonnancement », « Recherche inter-langues », « Métadonnées », « Rerank candidates », « Top N », zone de question, « Test », « Résultats » | [05](05-assistants-et-citations.md) |
| Onglet « Journaux » | base, menu de gauche | compteurs « Fichiers totaux », « Téléchargement », « Succès », « Échec », « Traitement » ; boutons « Fichier », « Base de connaissances », « Data source » ; tableau « ID », « Nom du fichier », « Source », « Pipeline d'ingestion », « Date de début », « Tâche », « Statut », « Opérations » (aperçu) | [03](03-datasets-et-decoupage.md) |
| Onglet « Configuration » | base, menu de gauche | « Informations de base » : « Nom », « Langue », « Avatar », « Description », « Autorisations » (« Moi uniquement »), « Modèle d'embedding », « Rang de page » ; « Mode d'analyse » (gabarit intégré ou pipeline) avec onglets « Parser », « General Chunker », « Extractor », « Indexer » ; « Enable vision enhancement » ; réglages par format (DOC, DOCX, Email, HTML, Image avec « OCR » DeepDoc ou « External OCR model », Markdown, PDF avec « Détecter la mise en page multi-colonnes », « Supprimer la table des matières d'origine », « Supprimer en-tête et pied de page », « Analyseur PDF », « Plages de pages », Tableur, « Texte & Code ») ; « Source de données », « Lier une source de données » ; « Annuler », « Enregistrer », « Introduction au pipeline intégré » | [03](03-datasets-et-decoupage.md), [04](04-deepdoc.md), [09](09-sources-externes.md) (source liée) |
| Onglet « Artifacts » | base, menu de gauche (page plein écran) | « Retour », liste des types « Wiki », « Tree/PageIndex », « Graph », « Mind map », « Timeline » ; message « No wiki yet » tant que rien n'est compilé | [07](07-knowledge-compilation.md) |

## Discussion

![Liste des assistants](img/carte/12-discussions.png)

![Fenêtre de création d'un assistant](img/carte/13-discussion-creation.png)

![Page d'un assistant](img/carte/14-discussion-assistant.png)

![Conversation citée](img/carte/15-discussion-conversation.png)

![Paramètres du chat](img/carte/16-discussion-parametres.png)

![Paramètres du modèle dépliés](img/carte/16-discussion-parametres-detail.png)

| Page ou menu | Chemin d'accès | Éléments (boutons, onglets, réglages) | Manuel qui le couvre |
|---|---|---|---|
| Liste des assistants (« Applications de chat ») | « Discussion » | filtre, « Rechercher », « Créer un chat », cartes avec menu « … », pagination | [02](02-prise-en-main.md) |
| Fenêtre « Créer un chat » | « Créer un chat » | « Nom », « Enregistrer », « Close » | [02](02-prise-en-main.md) |
| Page d'un assistant | clic sur une carte | nom de l'assistant, icône d'avion en papier (rôle à décrire dans le manuel 05), icône de repli du panneau ; « Conversations » avec compteur, « + » (nouvelle conversation), icône de suppression groupée, « Rechercher », liste des conversations (menu « … ») ; « Plusieurs modèles » ; zone « Saisissez votre message ici... », « Attach file », sélecteur « Naive » ou « Agentic », micro, « Send message » ; icône d'engrenage (paramètres) | [02](02-prise-en-main.md), [05](05-assistants-et-citations.md), [06](06-agentic-rag.md), [10](10-api-et-sdk.md) (partage) |
| Réponse dans une conversation | conversation ouverte | renvois « [1] » (survol : extrait), ligne « N tokens (… input, … output) · durée », vignette du document cité ; actions copier, régénérer, supprimer, lire à voix haute, pouce haut et bas | [02](02-prise-en-main.md), [05](05-assistants-et-citations.md) |
| Panneau « Paramètres du chat » | icône d'engrenage | « Télécharger » (avatar), nom et description (crayon), « Modèle », « Paramètres du modèle », « Message d'accueil », « Bases de connaissances », « Paramètres avancés », « Annuler », « Enregistrer » | [02](02-prise-en-main.md), [05](05-assistants-et-citations.md) |
| « Paramètres du modèle » | panneau, dépliant | « Liberté » (« Improviser », « Précis », « Équilibre », « Personnalisé »), « Température », « Top P », « Pénalité de présence », « Pénalité de fréquence », « Nombre max de tokens » (chacun avec interrupteur et curseur), « Thinking » (« System default », « Enabled », « Disabled ») | [05](05-assistants-et-citations.md) |
| « Paramètres avancés » | panneau, dépliant | « Afficher la citation », « Texte en parole », « Web search provider », « Métadonnées », mode « Naive » ou « Agentic » | [05](05-assistants-et-citations.md), [06](06-agentic-rag.md) |

## Recherche

![Liste des recherches](img/carte/17-recherche.png)

![Fenêtre de création d'une recherche](img/carte/18-recherche-creation.png)

| Page ou menu | Chemin d'accès | Éléments (boutons, onglets, réglages) | Manuel qui le couvre |
|---|---|---|---|
| Liste des applications de recherche | « Recherche » | « Aucune recherche créée pour le moment », « + » (création) | 15 Applications de recherche (prévu) |
| Fenêtre « Créer une recherche » | « + » | « Nom », « Enregistrer », « Close » | 15 Applications de recherche (prévu) |

## Agent

![Agents, onglet Workflow](img/carte/19-agents-workflow.png)

![Agents, onglet Ingestion pipeline](img/carte/20-agents-ingestion-pipeline.png)

![Agents, onglet Compilation operator](img/carte/21-agents-compilation-operator.png)

![Menu de création d'un agent](img/carte/22-agents-menu-creation.png)

![Gabarits d'agents](img/carte/23-agents-gabarits.png)

![Canevas d'un agent](img/carte/24-agent-canevas.png)

| Page ou menu | Chemin d'accès | Éléments (boutons, onglets, réglages) | Manuel qui le couvre |
|---|---|---|---|
| Onglet « Workflow » | « Agent » | filtre, « Rechercher », « + », icône de réseau, menu « … », cartes d'agents (« Dernière sauvegarde à ») | [08](08-agents.md) |
| Onglet « Ingestion pipeline » | « Agent », « Ingestion pipeline » | pipelines créés (ici « Essai-KC-mind_map-1835 », « Publié le ») ; « Built-in pipelines » : General, Q&A, Manual, Table, Paper, Book, Laws, Presentation, Picture, One, Audio, Email | [03](03-datasets-et-decoupage.md), [07](07-knowledge-compilation.md) |
| Onglet « Compilation operator » | « Agent », « Compilation operator » | opérateurs de compilation (ici « Essai-KC-mind_map-1835 », type « Mindmap ») ; icône de formes (création) | [07](07-knowledge-compilation.md) |
| Menu de création | « + » | « Créer depuis un blanc », « Créer depuis un modèle », « Importer un fichier JSON » | [08](08-agents.md) |
| Gabarits d'agents | « Créer depuis un modèle » | catégories « Recommandé », « Agent », « Support client », « Marketing », « Application grand public », « Autre » ; cartes (par exemple « Your starter dataset chatbot », « Deep research ») avec « Utiliser » | [08](08-agents.md) |
| Canevas d'un agent | clic sur une carte d'agent | « Save draft », « Exécuter », « Lancer », « Publier », « Checklist », « Gestion » ; nœuds (« Commencer », agent, « Retrieval »), notes, « Zoom In », « Zoom Out », « Fit View », « Toggle Interactivity » | [08](08-agents.md) |

## Mémoire

![Liste des mémoires](img/carte/25-memoire.png)

![Fenêtre de création d'une mémoire](img/carte/26-memoire-creation.png)

| Page ou menu | Chemin d'accès | Éléments (boutons, onglets, réglages) | Manuel qui le couvre |
|---|---|---|---|
| Liste des mémoires | « Mémoire » | « Aucune mémoire créée pour le moment », « + » (création) | [08](08-agents.md) (mémoire des agents, prévu) |
| Fenêtre « Créer une mémoire » | « + » | « Nom », « Type de mémoire » (« brut »), « Modèle d'embedding », « LLM », « Annuler », « Confirmer » | [08](08-agents.md) (mémoire des agents, prévu) |

## Gestion des fichiers

![Gestion des fichiers](img/carte/27-gestion-des-fichiers.png)

| Page ou menu | Chemin d'accès | Éléments (boutons, onglets, réglages) | Manuel qui le couvre |
|---|---|---|---|
| Gestion des fichiers | « Gestion des fichiers » | « Rechercher », « Ajouter un fichier », tableau « Nom », « Date de téléversement », « Taille », « Base de connaissances », « Action » ; dossier `.knowledgebase` (fichiers des bases) | [03](03-datasets-et-decoupage.md) (prévu) |

## Menu du compte

![Fournisseurs de modèles](img/carte/28-compte-fournisseurs-de-modeles.png)

![Sources de données](img/carte/29-compte-sources-de-donnees.png)

![Canaux de chat](img/carte/30-compte-canaux-de-chat.png)

![Serveurs MCP](img/carte/31-compte-mcp.png)

![Équipe](img/carte/32-compte-equipe.png)

![Profil](img/carte/33-compte-profil.png)

![API](img/carte/34-compte-api.png)

| Page ou menu | Chemin d'accès | Éléments (boutons, onglets, réglages) | Manuel qui le couvre |
|---|---|---|---|
| Menu du compte | avatar | adresse du compte, « Fournisseurs de modèles », « Sources de données », « Canaux de chat », « MCP », « Équipe », « Profil », « API », version « v1.0.0 », bascule soleil et lune, « Déconnexion » | [13](13-exploitation.md) |
| « Fournisseurs de modèles » | avatar, « Fournisseurs de modèles » | « Définir les modèles par défaut » (« Modèle de chat », « Modèle d'embedding », « Modèle Img2txt », « Modèle Speech2txt », « Modèle de rerank », « Modèle TTS », « Decision model ») ; « Modèles disponibles » avec « Rechercher » et une centaine de fournisseurs (point vert : configuré) ; par fournisseur : cartes d'instance (« Clé API », « URL de base », « Models », « Lister les modèles », « … », retirer ou ajouter un modèle, « Enregistrer », corbeille), « Add instance » | [01](01-installation.md) |
| « Sources de données » | avatar, « Sources de données » | « Sources disponibles » avec « Ajouter » : Confluence, Notion, Google Drive, Feishu Wiki, Gmail, Google Cloud Storage, Oracle Storage, S3, R2, Jira, Box, Dropbox, Bitbucket, Azure DevOps, GitLab, GitHub, Moodle, Discord, Xquik, Zendesk, Zotero, WebDAV, Airtable, Asana, IMAP, Dingtalk AI Table, SeaFile, MySQL, PostgreSQL, BigQuery, REST API, RSS, Sitemap, OneDrive, Outlook, Salesforce, Azure Blob Storage, Microsoft Teams, Slack, SharePoint | [09](09-sources-externes.md) |
| « Canaux de chat » | avatar, « Canaux de chat » | « Canaux disponibles » avec « Ajouter » : Discord, DingTalk, Feishu / Lark, QQ Bot, Telegram, WeCom, WhatsApp | [09](09-sources-externes.md) (page décrite, prévu) ; branchement d'un bot : Non couvert, compte en ligne chez un tiers exigé |
| « MCP » (« Serveurs MCP ») | avatar, « MCP » | « Rechercher », « Gestion en masse », « Importer », « Ajouter MCP », « Ajouter maintenant » | [08](08-agents.md) (outils MCP des agents, prévu) |
| « Équipe » | avatar, « Équipe » | espace de travail, « Membres de l'équipe » (« Inviter », tableau « Nom », « Date de mise à jour », « Adresse e-mail », « Rôle », « Action »), « Équipes rejointes » | [13](13-exploitation.md) (prévu) |
| « Profil » | avatar, « Profil » | « Nom d'utilisateur » (« Modifier »), « Avatar » (« Télécharger »), « Fuseau horaire » (« GMT+08:00 Asia/Shanghai » par défaut, « Modifier »), « Adresse e-mail » (non modifiable), « Mot de passe » (« Modifier ») | [13](13-exploitation.md) (prévu) |
| « API » | avatar, « API » | « RAGFlow API », « Clé API » (fenêtre des clés), « Serveur API » avec copie, « Afficher le contenu », documentation de l'API HTTP intégrée, carte « Langfuse » avec « Configuration » | [10](10-api-et-sdk.md) (clé et documentation, prévu) ; Langfuse : Non couvert, demande un serveur Langfuse absent du banc |

## Ce qui n'est pas couvert

| Élément | Raison |
|---|---|
| Branchement d'un canal de chat (Discord, Telegram, WhatsApp…) | exige un compte en ligne chez un tiers, hors du périmètre de la mission |
| Sources de données en ligne (Confluence, Notion, Google Drive, S3…) | même raison ; le connecteur « Sitemap » est essayé dans le manuel [09](09-sources-externes.md) |
| Carte « Langfuse » de la page « API » | demande un serveur Langfuse, absent du banc |

## Dépannage

| Symptôme | Cause probable | Action |
|---|---|---|
| La barre du haut disparaît | page plein écran (« Artifacts », passages, canevas d'agent) | bouton « Retour », ou icône de maison après retour |
| Interface en anglais | langue mémorisée par le navigateur | menu de langue, « Français » ([02](02-prise-en-main.md)) |

## Sources

- Scénario : `outils/ragflow/captures/carte.py` (scénario `carte`), lancé par `outils/communs/captures/lancer.sh`
- Textes et inventaires des pages : `outils/resultats/ragflow/captures/carte/`
- Libellés français : `web/src/locales/fr.ts` au tag v1.0.0 ; liens de l'en-tête : `web/src/layouts/components/header.tsx`
