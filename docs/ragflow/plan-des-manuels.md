# Plan des manuels RAGFlow

Plan établi au cadrage le 9 novembre 2026 à partir du plan type du kit et des thèmes de la fiche RAGFlow. Les écarts constatés en cours de rédaction sont notés en fin de page.

## Sommaire

- [Les manuels en une phrase](#les-manuels-en-une-phrase)
- [Contenu détaillé](#contenu-detaille)
- [Écarts au plan](#ecarts-au-plan)

## Les manuels en une phrase

| N° | Manuel | En une phrase |
|---|---|---|
| 00 | [Notions fondamentales](00-notions-fondamentales.md) | Ce qu'est un RAG, et comment RAGFlow l'organise en services. |
| 01 | [Installation sous Windows et WSL2](01-installation.md) | Installer RAGFlow branché sur LLM-Service, sans rien exposer au réseau. |
| 02 | [Prise en main](02-prise-en-main.md) | Du premier document importé à la première réponse citée. |
| 03 | [Datasets et découpage](03-datasets-et-decoupage.md) | Choisir un gabarit de découpage et mesurer son effet. |
| 04 | [DeepDoc et correction des passages](04-deepdoc.md) | Lire les scans, les tableaux et la mise en page, puis corriger les passages. |
| 05 | [Assistants de chat et citations](05-assistants-et-citations.md) | Régler la recherche et vérifier les citations. |
| 06 | [Agentic RAG](06-agentic-rag.md) | Comparer la réponse directe et le mode agentique. |
| 07 | [Knowledge Compilation](07-knowledge-compilation.md) | Ce que produisent graphes, arbres, cartes mentales, frises et wikis. |
| 08 | [Agents et gabarits](08-agents.md) | Construire un flux d'agent complet à partir d'un gabarit. |
| 09 | [Sources externes](09-sources-externes.md) | Ingestion par sitemap et synchronisation de sources. |
| 10 | [API HTTP et SDK Python](10-api-et-sdk.md) | Automatiser datasets, ingestion et questions. |
| 11 | [Recettes](11-recettes.md) | Cas d'usage complets, de bout en bout. |
| 12 | [Qualité et performances](12-qualite-et-performances.md) | Résultats du banc, réglages utiles, profils matériels. |
| 13 | [Exploitation](13-exploitation.md) | Sauvegarde, mise à jour, journaux, sécurité, comptes. |
| 14 | [Dépannage et FAQ](14-depannage.md) | Les échecs réellement rencontrés et leur remède. |

## Contenu détaillé

### 00. Notions fondamentales

RAG, embeddings, découpage, recherche hybride (mots-clés et vecteurs), reranking, citations ; architecture de RAGFlow 1.0 (serveur Go, ingestion, Elasticsearch, MySQL, MinIO, Kvrocks, NATS) avec schéma des services et des ports ; place de LLM-Service.

### 01. Installation sous Windows et WSL2

Prérequis mesurés ; relecture du compose ; override (ports sur `127.0.0.1`, secrets générés, données dans `donnees/ragflow/`) ; branchement à LLM-Service ; mémoire consommée par service au repos et en indexation ; premier démarrage ; compte local ; mise à jour ; désinstallation complète.

### 02. Prise en main

Connexion, déclaration des modèles (« Model providers »), création d'un dataset, import, analyse, création d'un assistant, première question, lecture des citations.

### 03. Datasets et découpage

Gabarits disponibles en 1.0 (General, Q&A, Manual, Table, Paper, Book, Laws, Presentation, Picture, One, Audio, Email) ; comparaison sur le corpus (au moins General, Table, Paper, Presentation) : nombre de passages, effet sur le banc.

### 04. DeepDoc et correction des passages

OCR du PDF scanné, structure des tableaux, mise en page ; temps d'analyse par page sur CPU ; visualisation et correction manuelle d'un passage.

### 05. Assistants de chat et citations

Réglages de recherche : top-n, seuil de similarité, poids mots-clés et vecteurs, reranker (absent du socle), message de réponse vide ; effet mesuré sur le banc.

### 06. Agentic RAG

Mode agentique (champ `reasoning`) comparé à la réponse directe : qualité et latence.

### 07. Knowledge Compilation

Composant Compiler d'un pipeline d'ingestion : ce que chaque type d'artefact produit sur un document court, durée observée.

### 08. Agents et gabarits

Un gabarit d'agent, un flux complet, exécution par l'interface et par l'API.

### 09. Sources externes

Ingestion d'un site local de test par sitemap ; synchronisation de sources ; limites (adresses privées refusées).

### 10. API HTTP et SDK Python

Clé d'API, datasets, téléversement, analyse, assistants, questions ; défauts relevés du SDK 1.0.0 et contournements ; exemples exécutés (`exemples/ragflow/`).

### 11. Recettes

Assistant documentaire d'entreprise sur le corpus ; automatisation d'une ingestion quotidienne par l'API.

### 12. Qualité et performances

Banc (38 questions) : réglages par défaut, réglages recommandés, mode agentique ; latences, RAM, VRAM ; profils matériels sans et avec GPU ; taille de contexte.

### 13. Exploitation

Sauvegarde et restauration des volumes, mise à jour (migration irréversible depuis 0.27), journaux, sécurité (ports, secrets, compte d'administration), comptes et équipes, API d'administration.

### 14. Dépannage et FAQ

Tableau Symptôme | Cause probable | Action, tiré des journaux d'essai.

## Écarts au plan

Aucun pour l'instant.
