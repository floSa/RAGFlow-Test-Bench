# RAGFlow : fiche technique

Architecture, réglages, API, versions et licences. Le guide d'utilisation est dans [le manuel](README.md).

## Sommaire

- [Architecture](#architecture)
- [Installation : prérequis et commandes](#installation--prérequis-et-commandes)
- [Configuration](#configuration)
- [API / Endpoints](#api--endpoints)
- [Tests](#tests)
- [Licences & composants](#licences--composants)
- [Données du banc](#données-du-banc)
- [Les pièges que ce banc documente](#les-pièges-que-ce-banc-documente)
- [Versions](#versions)
- [Ressources](#ressources)

## Architecture

| Service | Conteneur | Image | Rôle |
|---|---|---|---|
| RAGFlow | `rag-ragflow-server` | `infiniflow/ragflow:v1.0.0` | interface web (nginx), API, administration, ingestion et DeepDoc |
| Moteur documentaire | `rag-ragflow-es01` | `elasticsearch:8.11.3` | index des passages (mots-clés et vecteurs) |
| Base de données | `rag-ragflow-mysql` | `mysql:8.0.40` | comptes, bases, documents, assistants |
| Stockage | `rag-ragflow-minio` | `pgsty/silo:RELEASE.2026-08-06T00-00-00Z` | fichiers téléversés (fork de MinIO) |
| Cache | `rag-ragflow-kvrocks` | `apache/kvrocks:2.16.0` | cache |
| File de tâches | `rag-ragflow-nats` | `nats:2.14.2` | tâches d'analyse |
| Passerelle du service LLM central | `llm-central` (LLM-Service, géré à part, hors de ce dépôt) | `ghcr.io/berriai/litellm:v1.109.0` | point d'entrée unique compatible OpenAI, clé obligatoire, noms fixes `chat`, `embed`, `rerank`, `transcribe` |
| Modèles du service central | `llm-swap` (LLM-Service) | `ghcr.io/mostlygeek/llama-swap:v272-cuda-b12282` | llama-swap devant llama.cpp (`llama-server`, build 12282) sur la carte graphique : `chat` = Qwen3.5-4B Q4_K_M, `embed` = bge-m3 Q8_0, `rerank` = bge-reranker-v2-m3 Q8_0 (GGUF) |
| Transcription du service central | `llm-speaches` (LLM-Service) | `ghcr.io/speaches-ai/speaches:0.8.3-cpu` | `transcribe` = faster-whisper-small, sur le processeur |

Toutes les images sont figées par empreinte `@sha256` (`service/compose.override.yml`).

```mermaid
flowchart LR
  N[Navigateur Windows] -->|127.0.0.1:8088| S[rag-ragflow-server]
  P[Scripts, SDK] -->|127.0.0.1:9380| S
  A[Administration] -->|127.0.0.1:9381| S
  subgraph rag-ragflow
    S --> E[(es01)]
    S --> M[(mysql)]
    S --> O[(minio)]
    S --> K[(kvrocks)]
    S --> Q[(nats)]
  end
  S -->|llm-net, clé| V[llm-central :8080 LiteLLM]
  subgraph LLM-Service, géré à part
    V -->|chat, embed, rerank| W[llm-swap : llama-swap + llama.cpp, GPU]
    V -->|transcribe| X[llm-speaches : faster-whisper, CPU]
  end
```

Réseaux : `rag-ragflow` (interne à la pile), `llm-net` (LLM-Service, externe : RAGFlow y joint `llm-central`), `rag-local` (captures Playwright, externe). L'ancienne pile vLLM (`vllm-central`, `vllm-embed`) et le serveur de voix `rag-speaches` ne sont plus branchés ; leurs mesures restent dans les annexes comme historique daté du 9 au 11 novembre 2026.

## Installation : prérequis et commandes

Prérequis : WSL2 (Ubuntu), Docker et Compose, le service LLM central en marche (LLM-Service, géré dans son propre dépôt ; s'il est arrêté : `~/mes_projets/Projet-IA/LLM-Service/service/scripts/demarrer.sh`, profil carte graphique ; ce dépôt ne l'arrête ni ne le modifie), la clé propre de l'application dans `service/.env` (copie de `service/.env.example`, clé créée par `~/mes_projets/Projet-IA/LLM-Service/service/scripts/cle.sh creer ragflow-test-bench --dans <dépôt>/.env --noms LLM_CENTRAL_URL,LLM_CENTRAL_KEY`, jamais la clé maîtresse de LLM-Service), uv. Vérification : `banc-essai/communs/llm_central_sante.sh --essai`. Les scripts `llm_service*.sh` et `voix.sh` sont historiques (annexe A2). Mesures de la machine : [diagnostic](../banc-essai/resultats/machine/diagnostic-2026-11-09.json).

```bash
service/installer.sh
uv sync --project banc-essai
uv run --project banc-essai python service/configurer.py
uv run --project banc-essai python banc-essai/ragflow/verif_minimale.py
```

| Service | URL | Note |
|---|---|---|
| Interface web | http://127.0.0.1:8088 | identifiants dans `donnees/IDENTIFIANTS-LOCAUX.txt` ; langue : sélecteur de l'en-tête |
| API | http://127.0.0.1:9380/api/v1 | clé d'API `Bearer` |
| Administration | http://127.0.0.1:9381/api/v1/admin | compte `admin@ragflow.io` |
| Santé | http://127.0.0.1:9380/api/v1/system/healthz | sans authentification |

Installation complète, mémoire et désinstallation : [chapitre 02](manuel/02-installer-ragflow.md) et [annexe A4](annexes/A4-exploitation.md).

## Configuration

| Réglage | Valeur | Où |
|---|---|---|
| Mots de passe (Elasticsearch, MySQL, MinIO, Kvrocks, administration) | générés aléatoirement | `donnees/ragflow/ragflow.env` (droits 600, ignoré par git) |
| Port de l'interface | 8088 (8080 déjà occupé sur la machine d'essai) | `SVR_WEB_HTTP_PORT` |
| Mémoire d'Elasticsearch | 4 Gio (`MEM_LIMIT`, 8 Go dans le compose officiel) | `ragflow.env` |
| Fuseau horaire | `Europe/Paris` | `ragflow.env` |
| Adresses privées | `ALLOW_ANY_HOST=0` (défaut) | `ragflow.env` |

Écarts au compose officiel (fichier `service/compose.override.yml`) : ports sur `127.0.0.1` ou retirés, conteneurs `rag-ragflow-*`, images figées, volumes liés à `donnees/ragflow/`, réseaux `llm-net` et `rag-local`, réglages hors du `docker/.env` suivi.

Service LLM central (LLM-Service, dépôt séparé, géré à part) : un seul point d'entrée LiteLLM, `http://llm-central:8080/v1` depuis les conteneurs du réseau `llm-net` (`http://127.0.0.1:8080/v1` depuis l'hôte), clé obligatoire (`LLM_CENTRAL_KEY` dans `service/.env`, jamais commitée). Modèles fixes :

| Nom | Modèle | Usage |
|---|---|---|
| `chat` | Qwen3.5-4B, vision, réflexion activée par défaut | réponses, agents, synthèses (contexte 16 384 jetons par requête) |
| `embed` | bge-m3 (GGUF Q8_0), 1024 dimensions | recherche par le sens |
| `rerank` | bge-reranker-v2-m3 | reclassement, scores bruts non bornés |
| `transcribe` | faster-whisper-small | `/v1/audio/transcriptions` |

Dans RAGFlow : fournisseur `OpenAI-API-Compatible` pour les quatre usages (voir la [bascule](annexes/A7-bascule-vers-le-service-llm-central.md)). Les résultats mesurés avec l'ancienne pile (`gemma4:e4b` sur vLLM) restent dans `banc-essai/resultats/` comme preuves historiques.

### Bascule vers le service LLM central (dans l'interface de RAGFlow)

Procédure complète et justification : [annexe A7](annexes/A7-bascule-vers-le-service-llm-central.md). Résumé :

1. Menu du compte › « Fournisseurs de modèles » › ajouter `OpenAI-API-Compatible` : nom d'instance `llm-central`, URL `http://llm-central:8080/v1`, clé = `LLM_CENTRAL_KEY` ; modèles `chat` (type chat, 16 384), `embed` (embedding), `rerank` (rerank), `transcribe` (speech2text).
2. Modèles par défaut du compte : chat `chat`, embedding `embed`, rerank `rerank`, transcription `transcribe`.
3. Recréer les bases de connaissances après avoir déclaré l'instance (une base retient l'identifiant interne de son modèle d'embedding) : `bge-m3` est maintenant en Q8_0 GGUF au lieu de bf16 ; le jeu de démonstration se recrée par `banc-essai/ragflow/demo.py`, `essai_agent.py` et `essai_compilation.py`.
4. Réflexion de `chat` : activée par défaut, elle consomme des jetons et de la latence ; RAGFlow n'a pas de champ de paramètres supplémentaires par instance (voir A7).

## API / Endpoints

| Besoin | Appel |
|---|---|
| Santé | `GET /api/v1/system/healthz` |
| Bases | `POST /api/v1/datasets`, `POST /api/v1/datasets/{id}/documents`, `POST /api/v1/datasets/{id}/chunks` |
| Recherche seule | `POST /api/v1/retrieval` |
| Assistants et questions | `POST /api/v1/chats`, `POST /api/v1/chat/completions` |
| Agents | `POST /api/v1/agents`, `POST /api/v1/agents/chat/completions` |
| Modèles | `POST /api/v1/providers/{fournisseur}/instances`, `PATCH /api/v1/models/default` |
| Administration | `POST /api/v1/admin/login`, `GET /api/v1/admin/users` (port 9381) |

SDK `ragflow-sdk` 1.0.0 (Python 3.13) : deux défauts et leurs contournements dans l'[annexe A3](annexes/A3-automatiser-par-l-api.md).

## Tests

```bash
uv run --project banc-essai python banc-essai/ragflow/verif_minimale.py
banc-essai/exemples/lancer.sh
uv run --project banc-essai python banc-essai/ragflow/banc.py --etiquette defaut --reindexer
python3 banc-essai/communs/verifier_docs.py
```

Sorties obtenues le 12 novembre 2026 avec le service LLM central : vérification minimale, 4 passages et réponse citée en 14,1 s ([journal](../banc-essai/resultats/ragflow/installation-2026-11-12-verif.log)) ; six exemples en code 0 ([sorties vérifiées](../banc-essai/exemples/sorties_verifiees.txt)) ; banc 33/34 par défaut, 34/34 avec `--reranker` ([résultat](../banc-essai/resultats/ragflow/banc-2026-11-12-defaut.md), [avec reranker](../banc-essai/resultats/ragflow/banc-2026-11-12-defaut-reranker.md)) ; documentation à 0 point ([sortie du vérificateur](../banc-essai/resultats/ragflow/verifier-docs-2026-11-09.txt)).

## Licences & composants

| Composant | Rôle | Licence |
|---|---|---|
| RAGFlow | application testée | Apache License 2.0 |
| `ragflow-sdk` | SDK Python | Apache License 2.0 |
| Elasticsearch 8.11.3 | moteur documentaire | Elastic License 2.0 ou SSPL |
| MySQL 8.0.40 | base de données | GPL v2 |
| `pgsty/silo` (fork de MinIO) | stockage | GNU AGPL v3 |
| Apache Kvrocks | cache | Apache License 2.0 |
| NATS | file de tâches | Apache License 2.0 |
| LiteLLM | passerelle du service LLM central (géré à part) | MIT (noyau) |
| llama-swap, llama.cpp | service des modèles GGUF (géré à part) | MIT |
| Qwen3.5-4B | modèle de réponse `chat` | voir la fiche du modèle |
| bge-m3, bge-reranker-v2-m3 | modèles `embed` et `rerank` | voir la fiche de chaque modèle |
| Speaches, faster-whisper-small | transcription `transcribe` | MIT |
| Gemma 4 E4B (historique) | modèle de réponse des essais du 9 au 11 novembre | conditions de Google, voir la fiche du modèle |
| Playwright | captures d'écran | Apache License 2.0 |
| **Ce projet** | manuels, scripts, corpus, banc | MIT — Copyright (c) 2026 floSa |

## Données du banc

Entreprise fictive Vélanor (vélos électriques), 9 documents, 1 Mo, empreintes dans `banc-essai/corpus/MANIFEST.json` : rapport annuel PDF de 10 pages avec tableaux, contrat PDF scanné, audit en anglais, procédure DOCX, présentation PPTX, classeur XLSX, FAQ HTML, compte rendu Markdown, message vocal MP3. 38 questions de référence (`banc-essai/corpus/questions.json`) : faits simples, tableaux, scan, anglais, multi-documents, audio et 4 pièges sans réponse.

## Les pièges que ce banc documente

- Le compose officiel publie bases de données et stockage sur toutes les interfaces, avec des mots de passe connus.
- Un compte créé par l'API avec un mot de passe en clair ne peut pas se connecter dans le navigateur (le serveur compare `base64(mot de passe)`).
- `Session.ask` du SDK 1.0.0 répond 404 pour un assistant ; `parse_documents` peut rendre la main avant la fin.
- `reference.chunks` liste tous les passages fournis au modèle, pas seulement ceux qu'il cite (`[ID:n]`).
- À 3 072 jetons de contexte, 12 réponses sur 38 deviennent des messages d'erreur, avec un code d'API 0 ; 4 096 suffit.
- Un site interne est refusé par la synchronisation sitemap (protection contre les adresses privées).
- L'interface reste en anglais tant que le sélecteur de langue n'est pas utilisé.
- Une base retient l'identifiant interne de son modèle d'embedding : supprimer puis recréer l'instance de même nom laisse la base liée à un modèle disparu.
- « Lister les modèles » laisse « Tokens maximum » à 0 pour les noms fixes du service central : à régler à la main (16 384 pour `chat`).
- Un reranker nommé exactement `BAAI/bge-reranker-v2-m3` est pris pour un ancien reranker intégré ; le nom `rerank` évite le piège.
- Avec un modèle qui réfléchit (`chat`), la réponse d'un agent montre ce raisonnement entre balises `<think>`.

## Versions

| Composant | Version |
|---|---|
| RAGFlow, `ragflow-sdk` | v1.0.0 |
| Elasticsearch | 8.11.3 |
| MySQL | 8.0.40 |
| Kvrocks | 2.16.0 |
| NATS | 2.14.2 |
| MinIO (`pgsty/silo`) | RELEASE.2026-08-06 |
| Playwright (captures) | 1.64.1 |
| LiteLLM (service central, géré à part) | v1.109.0 |
| llama-swap / llama.cpp (service central) | v272 / build 12282 (`llama-server` 0.9.0-dev) |
| Speaches (service central) | 0.8.3 (CPU) |
| Modèles du service central | Qwen3.5-4B Q4_K_M, bge-m3 Q8_0, bge-reranker-v2-m3 Q8_0, faster-whisper-small |

Relevé : `banc-essai/resultats/ragflow/versions-llm-central-2026-11-12.txt` (images figées par empreinte dans LLM-Service).

## Ressources

- RAGFlow : https://github.com/infiniflow/ragflow, documentation https://ragflow.io/docs/
- Bilan de la mission : [documentations/rapport.md](rapport.md) ; avancement : [documentations/journal.md](journal.md)
- Banc précédent : https://github.com/floSa/Open-Notebook-Test-Bench
