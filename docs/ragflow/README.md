# RAGFlow — index des manuels

| Version décrite | Date des essais | Machine | Langue de l'interface |
|---|---|---|---|
| RAGFlow v1.0.0 (image `infiniflow/ragflow:v1.0.0`, `ragflow-sdk` 1.0.0) | 9 novembre 2026 | Ryzen 5 9600X, 32 Go de RAM dans WSL2, RTX 4060 Ti 16 Go ; LLM-Service `service-vllm` (vLLM 0.29.0, `gemma4:e4b`, `bge-m3`) | français par le sélecteur de l'en-tête (page de connexion en anglais) |

Première page à lire : [présentation](presentation.md). Plan détaillé : [plan des manuels](plan-des-manuels.md).

## Manuels

| N° | Manuel | Contenu |
|---|---|---|
| 00 | [Notions fondamentales](00-notions-fondamentales.md) | RAG, découpage, recherche hybride, citations ; architecture de RAGFlow 1.0 |
| 01 | [Installation sous Windows et WSL2](01-installation.md) | override sans exposition réseau, compte, modèles, mémoire, désinstallation |
| 02 | [Prise en main](02-prise-en-main.md) | connexion, langue, base de connaissances, passages, conversation citée |
| 03 | [Datasets et découpage](03-datasets-et-decoupage.md) | gabarits comparés sur le corpus |
| 04 | [DeepDoc et correction des passages](04-deepdoc.md) | scan, tableaux, correction manuelle |
| 05 | [Assistants de chat et citations](05-assistants-et-citations.md) | réglages de recherche et effet mesuré |
| 06 | [Agentic RAG](06-agentic-rag.md) | mode agentique contre réponse directe |
| 07 | [Knowledge Compilation](07-knowledge-compilation.md) | opérateur, pipeline avec Compiler, artefacts (graphe, arbre, frise, carte mentale) ; échecs Wiki et PageIndex |
| 08 | [Agents et gabarits](08-agents.md) | agent depuis un gabarit, blocs, essai, publication, import, mémoire, MCP |
| 09 | [Sources externes](09-sources-externes.md) | sources de données, liaison à une base, sitemap refusé, canaux de chat |
| 10 | [API HTTP et SDK Python](10-api-et-sdk.md) | automatisation, défauts du SDK 1.0.0 |
| 11 | [Recettes](11-recettes.md) | cas d'usage de bout en bout |
| 12 | [Qualité et performances](12-qualite-et-performances.md) | banc, réglages, profils matériels |
| 13 | [Exploitation](13-exploitation.md) | sauvegarde, mise à jour, journaux, sécurité |
| 14 | [Dépannage et FAQ](14-depannage.md) | échecs rencontrés et remèdes |
| 15 | [Applications de recherche](15-recherche.md) | page « Recherche » : moteur de recherche sur une base, résumé, carte mentale, intégration |

## Parcours de lecture

| Besoin | Parcours |
|---|---|
| Essayer en une heure | [présentation](presentation.md), [01](01-installation.md), [02](02-prise-en-main.md) |
| Améliorer les réponses | [03](03-datasets-et-decoupage.md), [04](04-deepdoc.md), [05](05-assistants-et-citations.md), [12](12-qualite-et-performances.md) |
| Automatiser | [10](10-api-et-sdk.md), [11](11-recettes.md) |
| Exploiter au quotidien | [13](13-exploitation.md), [14](14-depannage.md) |

## Limites connues

- SDK `ragflow-sdk` 1.0.0 : `Session.ask` sur un assistant répond 404 ; `parse_documents` peut rendre la main avant la fin réelle (manuel [10](10-api-et-sdk.md)).
- Aucun reranker dans le socle : reranking [À tester].
- Mode agentique moins bon que la réponse directe sur le banc (manuel [06](06-agentic-rag.md)).

## Ce qui reste ouvert

| Sujet | État |
|---|---|
| Non traité | mise à jour de version (aucune plus récente que v1.0.0) ; reranking ; second modèle et modèle de moins de 3 milliards de paramètres ; Wiki et PageIndex en échec avec `gemma4:e4b` (manuel [07](07-knowledge-compilation.md)) ; gabarit Picture ; gabarits d'agents qui demandent le web |
| Estimé, non mesuré | profil sans GPU (manuel [12](12-qualite-et-performances.md)) |
| Décisions en attente | montée de vLLM dans LLM-Service ; port 8088 au lieu de 8080 ; création du dépôt distant ; reranker ; ports `0.0.0.0` de services hors mission (voir [rapport](../../RAPPORT-ragflow.md)) |
| Ménage à faire à la main | images Docker gardées en cache (`docker rmi`) ; sauvegarde de test dans `donnees/sauvegardes/` |
| Écarts de version | images annexes à la version du compose (Elasticsearch 8.11.3, Kvrocks 2.16.0, NATS 2.14.2, MinIO d'août 2026) : plus récentes disponibles, non montées sans essai |
